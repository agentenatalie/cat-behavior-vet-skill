# Veterinary Behaviorist Agent

循证猫/伴侣动物行为 consult agent。它把大模型当推理层，把本地文献库、PaperQA2 和 Zotero MCP 当证据层，用来回答猫应激、攻击、排泄、恐惧、疼痛/疾病相关行为变化等问题。

这个仓库提供两种用法：

- CLI：直接运行 `scripts/consult.sh "问题"`，PaperQA2 检索本地语料并生成带引用回答。
- Skill：把 `skill/veterinary-behaviorist/SKILL.md` 安装到 Codex 或 Claude Code skills 目录，只有显式调用 `/veterinary-behaviorist` 或同义请求时启用。

## 发布范围和文献版权

可以提交到 GitHub：

- agent prompt / skill 文件
- CLI 脚本、PaperQA2 配置、环境变量模板
- PubMed 查询脚本
- PubMed provenance 元数据：PMID、标题、年份、期刊、查询来源

不要提交到 GitHub：

- `.env` 和任何 API key
- `.pqa_index/` PaperQA2 向量索引
- `papers/` 下生成的摘要文本、全文文本、PDF、`manifest.csv`
- `literature/*.ris`
- Zotero 本地库、笔记、注释、附件

原因：

- PubMed 可访问不等于每篇摘要都允许二次分发。RIS 文件和 `papers/*.abstract.txt` 里会包含摘要正文，所以默认只在本地生成，不提交。
- Unpaywall / Europe PMC 可找到开放获取全文，但每篇文章的许可不同。PDF 默认只供本地检索使用，除非逐篇确认许可证允许再分发。
- Zotero 内容属于使用者本地资料库，不能随仓库发布。

当前 `.gitignore` 已按这个边界配置。公开仓库只保留复现语料的脚本和元数据。

## 目录结构

```text
.
├── README.md
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
│   ├── consult.sh
│   ├── fetch_oa.py
│   ├── index.sh
│   └── zotero_mcp_local.py
└── skill/
    └── veterinary-behaviorist/
        └── SKILL.md
```

本地运行后会生成：

```text
literature/cat-behavior.ris
papers/PMID*.abstract.txt
papers/PMID*.fulltext.txt
papers/PMID*.pdf
papers/manifest.csv
.pqa_index/
```

这些文件会被 Git 忽略。

## 组件和下载链接

必需组件：

- Python 3.11+：<https://www.python.org/downloads/>
- pipx：<https://pipx.pypa.io/stable/installation/>
- PaperQA2 / `paper-qa`：<https://github.com/Future-House/paper-qa>
- sentence-transformers：<https://www.sbert.net/docs/installation.html>
- LiteLLM provider 配置参考：<https://docs.litellm.ai/docs/providers>

可选组件：

- Zotero 7+：<https://www.zotero.org/download/>
- Zotero MCP server：<https://pypi.org/project/zotero-mcp-server/>
- NCBI E-utilities：<https://www.ncbi.nlm.nih.gov/books/NBK25501/>
- Unpaywall API：<https://unpaywall.org/products/api>
- Europe PMC REST API：<https://europepmc.org/RestfulWebService>

本项目默认 PaperQA2 配置：

- LLM：`mimo-v2.5-pro`
- API base：`https://token-plan-sgp.xiaomimimo.com/v1`
- API key 环境变量：`PQA_API_KEY`
- embedding：`st-multi-qa-MiniLM-L6-cos-v1`
- embedding 在本地跑，不调用外部 embedding API

要换模型或 provider，改 `settings.json`：

- `llm`
- `summary_llm`
- `llm_config.model_list[0].model_name`
- `llm_config.model_list[0].litellm_params.model`
- `llm_config.model_list[0].litellm_params.api_base`
- `summary_llm_config` 里的同名字段

`api_key` 建议继续用 `os.environ/PQA_API_KEY`。

## 安装

进入仓库根目录：

```bash
cd /path/to/vet-agent
```

