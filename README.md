<h1 align="center">Veterinary Behaviorist Agent</h1>

<p align="center">
  Evidence-based cat behavior consults for Claude Code, Codex, and local-first AI agents.
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">中文</a>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: CC BY-NC-ND 4.0" src="https://img.shields.io/badge/License-CC_BY--NC--ND_4.0-lightgrey.svg"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-blue.svg"></a>
  <a href="#native-agent-mode"><img alt="Local-first mode" src="https://img.shields.io/badge/Mode-local--first-lightgrey.svg"></a>
</p>

Evidence-based veterinary behavior agent for cats and companion animals. It is designed for Claude Code, Codex, and other agent runtimes that can read a skill file and run local commands.

The default mode uses the current agent itself as the reasoning model. You do not need to connect another LLM API. This repository provides the veterinary behavior prompt, local literature retrieval scripts, corpus generation tooling, and optional Zotero MCP / PaperQA2 integrations.

## What This Is

This project is not a standalone chatbot, web app, or hosted API.

It is a **skill-based agent package**:

- `skill/veterinary-behaviorist/SKILL.md` tells Claude Code, Codex, or another compatible agent how to behave as an evidence-based veterinary behavior consult agent.
- `scripts/search_corpus.py` lets that same agent search local veterinary behavior literature.
- `literature/` and `scripts/fetch_oa.py` help build the local paper corpus.
- Zotero MCP and PaperQA2 are optional add-ons.

In plain terms: you install this repository as a skill, then your existing Claude Code/Codex session becomes the veterinary behaviorist agent when you explicitly call it.

## What You Get Back

When you call the skill with a case or question, the final output is a **cited veterinary behavior consult**, usually structured like this:

```text
Bottom line
Medical triage
Most likely behavioral diagnosis and differentials
Management and safety plan
Behavior modification plan
Long-term living strategy
Evidence and citations
Limitations and escalation thresholds
```

Example prompt:

```text
/veterinary-behaviorist
My 4-year-old neutered indoor cat suddenly attacks my leg after seeing an outdoor cat through the window. What should I do?
```

Example output shape:

- identifies likely redirected aggression vs pain/fear differentials;
- lists medical red flags that require a veterinarian;
- gives immediate safety management steps;
- proposes desensitization/counterconditioning and environmental changes;
- cites retrieved papers by author/year plus DOI or PMID;
- marks abstract-only evidence and uncertainty.

## What It Does

- Guides the current agent through a veterinary behavior consult workflow.
- Retrieves local evidence from a PubMed-derived cat behavior corpus.
- Supports cat stress, fear, aggression, elimination problems, pain or disease-related behavior change, and clinic handling questions.
- Encourages medical-first triage before behavioral interpretation.
- Requires citations from retrieved evidence. No fabricated PMID, DOI, or author-year citations.
- Supports optional Zotero MCP for local reference libraries, notes, annotations, and PDFs.
- Supports optional PaperQA2 mode when the user already has an OpenAI-compatible LLM API.

## How It Works

Default Native Agent Mode:

1. The user explicitly calls `/veterinary-behaviorist`.
2. Claude Code, Codex, or another compatible agent runtime loads `skill/veterinary-behaviorist/SKILL.md`.
3. The current agent runs `scripts/search_corpus.py` to retrieve local evidence snippets.
4. If Zotero MCP is configured, the current agent can also search the local Zotero library.
5. The current agent writes the final answer using its own model and cites only retrieved sources.

Optional PaperQA2 mode:

1. The user configures an OpenAI-compatible API key.
2. PaperQA2 indexes the local corpus.
3. `scripts/consult.sh` asks PaperQA2 to retrieve and synthesize a cited answer.

## Invocation Flow

There is no separate chat UI in this repository. The agent is invoked through the AI environment where you install the skill.

For Claude Code or Codex:

1. Clone this repository.
2. Generate the local corpus.
3. Symlink `skill/veterinary-behaviorist` into your skills directory.
4. Set `VET_AGENT_HOME` to the repository path.
5. In a normal Claude Code or Codex session, explicitly say:

