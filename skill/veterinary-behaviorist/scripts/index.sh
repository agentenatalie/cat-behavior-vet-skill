#!/usr/bin/env bash
# 重建/更新 PaperQA2 的本地索引 (本地 embedding，不需要 LLM key 即可索引已带 manifest 的 PDF)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"
if [ -f .env ]; then set -a; . ./.env; set +a; fi
PQA_API_KEY="${PQA_API_KEY:-${OPENAI_API_KEY:-unused-for-indexing}}"
export PQA_API_KEY
export OPENAI_API_KEY="$PQA_API_KEY"
export PATH="$HOME/.local/bin:$PATH"
exec pqa --settings "$HERE/settings" index "$HERE/papers"