安装 PaperQA2：

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install "paper-qa>=5"
pipx inject paper-qa sentence-transformers
```

确认 `pqa` 可用：

```bash
pqa --help
```

配置环境变量：

```bash
cp .env.example .env
```

编辑 `.env`：

```bash
PQA_API_KEY=your-openai-compatible-provider-key
UNPAYWALL_EMAIL=you@example.com
```

`UNPAYWALL_EMAIL` 用于 Unpaywall API 联系邮箱。建议使用可联系到你的邮箱。

## 生成本地文献语料

先用 PubMed E-utilities 生成 RIS。这个步骤会把摘要写入本地 RIS 文件，所以该文件被 Git 忽略。

```bash
cd /path/to/vet-agent/literature
NCBI_EMAIL=you@example.com python3 harvest_pubmed.py
```

输出：

```text
literature/cat-behavior.ris
literature/cat-behavior.provenance.json
```

再抓取开放获取全文，并为 PaperQA2 生成 manifest：

```bash
cd /path/to/vet-agent
UNPAYWALL_EMAIL=you@example.com python3 scripts/fetch_oa.py
```

输出：

```text
papers/PMID*.abstract.txt
papers/PMID*.fulltext.txt
papers/PMID*.pdf
papers/manifest.csv
```

抓取策略：

1. 如果 `papers/PMID<pmid>.pdf` 已存在且大小正常，使用现有 PDF。
2. 尝试 Unpaywall 开放获取 PDF。
3. 尝试 Europe PMC 开放获取 full-text XML，转为纯文本。
4. 找不到全文时，使用 PubMed 摘要生成 `PMID*.abstract.txt`。

如果有机构权限获取的 PDF，可以手动放进 `papers/`：

```text
papers/PMID29099247.pdf
```

再运行：

```bash
python3 scripts/fetch_oa.py
```

脚本会优先使用已有 PDF，并重写 `papers/manifest.csv`。

## 建索引

```bash
cd /path/to/vet-agent
./scripts/index.sh
```

索引输出在 `.pqa_index/`。索引使用本地 sentence-transformers embedding，不需要 LLM API key。脚本会给 PaperQA2 设置一个占位 key，避免某些配置读取时报错。

## CLI 使用

```bash
cd /path/to/vet-agent
./scripts/consult.sh "猫的应激行为有哪些可靠的客观指标?"
./scripts/consult.sh "redirected aggression 的触发因素和攻击对象规律?"
./scripts/consult.sh "猫突然开始攻击主人，应该优先排查哪些医学原因?"
```

`consult.sh` 会：

1. 读取 `.env`
2. 检查 `PQA_API_KEY`
3. 设置 `OPENAI_API_KEY`
4. 调用 `pqa --settings settings ask`

回答应包含引用。没有检索到足够证据时，不要补编引用。

## Skill 安装

Codex：

```bash
mkdir -p ~/.codex/skills
ln -s /path/to/vet-agent/skill/veterinary-behaviorist ~/.codex/skills/veterinary-behaviorist
```

Claude Code：

```bash
mkdir -p ~/.claude/skills
ln -s /path/to/vet-agent/skill/veterinary-behaviorist ~/.claude/skills/veterinary-behaviorist
```

设置仓库路径：

```bash
export VET_AGENT_HOME=/path/to/vet-agent
```

把这行放进你的 shell profile，或在 agent 运行环境里配置同名环境变量。Skill 里不写死本机路径；其他 agent 调用时应从 `VET_AGENT_HOME` 找仓库根目录。

激活方式：

```text
/veterinary-behaviorist
用兽医行为 skill 看一下这个 case
consult 兽医行为医生 agent
call the veterinary behaviorist
```

不要因为对话里出现“猫、狗、行为、攻击、应激、焦虑”等词就自动启用。必须显式调用。

## 给其他 agent 的调用规则

处理 case 时按这个顺序：

1. 先确认物种、年龄、性别/绝育、行为、触发因素、时间线、伤害风险。
2. 先做医疗优先分诊：疼痛、皮肤病、泌尿、内分泌、神经、药物、认知退化等。
3. 用 PaperQA2 检索核心证据：

```bash
cd "$VET_AGENT_HOME"
./scripts/consult.sh "focused evidence question"
```

4. 按动机分类行为问题。猫攻击不要只写“坏脾气”，要区分 fear/defensive、redirected、petting-induced、play、pain、territorial、predatory 等。
5. 方案要包含环境管理、行为改变、风险控制、何时需要兽医行为专科或当面兽医。
6. 引用只来自检索结果或 Zotero item。没有证据就明确说是临床推理，不要伪造 PMID、DOI、作者年份。

推荐输出结构：

```text
结论
医疗优先分诊
最可能诊断和鉴别
处理方案
长期相处策略
证据和引用
局限和升级条件
```

## Zotero MCP 可选配置

Zotero MCP 用于搜索本地 Zotero 文献库、读取元数据、全文、笔记和注释。CLI 不依赖 Zotero；skill 可以在 MCP 可用时同时使用 PaperQA2 和 Zotero。

安装：

```bash
pipx install zotero-mcp-server
```

确认命令：

```bash
zotero-mcp --help
```

Zotero 设置：

1. 安装并打开 Zotero 7+。
2. 打开 Zotero 本地 API。通常在 Settings / Advanced 相关设置里。
3. 保持 Zotero 运行。

如果本机 `localhost:23119` 返回 503，但 `127.0.0.1:23119` 正常，可以用启动器：

```bash
~/.local/pipx/venvs/zotero-mcp-server/bin/python /path/to/vet-agent/scripts/zotero_mcp_local.py serve
```

把 MCP server 注册到 Codex 或 Claude Code 时，命令使用上面这一行即可。注册完成后，agent 可以调用 Zotero MCP 工具搜索本地文献库。

导入 RIS 到 Zotero：

```bash
cd /path/to/vet-agent
curl -X POST http://127.0.0.1:23119/connector/import \
  -H "Content-Type: application/x-research-info-systems" \
  --data-binary @literature/cat-behavior.ris