```text
/veterinary-behaviorist
use the veterinary behaviorist skill for this case
consult the veterinary behaviorist agent
```

After that, the current agent should read the skill instructions, run local retrieval commands, and answer with citations. The user does not call `search_corpus.py` directly unless they want to test retrieval by hand.

## Do You Need Zotero?

No. Zotero is optional.

The default setup works without Zotero:

- `literature/harvest_pubmed.py` finds candidate papers through PubMed.
- `scripts/fetch_oa.py` creates local text/PDF corpus files when legally available.
- `scripts/search_corpus.py` searches those local files.
- The current agent writes the final answer.

Use Zotero only if you want the agent to access your personal reference library, notes, annotations, or PDFs. Zotero is helpful for researchers who already manage papers there, but it is not required for this project to work.

## How Papers Are Found

Users do not need to manually do Web Research for the default corpus.

The paper discovery flow is scripted:

1. `literature/harvest_pubmed.py` runs predefined PubMed E-utilities queries for feline stress, fear, anxiety, aggression, bites, and related behavior topics.
2. It writes `literature/cat-behavior.ris` locally.
3. `scripts/fetch_oa.py` reads that RIS file and tries, in order:
   - existing local `papers/PMID<pmid>.pdf`
   - Unpaywall open-access PDF
   - Europe PMC open-access full-text XML
   - PubMed abstract text fallback
4. It writes `papers/manifest.csv`, which tells the retrieval script where each local source file is and how to cite it.

Manual research is only needed when:

- you want to expand the corpus beyond the bundled PubMed query buckets;
- you have lawful access to a paywalled PDF and want to add it locally;
- a specific paper is missing and you want to locate its PMID/DOI or a legal full-text source.

To add legally obtained PDFs, place them in `papers/` with the PMID filename:

```text
papers/PMID29099247.pdf
```

Then refresh:

```bash
python3 scripts/fetch_oa.py
```

## Repository Layout

```text
.
├── README.md
├── README.zh-CN.md
├── .env.example
├── .gitignore
├── settings.json
├── literature/
│   ├── README.md
│   ├── harvest_pubmed.py
│   └── cat-behavior.provenance.json
├── papers/
│   └── .gitkeep
├── scripts/
│   ├── search_corpus.py
│   ├── consult.sh
│   ├── fetch_oa.py
│   ├── index.sh
│   └── zotero_mcp_local.py
└── skill/
    └── veterinary-behaviorist/
        └── SKILL.md
```

Local corpus files are generated after setup:

```text
literature/cat-behavior.ris
papers/PMID*.abstract.txt
papers/PMID*.fulltext.txt
papers/PMID*.pdf
papers/manifest.csv
.pqa_index/
```

These files are for local retrieval and are not shipped with the repository.

## Data Policy

This repository does not include article full text, article abstracts, Zotero attachments, or Zotero notes.

The corpus is generated locally from:

- PubMed E-utilities: <https://www.ncbi.nlm.nih.gov/books/NBK25501/>
- Unpaywall API: <https://unpaywall.org/products/api>
- Europe PMC REST API: <https://europepmc.org/RestfulWebService>

`literature/cat-behavior.provenance.json` stores public bibliographic metadata: PMID, title, year, journal, and query source. Actual retrieval text is generated on the user's machine.

## Attribution and Legal Notes

This section is not legal advice.

This project does not bundle, copy, or redistribute Academic Research Suite / Academic Research Skill files, prompts, workflows, templates, or agent definitions. Its retrieval flow uses general local-first RAG and literature-search patterns, implemented specifically for this veterinary behavior corpus.

The project uses official, public APIs and repositories for paper discovery:

- PubMed records are discovered through NCBI E-utilities. NCBI's copyright guidance notes that NLM data include U.S. Government works and may also include abstracts from publications that can be protected by U.S. or non-U.S. copyright law. Users should follow NLM's copyright and disclaimer guidance: <https://www.nlm.nih.gov/databases/download.html> and <https://www.ncbi.nlm.nih.gov/books/NBK25497/>.
- Unpaywall is used only to discover open-access locations and requires a contact email in API requests: <https://unpaywall.org/products/api>.
- Europe PMC is used for open-access full-text XML when available: <https://europepmc.org/RestfulWebService>.

