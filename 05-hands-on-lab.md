# Segment 5 — 動手指引（Hands-on Lab）

> 對應課綱 Segment 5「Q&A + 動手指引」。本節 20 分鐘，把 Segment 1–3 學到的 MCP / agent 概念，落地成一個你自己帶回家能改造的最小專案。

---

## 📦 本節產出物

讀完本頁 + 跑完 L1，你會有：

1. 一個在本機跑起來的 MCP agent（Node.js 後端 + Python FastMCP + 極簡 HTML chat）
2. 一支**屬於你領域的**客製 MCP 工具（改 JSON 就好）
3. 理解「工具選擇 → 參數綁定 → LLM 摘要」這整條 agent 資料流
4. 兩關延伸作業（L2 / L3）帶回家自修

---

## 🚀 快速入門（5 分鐘）

### 先決條件

- Node.js ≥ 18（`node --version`）
- [uv](https://docs.astral.sh/uv/)（Python 套件管理）
- Claude API key 或連到 workshop 當場提供的本地端點

### 五步上線

```bash
# 1. 取得教材
git clone https://github.com/UDICatNCHU/nchu-mcp-workshop-2026
cd nchu-mcp-workshop-2026/mini-project

# 2. 設定 API key（或 workshop 端點；見下方「本地端點」）
cp .env.example .env
# 編輯 .env 填入 ANTHROPIC_API_KEY=...

# 3. 環境檢查（自動裝依賴 + 試啟動）
./setup.sh
# 看到 5/5 ✅ 代表 OK

# 4. 啟動
cd backend-node && npm start
# 看到 "→ Mini AI Assistant: http://localhost:3000"

# 5. 瀏覽器打開 http://localhost:3000 → 問「英文中心幾點開門？」
```

如果看到 AI 回答你 JSON 裡的開放時間 — 恭喜，**agent loop 已經在你本機跑起來了**。

---

## 🧪 Lab 路徑（三關）

| Lab | 主題 | 時長 | 何時做 | 手冊 |
|-----|------|------|--------|------|
| **L1** | 換 JSON 做你領域的助理（0 行 Python） | 40 分 | **課堂現場** | [L1-customize-your-data.md](./mini-project/docs/labs/L1-customize-your-data.md) |
| **L2** | 加一支有參數的搜尋工具 | 40 分 | 課堂或課後 | [L2-add-a-search-tool.md](./mini-project/docs/labs/L2-add-a-search-tool.md) |
| **L3** | 呼叫外部 API（async + XML + 錯誤處理） | 60 分 | **課後自修** | [L3-call-external-api.md](./mini-project/docs/labs/L3-call-external-api.md) |

> 📌 **課堂現場只要完成 L1**。L2 / L3 是帶回去繼續挑戰的 stretch goals。

---

## 🌐 Workshop 現場：連 NCHU 本地模型

若您在工作坊現場，講師會提供兩個本地端點，不需要 Claude API 費用：

```bash
# .env 修改為：
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://<workshop-server>:8000/v1    # Gemma 4 31B（agent 端）
OPENAI_API_KEY=dummy
OPENAI_MODEL=gemma-4
```

延伸閱讀：[mini-project/README.md](./mini-project/README.md)（Multi-Provider 章節）

想看 **Gemma 4 與 Claude 的品質 head-to-head**：
[2026-04-24 benchmark 報告](./mini-project/docs/benchmarks/2026-04-24-claude-vs-gemma4.md)

---

## 🏗 架構快速回顧

```
瀏覽器 chat UI (web/index.html)
        │ POST /chat { messages }
        ▼
 Node.js server.js  ──→  LLMClient (Claude / vLLM via openai SDK)
                          │
                          │  tool-calling loop
                          ▼
                        MCPClient (官方 MCP SDK)
                          │  stdio JSON-RPC
                          ▼
                        FastMCP server (Python)
                          │  讀 JSON / 打 API
                          ▼
                          data/*.json
```

對應 Segment 2/3 的動畫：
- [mcp-architecture-animation.html](./mcp-architecture-animation.html)
- [mcp-connection-animation.html](./mcp-connection-animation.html)
- [sonnet-flow-running-example.html](./sonnet-flow-running-example.html)

---

## 🐛 常見卡點

| 症狀 | 原因 | 解法 |
|------|------|------|
| `setup.sh` 卡在 Node 版本 | 本機 Node 16 | `nvm install 22 && nvm use 22` |
| port 3000 被占 | 有其他服務 | `PORT=3001 npm start` 或先 `lsof -i:3000` 找程式殺掉 |
| 瀏覽器問後沒反應 | API key 格式錯 | `.env` 裡 `sk-ant-…` 非 `sk-ant-...` placeholder |
| `No such file or directory: data/...json` | Python 從錯誤 cwd 啟動 | 確認 `config.json` 的 `--directory` 設成 `mcp-server-py` |
| `listToolsRequest` 後 Node 沒印 `✓` | MCP server 連線失敗 | `uv run python mcp-server-py/hello_tool.py` 直接試，看 stderr |

更多 pitfalls 在各 Lab 手冊結尾。

---

## 🧭 繼續延伸

- **Claude-vs-Gemma4 實驗**：一份可重現的 benchmark，驗證本地 31B 模型能否打平 Claude。
  → [docs/benchmarks/2026-04-24-claude-vs-gemma4.md](./mini-project/docs/benchmarks/2026-04-24-claude-vs-gemma4.md)
- **Coding agent 支援**：想用 AI 幫你寫 L2 的工具？Aider 接本地 Qwen 2.5-Coder 32B。
  → 參見 `infra/README.md`
- **模型比較腳本**：`scripts/compare-*.js` 可跑自動化對比（Claude vs 任意 OpenAI-兼容端點）。

---

## 🙋 提問

現場：直接舉手或在 Slack / Line group 發問。
課後：GitHub Issue → https://github.com/UDICatNCHU/nchu-mcp-workshop-2026/issues