```

重复导入会产生重复条目。需要去 Zotero 的 Duplicate Items 里合并，或导入到新 collection。

## 常见问题

`pqa: command not found`

确认 pipx 的 bin 目录在 PATH：

```bash
python3 -m pipx ensurepath
export PATH="$HOME/.local/bin:$PATH"
```

`ERROR: 还没设置 PQA_API_KEY`

确认 `.env` 存在，并且不是占位值：

```bash
cat .env
```

`papers/manifest.csv` 不存在

先生成本地语料：

```bash
cd literature && NCBI_EMAIL=you@example.com python3 harvest_pubmed.py
cd ..
UNPAYWALL_EMAIL=you@example.com python3 scripts/fetch_oa.py
```

`literature/cat-behavior.ris` 不存在

运行：

```bash
cd literature
NCBI_EMAIL=you@example.com python3 harvest_pubmed.py
```

Zotero MCP 连不上

确认 Zotero 正在运行、本地 API 已开启。再检查：

```bash
curl http://127.0.0.1:23119/api/
```

如果 `localhost` 失败、`127.0.0.1` 成功，使用 `scripts/zotero_mcp_local.py` 启动 MCP。

## 更新语料

修改 `literature/harvest_pubmed.py` 里的 `BUCKETS` 查询后重跑：

```bash
cd literature
NCBI_EMAIL=you@example.com python3 harvest_pubmed.py
cd ..
UNPAYWALL_EMAIL=you@example.com python3 scripts/fetch_oa.py
./scripts/index.sh
```

更新后检查：

```bash
python3 - <<'PY'
import csv
from pathlib import Path
root = Path(".")
missing = []
with (root / "papers/manifest.csv").open(newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if not (root / "papers" / row["file_location"]).exists():
            missing.append(row["file_location"])
print("missing", len(missing))
for name in missing:
    print(name)
PY
```

确认无缺失后再索引。
