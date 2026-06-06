<h1 align="center">Veterinary Behaviorist Skill</h1>

<p align="center">
  A self-contained, evidence-based cat behavior consult skill for Claude Code, Codex, and local-first AI runtimes.
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">中文</a>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: CC BY-NC-ND 4.0" src="https://img.shields.io/badge/License-CC_BY--NC--ND_4.0-lightgrey.svg"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-blue.svg"></a>
  <a href="#native-skill-mode"><img alt="Mode: local-first" src="https://img.shields.io/badge/Mode-local--first-lightgrey.svg"></a>
  <a href="#data-and-copyright"><img alt="Corpus: local only" src="https://img.shields.io/badge/Corpus-local_only-lightgrey.svg"></a>
</p>

`Veterinary Behaviorist Skill` helps an AI coding assistant handle cat and companion-animal behavior questions as a structured, evidence-based consult. It guides intake, retrieves local veterinary behavior literature, optionally uses Zotero MCP or PaperQA2, checks real-world reports when web access is available, and writes a cited answer.

The default mode uses the AI runtime you already have. You do not need to connect another LLM API.

## What This Is

This repository is the source and distribution package for one self-contained skill:

```text
skill/veterinary-behaviorist/
```

It is not a standalone chatbot, web app, hosted API, or separate agent service.

Install the skill folder into Claude Code, Codex, or another compatible AI runtime. When you invoke the skill, the current AI assistant reads `SKILL.md`, asks intake questions, runs the bundled scripts, and produces the final consult.

## Agent vs Skill

An **AI agent/runtime** is the assistant you are already using, such as Claude Code or Codex.

A **skill** is a package of instructions, scripts, config, and resources that teaches that assistant a specific workflow.

This project is now a skill, not a separate agent. The current AI assistant becomes the veterinary behavior consultant only while using this skill.

## What You Get

For a full case, the skill produces a cited veterinary behavior consult:

```text
Confirmed case summary
Bottom line
Medical triage
Most likely diagnosis and differentials
Safety and management plan
Behavior modification plan
Long-term living strategy
Scientific evidence
Real-world reports / anecdotal patterns
Limitations and escalation thresholds
```

If the case is vague, the skill should not jump to a diagnosis. For example, if the user says:

```text
My cat suddenly attacked me.
```

The AI should first ask for the minimum context: animal profile, medical history, exact incident sequence, injury severity, pattern, triggers, household safety, previous responses, and user constraints. If the answer is incomplete, it should ask again for the missing facts. After enough context is available, it summarizes the case and asks the user to confirm before retrieving evidence and writing the full consult.

Urgent medical or safety risk is handled immediately before the remaining intake continues.

## Native Skill Mode

Native Skill Mode is the default and does not require another LLM API.

The current AI runtime:

1. Loads `skill/veterinary-behaviorist/SKILL.md`.
2. Runs intake and confirms the case summary.
3. Uses `scripts/search_corpus.py` inside the skill folder to retrieve local evidence.
4. Optionally searches Zotero MCP if the user has configured Zotero.
5. Uses web search, when available, to find similar real-world reports after the scientific retrieval step.
6. Writes the answer with its own model and cites only retrieved sources.

PaperQA2 is optional. Use it only if you want a separate literature-QA engine and already have an OpenAI-compatible API key.

## Install

Clone the repository:

```bash
git clone https://github.com/agentenatalie/cat-behavior-vet-agent.git
cd cat-behavior-vet-agent
```

Install as a Codex skill:

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skill/veterinary-behaviorist" ~/.codex/skills/veterinary-behaviorist
```

Install as a Claude Code skill:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skill/veterinary-behaviorist" ~/.claude/skills/veterinary-behaviorist
```

You can also copy only the skill folder:

```bash
cp -R skill/veterinary-behaviorist ~/.codex/skills/veterinary-behaviorist
```

Use a symlink if you want repository updates to affect the installed skill immediately.

## Call the Skill

Invocation syntax depends on the AI runtime. Use the skill name explicitly:

```text
Use $veterinary-behaviorist to assess this case.
```

or:

```text
/veterinary-behaviorist
My 4-year-old neutered indoor cat suddenly attacks my leg after seeing an outdoor cat through the window. What should I do?
```

The user does not need to run `search_corpus.py` by hand during normal use. The current AI assistant should run the bundled retrieval commands after intake is complete.

