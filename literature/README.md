# Cat behaviour literature corpus

Focus: feline stress behaviour + aggression toward humans.

## Files
- `harvest_pubmed.py` — harvester. Queries PubMed E-utilities (esearch + efetch MEDLINE),
  unions topic buckets, dedups by PMID, writes RIS. Re-run to refresh.
- `cat-behavior.ris` — 63 real records (RIS), ready to import into Zotero.
- `cat-behavior.provenance.json` — query strings, source, retrieval date, per-record PMIDs.

## Source
PubMed E-utilities. Every record comes from an efetch MEDLINE response — no fabricated data.
Buckets:
1. stress / stress response / cortisol / fear / anxiety (behaviour)  — 25
2. stress in veterinary / handling / restraint context              — 12
3. aggression toward humans (owner / people / bite)                  — 25
4. aggression / agonistic behaviour (general)                        — 12

After dedup: 63 unique articles.

## Refresh
```bash
python3 harvest_pubmed.py            # rewrites cat-behavior.ris
# then re-import into Zotero (Zotero must be running):
curl -X POST http://127.0.0.1:23119/connector/import \
  -H "Content-Type: application/x-research-info-systems" \
  --data-binary @cat-behavior.ris
```
Note: re-import creates duplicate items; use Zotero's "Duplicate Items" view to merge,
or import into a fresh collection.
