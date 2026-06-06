<h1 align="center">Veterinary Behaviorist Skill</h1>

<p align="center">
  面向 Claude Code、Codex 和本地优先 AI 工具的自包含循证猫行为 consult skill。
</p>

<p align="center">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">中文</a>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: CC BY-NC-ND 4.0" src="https://img.shields.io/badge/License-CC_BY--NC--ND_4.0-lightgrey.svg"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.11+" src="https://img.shields.io/badge/Python-3.11%2B-blue.svg"></a>
  <a href="#原生-skill-模式"><img alt="Mode: local-first" src="https://img.shields.io/badge/Mode-local--first-lightgrey.svg"></a>
  <a href="#数据和版权"><img alt="Corpus: local only" src="https://img.shields.io/badge/Corpus-local_only-lightgrey.svg"></a>
</p>

`Veterinary Behaviorist Skill` 用来让 AI 编程助手按循证兽医行为 consult 流程处理猫和伴侣动物行为问题。它会引导 intake、检索本地兽医行为文献、可选使用 Zotero MCP 或 PaperQA2、有 web access 时搜索真实案例，并输出带引用的回答。

默认模式使用你已经在用的 AI 工具本身，不需要再接入另一个 LLM API。

## 这是什么

这个仓库发布的是一个自包含 skill：

```text
skill/veterinary-behaviorist/
```

它不是单独的聊天机器人、网页应用、托管 API 或另一个需要启动的 agent 服务。

你把这个 skill 文件夹安装进 Claude Code、Codex 或其他兼容 AI 工具。调用时，当前 AI 助手会读取 `SKILL.md`、追问必要背景、运行 skill 里的脚本，并生成最终 consult。

## Agent 和 Skill 的区别

**AI agent / runtime** 是你正在使用的助手，比如 Claude Code 或 Codex。

**Skill** 是一包说明、脚本、配置和资源，用来教这个助手执行特定工作流。

本项目现在是 skill，不再按单独 agent 维护。当前 AI 助手只有在使用这个 skill 时，才按兽医行为 consult 流程工作。

## 最后会得到什么

完整 case 会输出一份带引用的兽医行为 consult：

```text
已确认的 case summary
结论
医学优先分诊
最可能诊断和鉴别诊断
安全和管理方案
行为改变方案
长期相处策略
科学文献证据
真实案例经验 / anecdotal patterns
局限和升级条件
```

如果用户描述太模糊，skill 不应该直接给诊断。例如用户只说：

```text
我家猫突然攻击我了。
```

AI 应该先问清最小背景：动物信息、医学背景、事件经过、伤害严重程度、发生模式、触发因素、家庭安全、之前怎么处理、用户目标和限制。用户回答不完整时，要继续追问缺失信息。信息足够后，AI 先复述 case summary，让用户确认，再检索证据并输出完整 consult。

如果有紧急医学或安全风险，先给即时安全分诊，再继续补全 intake。

## 原生 Skill 模式

原生 Skill 模式是默认模式，不需要另一个 LLM API。

当前 AI 工具会：

1. 读取 `skill/veterinary-behaviorist/SKILL.md`。
2. 执行 intake，并确认 case summary。
3. 用 skill 内的 `scripts/search_corpus.py` 检索本地证据。
4. 如果用户配置了 Zotero MCP，可选搜索 Zotero 本地库。
5. 有 web access 时，在科学文献检索后搜索相似真实案例。
6. 用自己的模型写回答，并且只引用检索到的来源。

PaperQA2 是可选项。只有当你想使用独立文献 QA 引擎，并且已经有 OpenAI-compatible API key 时才需要。

## 安装

克隆仓库：

```bash
git clone https://github.com/agentenatalie/cat-behavior-vet-agent.git
cd cat-behavior-vet-agent
```

安装为 Codex skill：

```bash
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skill/veterinary-behaviorist" ~/.codex/skills/veterinary-behaviorist
```