## Generate the Local Literature Corpus

The public repository does not include article abstracts, article full text, PDFs, RIS files, or vector indexes. Generate them locally:

```bash
cd skill/veterinary-behaviorist
NCBI_EMAIL=you@example.com python3 literature/harvest_pubmed.py
UNPAYWALL_EMAIL=you@example.com python3 scripts/fetch_oa.py
```

Test retrieval:

```bash
python3 scripts/search_corpus.py "owner-directed aggression in cats" -n 5
python3 scripts/search_corpus.py "cat redirected aggression outdoor cat window" -n 5
```

Generated local files:

```text
skill/veterinary-behaviorist/literature/cat-behavior.ris
skill/veterinary-behaviorist/papers/PMID*.abstract.txt
skill/veterinary-behaviorist/papers/PMID*.fulltext.txt
skill/veterinary-behaviorist/papers/PMID*.pdf
skill/veterinary-behaviorist/papers/manifest.csv
skill/veterinary-behaviorist/.pqa_index/
```

These files stay local and are ignored by Git.

## How Papers Are Found

Users do not need to manually do web research to build the default corpus.

The skill uses a scripted discovery flow:

1. `literature/harvest_pubmed.py` runs predefined PubMed E-utilities searches for feline stress, fear, anxiety, aggression, bites, and related behavior topics.
2. It writes `literature/cat-behavior.ris` locally.
3. `scripts/fetch_oa.py` reads the RIS file and tries, in order:
   - existing local `papers/PMID<pmid>.pdf`
   - Unpaywall open-access PDF
   - Europe PMC open-access full-text XML
   - PubMed abstract text fallback
4. It writes `papers/manifest.csv`, which local search uses for file paths and citations.

Manual research is useful only when you want to expand the corpus, add a specific lawful PDF, or locate a missing PMID/DOI.

If you have lawful access to a paper, place it in the local skill corpus with its PMID filename:

```text
skill/veterinary-behaviorist/papers/PMID29099247.pdf
```

Then refresh:

```bash
cd skill/veterinary-behaviorist
python3 scripts/fetch_oa.py
```

## Component Setup

| Component | Required? | Install / download | Configuration |
| --- | --- | --- | --- |
| Python 3.11+ | Yes | <https://www.python.org/downloads/> | Used by all bundled scripts. |
| PubMed E-utilities | Yes for corpus generation | <https://www.ncbi.nlm.nih.gov/books/NBK25501/> | Set `NCBI_EMAIL=you@example.com` when running `harvest_pubmed.py`. |
| Unpaywall API | Yes for OA lookup | <https://unpaywall.org/products/api> | Set `UNPAYWALL_EMAIL=you@example.com` when running `fetch_oa.py`. |
| Europe PMC REST API | Used automatically | <https://europepmc.org/RestfulWebService> | No key required for the current script. |
| Zotero 7+ | Optional | <https://www.zotero.org/download/> | Install only if you want the AI to use your local Zotero library, notes, annotations, or PDFs. |
| Zotero MCP server | Optional | <https://pypi.org/project/zotero-mcp-server/> | Install with `pipx install zotero-mcp-server`; keep Zotero running with local API access enabled. |
| PaperQA2 / `paper-qa` | Optional | <https://github.com/Future-House/paper-qa> | Requires an OpenAI-compatible API key in `.env`. |
| pipx | Optional | <https://pipx.pypa.io/stable/installation/> | Convenient for installing PaperQA2 and Zotero MCP. |
| sentence-transformers | Optional | <https://www.sbert.net/docs/installation.html> | Inject into PaperQA2 if using local embeddings. |
| LiteLLM provider config | Optional | <https://docs.litellm.ai/docs/providers> | Edit `settings.json` if using a different PaperQA2 model/provider. |
| Web access | Optional | Depends on your AI runtime | Used after scientific retrieval to find similar public real-world cases. |

## Optional: PaperQA2

