#!/usr/bin/env python3
"""Search the local veterinary-behavior corpus without calling an LLM.

This is the default evidence retrieval path for Native Skill Mode: the current
AI runtime runs this script, reads the returned snippets, and uses its own model
to synthesize the answer.
"""
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import Counter
from pathlib import Path


SYNONYMS = {
    "应激": ["stress", "stressor", "cortisol", "fear", "anxiety"],
    "压力": ["stress", "cortisol"],
    "攻击": ["aggression", "aggressive", "bite", "owner-directed"],
    "咬": ["bite", "aggression"],
    "抓": ["scratch", "scratching"],
    "恐惧": ["fear", "anxiety", "defensive"],
    "焦虑": ["anxiety", "fear", "stress"],
    "疼痛": ["pain", "medical", "disease", "inflammation"],
    "疾病": ["disease", "medical", "metabolic", "inflammation"],
    "皮肤": ["skin", "dermatologic", "pruritus"],
    "泌尿": ["urinary", "urination", "elimination", "lower urinary tract"],
    "排尿": ["urination", "urinary", "elimination"],
    "排泄": ["elimination", "urination", "defecation"],
    "转嫁": ["redirected", "redirected aggression"],
    "主人": ["owner", "owner-directed", "human-directed"],
    "人": ["human", "owner", "people"],
    "玩耍": ["play", "play-related"],
    "环境": ["environmental", "enrichment", "resources"],
    "药": ["psychopharmacology", "gabapentin", "medication"],
    "加巴喷丁": ["gabapentin"],
    "皮质醇": ["cortisol"],
}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*|[\u4e00-\u9fff]", text)
    return [t for t in tokens if len(t) > 1 or "\u4e00" <= t <= "\u9fff"]


def expand_query(query: str) -> list[str]:
    parts = tokenize(query)
    expanded = list(parts)
    for zh, terms in SYNONYMS.items():
        if zh in query:
            expanded.extend(tokenize(" ".join(terms)))
    return expanded


def read_manifest(root: Path) -> list[dict[str, str]]:
    manifest = root / "papers" / "manifest.csv"
    if not manifest.exists():
        raise FileNotFoundError(
            "papers/manifest.csv not found. Generate the local corpus first: "
            "python3 scripts/fetch_oa.py"
        )
    with manifest.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_doc(root: Path, row: dict[str, str]) -> str:
    path = root / "papers" / row["file_location"]
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def split_snippets(text: str, max_len: int = 900) -> list[str]:
    chunks = re.split(r"\n{2,}|(?<=[.!?。！？])\s+", text)
    snippets: list[str] = []
    buf = ""
    for chunk in chunks:
        chunk = re.sub(r"\s+", " ", chunk).strip()
        if not chunk:
            continue
        if len(buf) + len(chunk) + 1 <= max_len:
            buf = f"{buf} {chunk}".strip()
        else:
            if buf:
                snippets.append(buf)
            buf = chunk[:max_len]
    if buf:
        snippets.append(buf)
    return snippets


def score(query_terms: list[str], title: str, snippet: str) -> float:
    title_terms = Counter(tokenize(title))
    snippet_terms = Counter(tokenize(snippet))
    score_value = 0.0
    for term in query_terms:
        score_value += 4.0 * title_terms.get(term, 0)
        score_value += snippet_terms.get(term, 0)
        if term in snippet.lower():
            score_value += 0.5
    length_penalty = math.log(max(len(tokenize(snippet)), 10), 10)
    return score_value / length_penalty


def search(root: Path, query: str, limit: int) -> list[tuple[float, dict[str, str], str]]:
    rows = read_manifest(root)
    query_terms = expand_query(query)
    if not query_terms:
        return []

    results: list[tuple[float, dict[str, str], str]] = []
    for row in rows:
        text = read_doc(root, row)
        if not text:
            continue
        snippets = split_snippets(text)
        best = max((score(query_terms, row.get("title", ""), s), s) for s in snippets)
        if best[0] > 0:
            results.append((best[0], row, best[1]))

    results.sort(key=lambda item: item[0], reverse=True)
    return results[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Search local corpus snippets without an LLM.")
    parser.add_argument("query", help="Evidence question or keyword query")
    parser.add_argument("-n", "--limit", type=int, default=8, help="Number of results to print")
    parser.add_argument(
        "--root",
        default=None,
        help="Corpus root. Defaults to the parent directory of this script.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    try:
        results = search(root, args.query, args.limit)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not results:
        print("No matching local evidence found.")
        return 0

    for idx, (score_value, row, snippet) in enumerate(results, 1):
        print(f"[{idx}] {row.get('title', 'Untitled')} ({row.get('year', '')})")
        print(f"PMID/DOI: {row.get('citation', '').split('PMID:')[-1] if 'PMID:' in row.get('citation', '') else row.get('doi', '')}")
        print(f"Source: {row.get('source', '')}; file: papers/{row.get('file_location', '')}; score: {score_value:.2f}")
        print(f"Citation: {row.get('citation', '')}")
        print(f"Snippet: {snippet}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