Generated abstracts, full text, PDFs, Zotero libraries, notes, annotations, and PaperQA2 indexes stay local. They are not redistributed by this repository.

This repository is not affiliated with NCBI, NLM, PubMed, Unpaywall, Europe PMC, Zotero, PaperQA2, DACVB, or ECAWBM.

## Requirements

Default Native Agent Mode:

- Python 3.11+
- Claude Code, Codex, or another agent environment that can read local instructions and run shell commands

Optional integrations:

- Zotero 7+: <https://www.zotero.org/download/>
- Zotero MCP server: <https://pypi.org/project/zotero-mcp-server/>
- pipx: <https://pipx.pypa.io/stable/installation/>
- PaperQA2 / `paper-qa`: <https://github.com/Future-House/paper-qa>
- sentence-transformers: <https://www.sbert.net/docs/installation.html>
- LiteLLM provider configuration: <https://docs.litellm.ai/docs/providers>

## Quick Start

Clone the repository:

```bash
git clone https://github.com/agentenatalie/cat-behavior-vet-agent.git
cd cat-behavior-vet-agent
```

Generate the local literature corpus:

```bash
cd literature
NCBI_EMAIL=you@example.com python3 harvest_pubmed.py
cd ..
UNPAYWALL_EMAIL=you@example.com python3 scripts/fetch_oa.py
```

Test local retrieval:

```bash
python3 scripts/search_corpus.py "owner-directed aggression in cats" -n 5
python3 scripts/search_corpus.py "猫突然攻击主人，疼痛和 redirected aggression 怎么区分?" -n 5
```

## Install as a Claude Code or Codex Skill

Codex:

```bash
mkdir -p ~/.codex/skills
ln -s /path/to/cat-behavior-vet-agent/skill/veterinary-behaviorist ~/.codex/skills/veterinary-behaviorist
```

Claude Code:

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/cat-behavior-vet-agent/skill/veterinary-behaviorist ~/.claude/skills/veterinary-behaviorist
```

Set the repository path:

```bash
export VET_AGENT_HOME=/path/to/cat-behavior-vet-agent
```

Put that line in your shell profile or configure the same environment variable in your agent runtime.

Call the skill explicitly:

```text
/veterinary-behaviorist
use the veterinary behaviorist skill for this case
consult the veterinary behaviorist agent
用兽医行为 skill 看一下这个 case
```

The skill is off by default. The current agent should not activate it just because a conversation mentions cats, dogs, behavior, aggression, stress, or anxiety.

## Native Agent Mode

Native Agent Mode is the default. It does not require an additional LLM API.

The current agent retrieves local evidence:

```bash
cd "$VET_AGENT_HOME"
python3 scripts/search_corpus.py "objective indicators of stress in cats" -n 10
python3 scripts/search_corpus.py "cat owner-directed aggression treatment" -n 10
```

`search_corpus.py` returns:

- Title and year
- DOI or PMID
- Corpus source
- Citation
- Matching snippet

The current agent then uses its own model to produce the consult answer.

## Behavior Contract for Current Agents

When the skill is activated, the current agent should:

1. Restate the case: species, age, sex/neuter status, behavior, triggers, timeline, and injury risk.
2. Start with medical-first triage: pain, skin disease, urinary disease, endocrine disease, neurologic disease, medication effects, cognitive decline.
3. Retrieve evidence with `scripts/search_corpus.py`.
4. Use Zotero MCP if available and relevant.
5. Classify aggression by motivation: fear/defensive, redirected, petting-induced, play, pain, territorial, predatory, or other supported categories.
6. Provide management, environmental modification, behavior modification, safety thresholds, and referral triggers.
7. Cite only retrieved evidence from local search, Zotero, or PaperQA2.
8. State uncertainty when evidence is abstract-only, weak, extrapolated, or missing.

Suggested answer format:

```text
Bottom line
Medical triage
Most likely diagnosis and differentials
Plan
Long-term living strategy
Evidence and citations
Limitations and escalation thresholds
```

## Generate or Refresh the Corpus

Generate PubMed RIS data:

```bash
cd /path/to/cat-behavior-vet-agent/literature
NCBI_EMAIL=you@example.com python3 harvest_pubmed.py
```

Fetch open-access full text when available and create `papers/manifest.csv`:

```bash
cd /path/to/cat-behavior-vet-agent
UNPAYWALL_EMAIL=you@example.com python3 scripts/fetch_oa.py
```

Fetch strategy:

1. Use an existing local `papers/PMID<pmid>.pdf` if present.
2. Try Unpaywall open-access PDF.
3. Try Europe PMC open-access full-text XML and convert it to text.
4. Use PubMed abstract text when no full text is available.

If you have lawful access to a PDF, place it in `papers/`:

```text
papers/PMID29099247.pdf
```

Then refresh the manifest:

```bash
python3 scripts/fetch_oa.py
```

## Optional: PaperQA2 Mode

PaperQA2 mode lets `pqa` retrieve and synthesize cited answers. Use it when you already have an OpenAI-compatible LLM API.

Install:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install "paper-qa>=5"
pipx inject paper-qa sentence-transformers
```