安装为 Claude Code skill：

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skill/veterinary-behaviorist" ~/.claude/skills/veterinary-behaviorist
```

也可以只复制 skill 文件夹：

```bash
cp -R skill/veterinary-behaviorist ~/.codex/skills/veterinary-behaviorist
```

想让仓库更新立即影响已安装 skill，就用软链。

## 调用方式

不同 AI 工具的调用语法可能不同。明确写出 skill 名称即可：

```text
Use $veterinary-behaviorist to assess this case.
```

或：

```text
/veterinary-behaviorist
我家 4 岁已绝育室内猫看到窗外野猫后突然攻击我的腿，应该怎么办？
```

正常使用时，用户不需要手动运行 `search_corpus.py`。当前 AI 助手应该在 intake 完成后自己运行 skill 内的检索命令。

## 生成本地文献语料

公开仓库不包含论文摘要正文、全文、PDF、RIS 文件或向量索引。需要在本地生成：

```bash
cd skill/veterinary-behaviorist
NCBI_EMAIL=you@example.com python3 literature/harvest_pubmed.py
UNPAYWALL_EMAIL=you@example.com python3 scripts/fetch_oa.py
```

测试检索：

```bash
python3 scripts/search_corpus.py "owner-directed aggression in cats" -n 5
python3 scripts/search_corpus.py "cat redirected aggression outdoor cat window" -n 5
```

本地生成文件：

```text
skill/veterinary-behaviorist/literature/cat-behavior.ris
skill/veterinary-behaviorist/papers/PMID*.abstract.txt
skill/veterinary-behaviorist/papers/PMID*.fulltext.txt
skill/veterinary-behaviorist/papers/PMID*.pdf
skill/veterinary-behaviorist/papers/manifest.csv
skill/veterinary-behaviorist/.pqa_index/
```

这些文件只留在本地，并被 Git 忽略。

## Paper 是怎么找到的

默认语料不需要用户手动 Web Research。

skill 使用脚本化 discovery 流程：

1. `literature/harvest_pubmed.py` 运行预设 PubMed E-utilities 查询，覆盖 feline stress、fear、anxiety、aggression、bite 等猫行为主题。
2. 脚本在本地写入 `literature/cat-behavior.ris`。
3. `scripts/fetch_oa.py` 读取 RIS，并按顺序尝试：
   - 已存在的本地 `papers/PMID<pmid>.pdf`
   - Unpaywall 开放获取 PDF
   - Europe PMC 开放获取 full-text XML
   - PubMed 摘要文本 fallback
4. 脚本写入 `papers/manifest.csv`，供本地检索使用。

只有这些情况需要人工补充研究：扩展语料、加入某篇你合法获得的 PDF、查找缺失 paper 的 PMID/DOI。

如果你有合法获取的论文 PDF，把它按 PMID 命名放到本地 skill 语料里：

```text
skill/veterinary-behaviorist/papers/PMID29099247.pdf
```

然后刷新：

```bash
cd skill/veterinary-behaviorist
python3 scripts/fetch_oa.py
```

## 组件配置

| 组件 | 是否必需 | 下载 / 安装 | 配置 |
| --- | --- | --- | --- |
| Python 3.11+ | 必需 | <https://www.python.org/downloads/> | 所有脚本都用 Python。 |
| PubMed E-utilities | 生成语料时必需 | <https://www.ncbi.nlm.nih.gov/books/NBK25501/> | 运行 `harvest_pubmed.py` 时设置 `NCBI_EMAIL=you@example.com`。 |
| Unpaywall API | 查找 OA 来源时必需 | <https://unpaywall.org/products/api> | 运行 `fetch_oa.py` 时设置 `UNPAYWALL_EMAIL=you@example.com`。 |
| Europe PMC REST API | 自动使用 | <https://europepmc.org/RestfulWebService> | 当前脚本不需要 key。 |
| Zotero 7+ | 可选 | <https://www.zotero.org/download/> | 只有想让 AI 读取你的 Zotero 本地库、笔记、注释或 PDF 时才安装。 |
| Zotero MCP server | 可选 | <https://pypi.org/project/zotero-mcp-server/> | `pipx install zotero-mcp-server`，并保持 Zotero 运行、本地 API 开启。 |
| PaperQA2 / `paper-qa` | 可选 | <https://github.com/Future-House/paper-qa> | 需要在 `.env` 里配置 OpenAI-compatible API key。 |
| pipx | 可选 | <https://pipx.pypa.io/stable/installation/> | 安装 PaperQA2 和 Zotero MCP 会比较方便。 |
| sentence-transformers | 可选 | <https://www.sbert.net/docs/installation.html> | 使用 PaperQA2 本地 embedding 时注入。 |
| LiteLLM provider 配置 | 可选 | <https://docs.litellm.ai/docs/providers> | 如果换 PaperQA2 模型或 provider，修改 `settings.json`。 |
| Web access | 可选 | 取决于你的 AI 工具 | 文献检索后，用来查找相似公开真实案例。 |

## 可选：PaperQA2

安装：

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install "paper-qa>=5"
pipx inject paper-qa sentence-transformers
```