Install:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install "paper-qa>=5"
pipx inject paper-qa sentence-transformers
```

Configure:

```bash
cd skill/veterinary-behaviorist
cp .env.example .env
```

Edit `.env`:

```bash
PQA_API_KEY=your-openai-compatible-provider-key
UNPAYWALL_EMAIL=you@example.com
```

Index and ask:

```bash
./scripts/index.sh
./scripts/consult.sh "What are reliable objective indicators of stress in cats?"
```

Default PaperQA2 settings live in `skill/veterinary-behaviorist/settings.json`. Change `llm`, `summary_llm`, model IDs, API base, and provider settings there if needed. Keep `api_key` as `os.environ/PQA_API_KEY`.

## Optional: Zotero MCP

Zotero is not required. Use it only if you already manage papers in Zotero or want the AI to search your local library.

Install:

```bash
pipx install zotero-mcp-server
```

Make sure Zotero 7+ is installed, running, and local API access is enabled.

If `localhost:23119` fails but `127.0.0.1:23119` works, use the bundled launcher:

```bash
~/.local/pipx/venvs/zotero-mcp-server/bin/python skill/veterinary-behaviorist/scripts/zotero_mcp_local.py serve
```

Import the generated RIS into Zotero:

```bash
cd skill/veterinary-behaviorist
curl -X POST http://127.0.0.1:23119/connector/import \
  -H "Content-Type: application/x-research-info-systems" \
  --data-binary @literature/cat-behavior.ris
```

Repeated imports can create duplicates. Use Zotero's Duplicate Items view or import into a fresh collection.

## Real-World Web Corroboration

Web search is not the default way to find papers. It is a second-stage consult step.

After intake and scientific retrieval, the AI may search public web sources for similar real-world cases and outcomes. These reports help identify practical implementation patterns, such as what similar owners tried, what helped, what failed, and whether the case context really matches.

Real-world reports must be labeled anecdotal. They do not override veterinary literature, medical triage, or safety rules.

## Repository Layout

```text
.
├── README.md
├── README.zh-CN.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
└── skill/
    └── veterinary-behaviorist/
        ├── SKILL.md
        ├── .env.example
        ├── settings.json
        ├── agents/
        │   └── openai.yaml
        ├── literature/
        │   ├── harvest_pubmed.py
        │   └── cat-behavior.provenance.json
        ├── papers/
        │   └── .gitkeep
        └── scripts/
            ├── search_corpus.py
            ├── fetch_oa.py
            ├── consult.sh
            ├── index.sh
            └── zotero_mcp_local.py
```

## Data and Copyright

This repository includes only skill instructions, scripts, configuration templates, and public provenance metadata.

It does not include:

- `.env` files or API keys
- PaperQA2 vector indexes
- generated abstracts, full text, PDFs, or `manifest.csv`
- generated RIS files
- Zotero local libraries, notes, annotations, or attachments

Paper discovery uses official public services:

- PubMed E-utilities: <https://www.ncbi.nlm.nih.gov/books/NBK25501/>
- Unpaywall API: <https://unpaywall.org/products/api>
- Europe PMC REST API: <https://europepmc.org/RestfulWebService>

PubMed accessibility does not mean every abstract can be redistributed. Open-access discovery does not mean every PDF has the same license. Generated corpus files stay on the user's machine unless each item has been separately checked for redistribution rights.

## Attribution

This project does not bundle, copy, or redistribute Academic Research Suite / Academic Research Skill files, prompts, templates, or agent definitions.

It uses a general local-first research pattern: scripted discovery, local corpus generation, local retrieval, optional reference-manager integration, and cited synthesis by the current AI runtime. The implementation and veterinary behavior workflow in this repository are specific to this skill.

This project is not affiliated with NCBI, NLM, PubMed, Unpaywall, Europe PMC, Zotero, PaperQA2, DACVB, or ECAWBM.

## Safety

This skill is for education and decision support. It is not a veterinary diagnosis service and does not replace an in-person veterinarian or board-certified veterinary behaviorist.

Behavior changes can be caused by pain, disease, medication effects, neurologic issues, or environmental stressors. For injuries, escalating aggression, sudden behavior change, severe distress, or welfare risk, seek in-person veterinary care.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

Useful contribution areas:

- better PubMed query buckets
- better local retrieval ranking
- additional species or behavior domains
- stronger Zotero MCP setup docs
- tests for corpus generation and local search

## License

Licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](LICENSE).

You may share unmodified copies for non-commercial purposes with attribution. Commercial use and distribution of modified versions require separate permission.

Because this license includes NonCommercial and NoDerivatives restrictions, this is a public-source project, not an OSI open-source project.