Configure:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
PQA_API_KEY=your-openai-compatible-provider-key
UNPAYWALL_EMAIL=you@example.com
```

Index:

```bash
cd /path/to/cat-behavior-vet-agent
./scripts/index.sh
```

Ask:

```bash
./scripts/consult.sh "What are reliable objective indicators of stress in cats?"
```

Default PaperQA2 settings are in `settings.json`. The default model is `mimo-v2.5-pro` through an OpenAI-compatible endpoint. To use another provider, update `llm`, `summary_llm`, model names, model IDs, and API base values in `settings.json`. Keep `api_key` as `os.environ/PQA_API_KEY`.

## Optional: Zotero MCP

Zotero MCP lets the current agent search a local Zotero library, read metadata, inspect full text, and use notes or annotations.

Install:

```bash
pipx install zotero-mcp-server
```

Make sure Zotero 7+ is installed, running, and local API access is enabled.

If `localhost:23119` fails but `127.0.0.1:23119` works, use the launcher:

```bash
~/.local/pipx/venvs/zotero-mcp-server/bin/python /path/to/cat-behavior-vet-agent/scripts/zotero_mcp_local.py serve
```

Import the generated RIS file into Zotero:

```bash
cd /path/to/cat-behavior-vet-agent
curl -X POST http://127.0.0.1:23119/connector/import \
  -H "Content-Type: application/x-research-info-systems" \
  --data-binary @literature/cat-behavior.ris
```

Repeated imports can create duplicate Zotero items. Use Zotero's Duplicate Items view or import into a fresh collection.

## FAQ

### Do I need another LLM API?

No. The default Native Agent Mode uses Claude Code, Codex, or your current agent runtime as the reasoning model.

### Why is there a PaperQA2 configuration?

PaperQA2 is an optional mode for users who want a separate literature-QA engine and already have an OpenAI-compatible API key.

### Why are papers not included?

Article abstracts, full text, and PDFs can have different redistribution rights. The repository includes reproducible retrieval scripts and public provenance metadata instead.

### Is this a veterinary diagnosis service?

No. It is an evidence-retrieval and reasoning aid. It cannot replace an in-person veterinarian or a board-certified veterinary behaviorist.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

Useful contribution areas:

- Better PubMed query buckets
- Higher-quality retrieval ranking
- Additional species or behavior domains
- More robust Zotero MCP setup docs
- Tests for corpus generation and local search

## Safety and Medical Disclaimer

This project is for educational and decision-support use. Behavior changes can be caused by pain, disease, medication effects, or environmental stressors. For injuries, escalating aggression, sudden behavior change, or welfare risk, seek in-person veterinary care.

## License

Licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](LICENSE).

You may share unmodified copies for non-commercial purposes with attribution. Commercial use and distribution of modified versions require separate permission.

Because this license includes NonCommercial and NoDerivatives restrictions, this is a public-source project, not an OSI open-source project.
