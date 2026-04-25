#!/usr/bin/env bash
# setup.sh — 工作坊環境預檢腳本
# 用法：./setup.sh   （在 mini-project/ 根目錄執行）
#
# 本腳本會：
#   1. 檢查必要工具（Node ≥18、npm、uv、python3.11+）
#   2. 檢查專案檔案完整
#   3. 檢查 .env 與 ANTHROPIC_API_KEY
#   4. 自動安裝 npm / uv 依賴（若尚未安裝）
#   5. 試啟動 server 一次，確認 MCP 連線與 port 3000 可用
#
# 全部 ✅ = 上課可直接進入 hands-on。有任何 ❌ = 請先處理再重跑。

set +e
cd "$(dirname "$0")"

# ── 輔助函式 ─────────────────────────────────────────
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
PASS=0; FAIL=0; WARN=0

ok()      { echo -e "${GREEN}✅${NC} $1"; PASS=$((PASS+1)); }
bad()     { echo -e "${RED}❌${NC} $1"; [ -n "$2" ] && echo "     → $2"; FAIL=$((FAIL+1)); }
warn()    { echo -e "${YELLOW}⚠${NC}  $1"; [ -n "$2" ] && echo "     → $2"; WARN=$((WARN+1)); }
section() { echo ""; echo -e "${BLUE}── $1 ──${NC}"; }

cleanup() {
  if [ -n "${BOOT_PID:-}" ]; then
    kill "$BOOT_PID" 2>/dev/null
    wait "$BOOT_PID" 2>/dev/null
  fi
  rm -f /tmp/mini-setup-boot.log
  echo ""
  echo "────────────────────────────────────────"
  echo -e "結果：${GREEN}$PASS ✅${NC}   ${YELLOW}$WARN ⚠${NC}   ${RED}$FAIL ❌${NC}"
  if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}環境尚未就緒，請修正 ❌ 後重跑 ./setup.sh${NC}"
    exit 1
  fi
  echo -e "${GREEN}環境 OK！上課時直接 cd backend-node && npm start${NC}"
}
trap cleanup EXIT

# ── 1. 基本工具 ─────────────────────────────────────
section "1/5 基本工具"

if command -v node >/dev/null 2>&1; then
  NODE_VER=$(node --version | sed 's/v//')
  NODE_MAJOR=${NODE_VER%%.*}
  if [ "$NODE_MAJOR" -ge 18 ]; then
    ok "Node v$NODE_VER"
  else
    bad "Node v$NODE_VER（需 ≥18）" "nvm install 22 && nvm use 22"
  fi
else
  bad "node 未安裝" "https://nodejs.org/ 或 nvm"
fi

if command -v npm >/dev/null 2>&1; then
  ok "npm $(npm --version)"
else
  bad "npm 未安裝"
fi

if command -v uv >/dev/null 2>&1; then
  ok "uv $(uv --version 2>&1 | awk '{print $2}')"
else
  bad "uv 未安裝" "curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

if command -v python3 >/dev/null 2>&1; then
  PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
  PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
  if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 11 ]; then
    ok "Python $PY_VER"
  else
    warn "Python $PY_VER < 3.11" "uv sync 會嘗試自動安裝符合版本"
  fi
else
  warn "python3 未直接安裝" "uv 會自動解決"
fi

# ── 2. 專案檔案完整性 ────────────────────────────
section "2/5 專案結構"

MISSING=0
for f in config.json backend-node/package.json backend-node/server.js \
         backend-node/mcp-client.js backend-node/llm-client.js \
         mcp-server-py/pyproject.toml mcp-server-py/hello_tool.py \
         mcp-server-py/data/english_center.json web/index.html; do
  if [ -f "$f" ]; then
    :  # 靜默通過
  else
    bad "$f 不存在"
    MISSING=$((MISSING+1))
  fi
done
[ "$MISSING" -eq 0 ] && ok "9 個核心檔案齊全"

# ── 3. API Key 與 .env ──────────────────────────
section "3/5 API Key 與 .env"

if [ -f .env ]; then
  ok ".env 檔已建立"
  if grep -qE "^ANTHROPIC_API_KEY=sk-ant-[A-Za-z0-9_-]{20,}" .env; then
    ok "ANTHROPIC_API_KEY 格式正確"
  elif grep -q "^ANTHROPIC_API_KEY=sk-ant-\.\.\." .env; then
    bad ".env 的 ANTHROPIC_API_KEY 還是範例 placeholder" "編輯 .env 填入真實 key"
  elif grep -q "^ANTHROPIC_API_KEY=" .env; then
    warn ".env 的 ANTHROPIC_API_KEY 格式看起來異常" "key 應以 sk-ant- 開頭"
  else
    bad ".env 沒有 ANTHROPIC_API_KEY 這行"
  fi
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  warn ".env 不存在（但環境變數已設）" "建議 cp .env.example .env"
else
  bad ".env 不存在且 ANTHROPIC_API_KEY 環境變數未設" "cp .env.example .env 後編輯填 key"
fi

# ── 4. 依賴安裝 ─────────────────────────────────
section "4/5 依賴安裝"

if [ -d backend-node/node_modules ]; then
  ok "Node 依賴已安裝"
else
  echo "   首次執行，安裝 Node 依賴 (約 30 秒)…"
  if (cd backend-node && npm install >/tmp/mini-npm.log 2>&1); then
    ok "npm install 完成"
  else
    bad "npm install 失敗" "看 /tmp/mini-npm.log"
  fi
fi

if [ -d mcp-server-py/.venv ]; then
  ok "Python 依賴已安裝"
else
  echo "   首次執行，安裝 Python 依賴 (約 30 秒)…"
  if (cd mcp-server-py && uv sync >/tmp/mini-uv.log 2>&1); then
    ok "uv sync 完成"
  else
    bad "uv sync 失敗" "看 /tmp/mini-uv.log"
  fi
fi

# ── 5. Boot 驗證 ────────────────────────────────
section "5/5 啟動驗證 (6 秒)"

# 檢查 port 3000 是否被占用
if command -v lsof >/dev/null 2>&1 && lsof -i :3000 >/dev/null 2>&1; then
  bad "port 3000 已被其他程式佔用" "lsof -i :3000 查找並關掉"
elif [ "$FAIL" -gt 0 ]; then
  warn "跳過啟動驗證" "前面有項目未通過，先修好再跑"
else
  (cd backend-node && node server.js >/tmp/mini-setup-boot.log 2>&1) &
  BOOT_PID=$!
  sleep 6

  if grep -q "Mini AI Assistant:" /tmp/mini-setup-boot.log 2>/dev/null; then
    ok "Express server 啟動"
    if grep -q "✓ hello_tool" /tmp/mini-setup-boot.log; then
      ok "MCP server 連線成功（hello_tool 工具已載入）"
    else
      bad "MCP server 連線失敗" "cat /tmp/mini-setup-boot.log"
    fi
  else
    bad "server 無法啟動" "cat /tmp/mini-setup-boot.log"
  fi
fi
