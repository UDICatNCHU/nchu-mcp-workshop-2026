# Mini AI Assistant — 教學範例

這是 **中興大學 AiLearningMate** 正式版的極簡抽取版，用來教學「LLM + MCP tool-calling + Web UI」的最小整合模式。

**整份專案約 300 行程式碼**，可在一堂課內讀完並親手擴充成自己的應用。

## 架構

```
┌────────────┐   POST /chat    ┌──────────────┐   Claude API   ┌──────────────┐
│  瀏覽器    │ ──────────────> │  Express     │ ─────────────> │  Claude      │
│  (web/)    │ <────────────── │  (backend-   │ <───────────── │  (Anthropic) │
└────────────┘   {reply, ...}  │   node/)     │   tool_use?    └──────────────┘
                                │              │
                                │  MCPClient   │   stdio JSON-RPC
                                │              │ ──────────────────┐
                                └──────────────┘                   │
                                                                   ▼
                                                         ┌──────────────────┐
                                                         │  FastMCP server  │
                                                         │  (mcp-server-py/)│
                                                         │  讀 JSON 回傳    │
                                                         └──────────────────┘
```

三個模組，各自獨立可換：
| 模組 | 語言 | 檔案 | 職責 |
|------|------|------|------|
| MCP 工具伺服器 | Python | `mcp-server-py/hello_tool.py` | 定義工具、回傳資料 |
| Web 後端 | Node.js | `backend-node/*.js` | 轉接 LLM、管理 MCP client |
| 前端 | HTML + vanilla JS | `web/index.html` | 收發對話 |

## 快速啟動（4 步）

> 先確認有安裝 [uv](https://docs.astral.sh/uv/) 和 Node.js 18+。

```bash
# 1. 安裝 Python 端（會自動建立 .venv）
cd mcp-server-py && uv sync && cd ..

# 2. 安裝 Node 端
cd backend-node && npm install && cd ..

# 3. 設定 API Key
cp .env.example .env
# 編輯 .env，填入從 https://console.anthropic.com/ 取得的 key

# 4. 啟動（會同時啟動 Python MCP server 做為子程序）
cd backend-node && npm start
```

瀏覽器打開 `http://localhost:3000`，輸入 `英文中心幾點開門？` 試試。

## 核心程式路徑

使用者送訊息後，資料流如下：

1. `web/index.html` 的 `send()` → `fetch('/chat', {messages})`
2. `backend-node/server.js` 的 `POST /chat` → `llm.chat(messages)`
3. `backend-node/llm-client.js` 的 `chat()`：呼叫 Claude API
4. Claude 回覆 `stop_reason === 'tool_use'` → 從 `mcp-client.js` 呼叫工具
5. `backend-node/mcp-client.js` 的 `callTool()` → 透過 stdio JSON-RPC 呼叫 Python
6. `mcp-server-py/hello_tool.py` 的 `get_english_center_info()` 回傳 JSON 字串
7. 結果塞回 `messages` 陣列，再呼叫一次 Claude API 請它總結
8. Claude 回覆 `stop_reason === 'end_turn'` → 取出 text，回傳給前端

**最重要的 20 行**：`llm-client.js:17-54` 的 tool-calling 迴圈。這是整個系統的靈魂。

## 如何做出你自己的 AI 助理

5 步驟：

### 1. 複製一支工具
```bash
cp mcp-server-py/hello_tool.py mcp-server-py/my_tool.py
```

### 2. 改工具
編輯 `my_tool.py`：
- 改 `FastMCP("hello_tool")` → `FastMCP("my_tool")`
- 改 `@mcp.tool()` 下的函式名稱與 docstring
- 改 `INFO = _load_data()` 與相關 JSON 檔，或直接把 JSON 換成你自己的邏輯（呼叫 API、查資料庫等）

**docstring 會變成 LLM 看到的工具說明**，寫清楚呼叫情境很重要。

### 3. 加進 config.json
```json
{
  "mcpServers": {
    "hello_tool": { ... },
    "my_tool": {
      "command": "uv",
      "args": ["--directory", "mcp-server-py", "run", "python", "my_tool.py"]
    }
  }
}
```

### 4. 重啟
```bash
# Ctrl-C 停掉 node，再 npm start
```
啟動 log 會印出 `✓ my_tool → ...`，代表工具已被 Claude 看見。

### 5. 測試
在網頁問相關問題 → Claude 會自己決定是否呼叫你的新工具。

---

## 參考：去掉了什麼？

本教學版相較於正式版，**刻意砍掉**：
- SSE 串流、Markdown 渲染、語音輸入
- MongoDB 持久化對話
- 多模型 fallback（Gemini / ChatGPT / Ollama / OpenRouter）
- SSO、速率限制、Turnstile、admin dashboard
- PM2 cluster、Redis 快取、i18n、Chrome extension
- 其餘 40 支 MCP server、~238 支工具

這些在正式版 `claude-mcp-project/` + `library/` 都可以看到；**本教學版的目的只是給你最短的入門路徑**。