配置：

```bash
cd skill/veterinary-behaviorist
cp .env.example .env
```

编辑 `.env`：

```bash
PQA_API_KEY=your-openai-compatible-provider-key
UNPAYWALL_EMAIL=you@example.com
```

索引和提问：

```bash
./scripts/index.sh
./scripts/consult.sh "What are reliable objective indicators of stress in cats?"
```

PaperQA2 默认配置在 `skill/veterinary-behaviorist/settings.json`。如果要换模型或 provider，修改里面的 `llm`、`summary_llm`、model ID、API base 和 provider 配置。建议保留 `api_key` 为 `os.environ/PQA_API_KEY`。

## 可选：Zotero MCP

Zotero 不是必需项。只有你已经用 Zotero 管理论文，或者想让 AI 搜索你的本地文献库时才需要。

安装：

```bash
pipx install zotero-mcp-server
```

确认 Zotero 7+ 已安装、正在运行，并开启本地 API。

如果 `localhost:23119` 失败但 `127.0.0.1:23119` 正常，可以用 skill 内的启动器：

```bash
~/.local/pipx/venvs/zotero-mcp-server/bin/python skill/veterinary-behaviorist/scripts/zotero_mcp_local.py serve
```

把生成的 RIS 导入 Zotero：

```bash
cd skill/veterinary-behaviorist
curl -X POST http://127.0.0.1:23119/connector/import \
  -H "Content-Type: application/x-research-info-systems" \
  --data-binary @literature/cat-behavior.ris
```

重复导入可能产生重复条目。可以用 Zotero 的 Duplicate Items 视图合并，或导入到新 collection。

## 真实案例 Web 校验

Web search 不是默认找论文的方法。它是 consult 的第二阶段。

intake 和科学文献检索完成后，AI 可以搜索公开 web source，查找相似真实案例和结果。这一步用来了解实践模式：别人试过什么、什么有帮助、什么失败、案例背景是否真的相似。

真实案例必须标注为 anecdotal。它不能覆盖兽医文献、医学分诊和安全规则。

## 仓库结构

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

## 数据和版权

仓库只包含 skill 指令、脚本、配置模板和公开 provenance 元数据。

仓库不包含：

- `.env` 文件或 API key
- PaperQA2 向量索引
- 生成的摘要、全文、PDF 或 `manifest.csv`
- 生成的 RIS 文件
- Zotero 本地库、笔记、注释或附件

paper discovery 使用官方公开服务：

- PubMed E-utilities：<https://www.ncbi.nlm.nih.gov/books/NBK25501/>
- Unpaywall API：<https://unpaywall.org/products/api>
- Europe PMC REST API：<https://europepmc.org/RestfulWebService>

PubMed 可访问不等于每篇摘要都可以再分发。开放获取检索结果也不代表每篇 PDF 都有相同许可证。生成的语料默认只保留在使用者本机，除非逐篇确认允许再分发。

## Attribution

本项目没有捆绑、复制或再分发 Academic Research Suite / Academic Research Skill 的文件、prompt、template 或 agent definition。

它使用的是通用本地优先研究模式：脚本化 discovery、本地语料生成、本地检索、可选 reference manager 集成、由当前 AI 工具做带引用 synthesis。本仓库中的实现和兽医行为工作流是为这个 skill 单独维护的。

本项目与 NCBI、NLM、PubMed、Unpaywall、Europe PMC、Zotero、PaperQA2、DACVB、ECAWBM 均无隶属关系。

## 安全说明

这个 skill 用于教育和决策辅助。它不是兽医诊断服务，不能替代线下兽医或 board-certified veterinary behaviorist。

行为变化可能来自疼痛、疾病、药物影响、神经问题或环境压力。涉及受伤、攻击升级、突然行为变化、严重 distress 或动物福利风险时，应寻求线下兽医帮助。

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。

适合贡献的方向：

- 更好的 PubMed query buckets
- 更好的本地检索排序
- 其他物种或行为领域
- 更完整的 Zotero MCP 文档
- 语料生成和本地检索测试

## License

本项目使用 [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](LICENSE)。

你可以在非商业场景下署名分享未修改版本。商业使用和分发修改版本需要另行获得许可。

因为该许可证包含 NonCommercial 和 NoDerivatives 限制，本项目是 public-source 项目，不是 OSI 意义上的 open-source 项目。
