#!/usr/bin/env python3
"""Harvest real cat-behaviour literature from PubMed E-utilities and write RIS.

No fabricated data: every record comes from an efetch MEDLINE response.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
HERE = os.path.dirname(os.path.abspath(__file__))
RIS_PATH = os.path.join(HERE, "cat-behavior.ris")
PROVENANCE_PATH = os.path.join(HERE, "cat-behavior.provenance.json")
# Focus: cat STRESS behaviour + AGGRESSION toward humans. (query, quota), relevance-sorted.
BUCKETS = [
    # 应激行为 / stress response, fear, anxiety, cortisol
    ('"Cats"[Mesh] AND (stress[tiab] OR "stress response"[tiab] OR stressor[tiab] '
     'OR cortisol[tiab] OR fear[tiab] OR anxiety[tiab]) '
     'AND ("Behavior, Animal"[Mesh] OR behavi*[tiab])', 25),
    # 应激 in veterinary / handling / restraint context
    ('"Cats"[Mesh] AND (stress[tiab] OR fear[tiab]) '
     'AND (veterinary[tiab] OR clinic[tiab] OR handling[tiab] OR restraint[tiab])', 12),
    # 攻击人 / aggression directed at humans
    ('"Cats"[Mesh] AND aggress*[tiab] AND (human[tiab] OR owner[tiab] OR people[tiab] '
     'OR person[tiab] OR caretaker[tiab] OR handler[tiab] OR bite[tiab])', 25),
    # 攻击行为总论 / agonistic behaviour
    ('"Cats"[Mesh] AND (aggress*[tiab] OR "agonistic behavior"[tiab])', 12),
]
TOOL = "cat-behaviour-library"
EMAIL = os.environ.get("NCBI_EMAIL", "you@example.com")


def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # transient 429 / network
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def esearch(term, retmax):
    params = urllib.parse.urlencode({
        "db": "pubmed", "term": term, "retmax": retmax,
        "sort": "relevance", "retmode": "json", "tool": TOOL, "email": EMAIL,
    })
    data = json.loads(fetch(f"{EUTILS}/esearch.fcgi?{params}"))
    return data["esearchresult"]["idlist"]


def collect_pmids():
    """Union PMIDs across buckets, preserving first-seen relevance order."""
    seen, order = set(), []
    for term, quota in BUCKETS:
        ids = esearch(term, quota)
        print(f"  bucket quota={quota:>3} got={len(ids):>3} :: {term[:55]}...", file=sys.stderr)
        for pid in ids:
            if pid not in seen:
                seen.add(pid)
                order.append(pid)
        time.sleep(0.4)
    return order


def efetch(pmids):
    params = urllib.parse.urlencode({
        "db": "pubmed", "id": ",".join(pmids), "rettype": "medline",
        "retmode": "text", "tool": TOOL, "email": EMAIL,
    })
    return fetch(f"{EUTILS}/efetch.fcgi?{params}")


def parse_medline(text):
    """Split MEDLINE text into records -> list of dict(tag -> [values])."""
    records = []
    cur = {}
    last_tag = None
    for line in text.splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([A-Z]{2,4})\s*-\s?(.*)$", line)
        if m:
            tag, val = m.group(1), m.group(2)
            cur.setdefault(tag, []).append(val)
            last_tag = tag
        elif line.startswith("      ") and last_tag:  # continuation
            cur[last_tag][-1] += " " + line.strip()
        if line.strip() == "" :
            pass
        # record separator: PMID starts a new record
    # MEDLINE separates records by blank lines; re-parse by PMID blocks instead
    return records


def parse_medline_blocks(text):
    blocks = re.split(r"\n\n+", text.strip())
    out = []
    for blk in blocks:
        rec = {}
        last = None
        for line in blk.splitlines():
            m = re.match(r"^([A-Z]{2,4})\s*-\s?(.*)$", line)
            if m:
                tag, val = m.group(1), m.group(2)
                rec.setdefault(tag, []).append(val)
                last = tag
            elif line.startswith(" ") and last:
                rec[last][-1] += " " + line.strip()
        if rec.get("PMID"):
            out.append(rec)
    return out


def to_ris(rec):
    L = []
    pubtypes = rec.get("PT", [])
    ty = "JOUR"
    if any("Review" in p for p in pubtypes):
        ty = "JOUR"  # keep JOUR; Zotero handles review via notes
    L.append(("TY", ty))
    for au in rec.get("FAU", rec.get("AU", [])):
        L.append(("AU", au))
    if rec.get("TI"):
        L.append(("TI", " ".join(rec["TI"]).rstrip(".")))
    if rec.get("JT"):
        L.append(("JO", rec["JT"][0]))
    elif rec.get("TA"):
        L.append(("JO", rec["TA"][0]))
    # year
    dp = (rec.get("DP") or [""])[0]
    ym = re.match(r"(\d{4})", dp)
    if ym:
        L.append(("PY", ym.group(1)))
    if rec.get("VI"):
        L.append(("VL", rec["VI"][0]))
    if rec.get("IP"):
        L.append(("IS", rec["IP"][0]))
    if rec.get("PG"):
        L.append(("SP", rec["PG"][0]))
    if rec.get("AB"):
        L.append(("AB", " ".join(rec["AB"])))
    for mh in rec.get("MH", []):
        L.append(("KW", mh))
    # DOI / IDs
    doi = None
    for aid in rec.get("AID", []) + rec.get("LID", []):
        dm = re.match(r"(10\.\S+?)\s*\[doi\]", aid)
        if dm:
            doi = dm.group(1)
            break
    if doi:
        L.append(("DO", doi))
    pmid = rec["PMID"][0]
    L.append(("UR", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"))
    L.append(("AN", f"PMID:{pmid}"))
    if rec.get("ISSN"):
        L.append(("SN", rec["ISSN"][0]))
    L.append(("ER", ""))
    return "\r\n".join(f"{t}  - {v}" if v != "" else f"{t}  -" for t, v in L)


def main():
    pmids = collect_pmids()
    print(f"union of buckets = {len(pmids)} unique PMIDs", file=sys.stderr)
    time.sleep(0.4)
    medline = efetch(pmids)
    recs = parse_medline_blocks(medline)
    print(f"parsed {len(recs)} MEDLINE records", file=sys.stderr)
    ris_blocks = [to_ris(r) for r in recs]
    with open(RIS_PATH, "w", encoding="utf-8") as f:
        f.write("\r\n\r\n".join(ris_blocks) + "\r\n")
    # provenance
    prov = [{
        "pmid": r["PMID"][0],
        "title": " ".join(r.get("TI", [])).rstrip("."),
        "year": (re.match(r"(\d{4})", (r.get("DP") or [""])[0]) or [None]).group(1)
                 if re.match(r"(\d{4})", (r.get("DP") or [""])[0]) else None,
        "journal": (r.get("JT") or r.get("TA") or [None])[0],
    } for r in recs]
    with open(PROVENANCE_PATH, "w", encoding="utf-8") as f:
        json.dump({"queries": [b[0] for b in BUCKETS], "source": "PubMed E-utilities",
                   "focus": "cat stress behaviour + aggression toward humans",
                   "retrieved": time.strftime("%Y-%m-%d"), "count": len(recs),
                   "records": prov}, f, ensure_ascii=False, indent=2)
    print(f"wrote {RIS_PATH} with {len(ris_blocks)} records", file=sys.stderr)


if __name__ == "__main__":
    main()
