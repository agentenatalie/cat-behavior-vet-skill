#!/usr/bin/env python3
"""Fetch open-access full-text PDFs for the cat-behaviour corpus and build a
PaperQA2 manifest. Sources: Unpaywall + Europe PMC / PMC OA. Legal OA only.

Reads ../literature/cat-behavior.ris, writes PDFs + manifest.csv into ../papers/.
Re-runnable: skips already-downloaded files.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RIS = os.path.join(ROOT, "literature", "cat-behavior.ris")
PAPERS = os.path.join(ROOT, "papers")
MANIFEST = os.path.join(PAPERS, "manifest.csv")
EMAIL = os.environ.get("UNPAYWALL_EMAIL", "you@example.com")
UA = "cat-behaviour-veterinary-behaviorist-skill/1.0 (mailto:%s)" % EMAIL
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"


def get(url, accept=None, binary=False, tries=3, timeout=40):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, **({"Accept": accept} if accept else {})})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except Exception as e:
            last = e
            time.sleep(1.2 * (i + 1))
    raise last


def parse_ris(path):
    recs, cur, tag = [], {}, None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\r\n")
            m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line)
            if m:
                tag, val = m.group(1), m.group(2)
                cur.setdefault(tag, []).append(val)
                if tag == "ER":
                    recs.append(cur)
                    cur = {}
    out = []
    for r in recs:
        pmid = None
        for an in r.get("AN", []):
            mm = re.search(r"PMID:(\d+)", an)
            if mm:
                pmid = mm.group(1)
        out.append({
            "pmid": pmid,
            "doi": (r.get("DO") or [None])[0],
            "title": (r.get("TI") or [""])[0],
            "year": (r.get("PY") or [""])[0],
            "journal": (r.get("JO") or [""])[0],
            "authors": r.get("AU", []),
            "abstract": " ".join(r.get("AB", [])),
        })
    return out


def strip_xml(xml):
    body = re.search(r"<body[\s>].*?</body>", xml, re.S)
    text = body.group(0) if body else xml
    text = re.sub(r"<(ref-list|back|fig|table-wrap)[\s>].*?</\1>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def try_epmc_fulltext(pmid, doi):
    """Return (pmcid, fulltext_plaintext) for OA articles, else None."""
    q = f"DOI:{doi}" if doi else f"EXT_ID:{pmid} AND SRC:MED"
    try:
        d = json.loads(get(f"{EPMC}/search?query={urllib.parse.quote(q)}&format=json&resultType=core&pageSize=1"))
    except Exception:
        return None
    res = (d.get("resultList") or {}).get("result") or []
    if not res:
        return None
    r0 = res[0]
    pmcid = r0.get("pmcid")
    if r0.get("isOpenAccess") != "Y" or not pmcid:
        return None
    try:
        xml = get(f"{EPMC}/PMC/{pmcid}/fullTextXML")
    except Exception:
        return None
    txt = strip_xml(xml)
    return (pmcid, txt) if len(txt) > 1500 else None


def is_pdf(data):
    return data[:5] == b"%PDF-"


def try_unpaywall(doi):
    if not doi:
        return None
    try:
        d = json.loads(get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={EMAIL}"))
    except Exception:
        return None
    loc = d.get("best_oa_location") or {}
    url = loc.get("url_for_pdf") or loc.get("url")
    if d.get("is_oa") and url:
        return url
    for loc in d.get("oa_locations", []):
        if loc.get("url_for_pdf"):
            return loc["url_for_pdf"]
    return None


def try_epmc_pdf(pmid, doi):
    """Find an OA PMCID via Europe PMC and return its PDF url."""
    q = f"DOI:{doi}" if doi else f"EXT_ID:{pmid} AND SRC:MED"
    try:
        d = json.loads(get(f"{EPMC}/search?query={urllib.parse.quote(q)}&format=json&resultType=core&pageSize=1"))
    except Exception:
        return None
    res = (d.get("resultList") or {}).get("result") or []
    if not res:
        return None
    r0 = res[0]
    if r0.get("isOpenAccess") == "Y" and r0.get("pmcid"):
        pmcid = r0["pmcid"]
        # Europe PMC OA full-text PDF endpoint
        return f"{EPMC}/{r0.get('source','PMC')}/{pmcid}/fullTextPDF" if False else \
               f"https://europepmc.org/articles/{pmcid}?pdf=render"
    # full text url list
    for u in (r0.get("fullTextUrlList") or {}).get("fullTextUrl", []):
        if u.get("documentStyle") == "pdf" and u.get("availability") in ("Open access", "Free"):
            return u.get("url")
    return None


def download_pdf(url, dest):
    try:
        data = get(url, accept="application/pdf", binary=True)
    except Exception:
        return False
    if not is_pdf(data) or len(data) < 8000:
        return False
    with open(dest, "wb") as f:
        f.write(data)
    return True


def citation(rec):
    au = rec["authors"]
    who = au[0] + (" et al." if len(au) > 1 else "") if au else "Anon"
    return f"{who} ({rec['year']}). {rec['title']}. {rec['journal']}. https://doi.org/{rec['doi']}" if rec["doi"] \
        else f"{who} ({rec['year']}). {rec['title']}. {rec['journal']}. PMID:{rec['pmid']}"


def main():
    os.makedirs(PAPERS, exist_ok=True)
    recs = parse_ris(RIS)
    print(f"corpus: {len(recs)} records", file=sys.stderr)
    rows = []
    n_pdf = n_xml = n_abs = 0
    for i, rec in enumerate(recs, 1):
        if not rec["pmid"]:
            continue
        pdfname = f"PMID{rec['pmid']}.pdf"
        pdfdest = os.path.join(PAPERS, pdfname)
        # 1) existing PDF (incl. ones dropped in manually)
        if os.path.exists(pdfdest) and os.path.getsize(pdfdest) > 8000:
            rows.append(rec_to_row(rec, pdfname, "fulltext-pdf"))
            n_pdf += 1
            print(f"  [{i}/{len(recs)}] pdf*  {pdfname}", file=sys.stderr)
            continue
        # 2) Unpaywall OA PDF
        url = try_unpaywall(rec["doi"])
        time.sleep(0.25)
        if url and download_pdf(url, pdfdest):
            rows.append(rec_to_row(rec, pdfname, "fulltext-pdf"))
            n_pdf += 1
            print(f"  [{i}/{len(recs)}] PDF   {pdfname}", file=sys.stderr)
            time.sleep(0.2)
            continue
        # 3) Europe PMC OA full-text XML -> txt
        ft = try_epmc_fulltext(rec["pmid"], rec["doi"])
        time.sleep(0.25)
        if ft:
            txtname = f"PMID{rec['pmid']}.fulltext.txt"
            with open(os.path.join(PAPERS, txtname), "w", encoding="utf-8") as f:
                f.write(f"{rec['title']}\n\n{ft[1]}")
            rows.append(rec_to_row(rec, txtname, "fulltext-xml"))
            n_xml += 1
            print(f"  [{i}/{len(recs)}] XML   {txtname}", file=sys.stderr)
            continue
        # 4) abstract fallback (always available, grounded + cited)
        if rec["abstract"]:
            absname = f"PMID{rec['pmid']}.abstract.txt"
            with open(os.path.join(PAPERS, absname), "w", encoding="utf-8") as f:
                f.write(f"{rec['title']}\n\nABSTRACT (摘要级证据，非全文):\n{rec['abstract']}")
            rows.append(rec_to_row(rec, absname, "abstract-only"))
            n_abs += 1
            print(f"  [{i}/{len(recs)}] abs   {absname}", file=sys.stderr)
        else:
            print(f"  [{i}/{len(recs)}] SKIP  PMID:{rec['pmid']} (无全文也无摘要)", file=sys.stderr)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file_location", "doi", "title", "year", "journal", "citation", "source"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nDONE: {len(rows)}/{len(recs)} docs indexed — "
          f"{n_pdf} full-text PDF, {n_xml} full-text XML, {n_abs} abstract-only.", file=sys.stderr)
    print(f"manifest: {MANIFEST}", file=sys.stderr)


def rec_to_row(rec, fname, source):
    return {
        "file_location": fname,
        "doi": rec["doi"] or "",
        "title": rec["title"],
        "year": rec["year"],
        "journal": rec["journal"],
        "citation": citation(rec),
        "source": source,
    }


if __name__ == "__main__":
    main()
