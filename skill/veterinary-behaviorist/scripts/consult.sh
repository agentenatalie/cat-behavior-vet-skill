#!/usr/bin/env bash
# 兽医行为 consult skill 的可选文献问答内核 (PaperQA2)
# 用法: ./scripts/consult.sh "猫的压力行为有哪些可靠的客观指标?"
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"

# 载入 .env (PQA_API_KEY 等)
if [ -f .env ]; then set -a; . ./.env; set +a; fi
PQA_API_KEY="${PQA_API_KEY:-${OPENAI_API_KEY:-}}"
if [ -z "${PQA_API_KEY:-}" ] || [ "${PQA_API_KEY}" = "put-your-openai-compatible-api-key-here" ]; then
  echo "ERROR: 还没设置 PQA_API_KEY。请 cp .env.example .env 并填入 OpenAI-compatible provider 的 API key。" >&2
  exit 1
fi
# litellm 走 OpenAI 兼容 provider，用同一个 key
export PQA_API_KEY
export OPENAI_API_KEY="$PQA_API_KEY"
export PATH="$HOME/.local/bin:$PATH"

if [ "$#" -lt 1 ]; then echo "用法: $0 \"你的问题\"" >&2; exit 1; fi
exec pqa --settings "$HERE/settings" ask "$*"
