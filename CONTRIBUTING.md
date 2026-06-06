# Contributing

Thank you for improving Veterinary Behaviorist Skill. This project is a local-first skill package for evidence-based veterinary behavior support in AI runtimes such as Claude Code and Codex.

This repository is public-source under CC BY-NC-ND 4.0. By opening a pull request, you confirm that you own or have permission to submit the contribution, and you grant the maintainers permission to review, adapt, merge, and publish your contribution in this repository under the project license.

## Good Contributions

- Better PubMed query buckets
- Better local retrieval ranking
- Tests for the bundled skill scripts
- Clearer setup docs for Claude Code, Codex, Zotero MCP, or PaperQA2
- Support for additional species or behavior domains
- Safer consult workflow language and escalation criteria

## Ground Rules

- Do not commit API keys, local Zotero exports, notes, annotations, PDFs, generated corpus text, generated RIS files, or PaperQA2 indexes.
- Do not add fabricated citations.
- Do not add aversive, dominance-based, or punishment-first behavior advice.
- Keep Native Skill Mode as the default path. PaperQA2 and Zotero MCP should remain optional integrations.
- Treat medical claims carefully. Behavior change can be driven by pain or disease.
- Do not redistribute modified versions of this project without separate permission from the copyright holders.

## Development Setup

```bash
git clone https://github.com/agentenatalie/cat-behavior-vet-agent.git
cd cat-behavior-vet-agent
```

Generate a local corpus if you need to test retrieval:

```bash
cd skill/veterinary-behaviorist
NCBI_EMAIL=you@example.com python3 literature/harvest_pubmed.py
UNPAYWALL_EMAIL=you@example.com python3 scripts/fetch_oa.py
```

Run basic checks:

```bash
python3 -m py_compile \
  skill/veterinary-behaviorist/scripts/search_corpus.py \
  skill/veterinary-behaviorist/scripts/fetch_oa.py \
  skill/veterinary-behaviorist/scripts/zotero_mcp_local.py \
  skill/veterinary-behaviorist/literature/harvest_pubmed.py
bash -n \
  skill/veterinary-behaviorist/scripts/consult.sh \
  skill/veterinary-behaviorist/scripts/index.sh
python3 -m json.tool skill/veterinary-behaviorist/settings.json >/dev/null
python3 skill/veterinary-behaviorist/scripts/search_corpus.py "owner-directed aggression in cats" -n 3
```

Before opening a pull request, check that generated or private files are not staged:

```bash
git diff --cached --name-only | grep -E '(^|/)\\.env$|\\.ris$|\\.pdf$|papers/.*\\.(txt|pdf)$|papers/manifest\\.csv|\\.pqa_index' || true
```

## Pull Requests

Include:

- What changed
- Why it matters
- How you tested it
- Any safety, citation, or data-rights considerations

## 中文说明

欢迎贡献。这个项目的目标是让 Claude Code、Codex 等 AI 工具以本地优先的方式执行循证兽医行为 consult。

本仓库使用 CC BY-NC-ND 4.0。提交 PR 代表你确认自己拥有或被授权提交该贡献，并授权维护者 review、调整、合并和以本项目许可证发布你的贡献。

贡献时请注意：

- 不要提交 API key、Zotero 本地库、笔记、注释、PDF、生成的摘要/全文语料、生成的 RIS 文件或 PaperQA2 索引。
- 不要加入伪造引用。
- 不要加入惩罚优先、支配论或 aversive 行为建议。
- 默认路径应保持为 Native Skill Mode；PaperQA2 和 Zotero MCP 是可选增强。
- 医学相关表述要谨慎，行为变化可能来自疼痛或疾病。
- 未经版权持有人另行许可，不要分发本项目的修改版本。

提交 PR 时请写明改动内容、原因、测试方式，以及任何安全、引用或数据版权相关考虑。
