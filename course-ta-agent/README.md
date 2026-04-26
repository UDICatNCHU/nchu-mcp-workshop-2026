# Course TA Agent

NCHU MCP Workshop 2026 課程小助教 —— 學員可直接問課程概念、Lab 操作、mini-project 程式碼。

## 架構

```
[Browser] ⇅ [Express + Claude] ⇅ stdio JSON-RPC ⇅ [FastMCP — 4 tools]
                                                          ↓
                                         data/*.md（投影片 + 手冊抽出）
                                         ../mini-project/**（沙盒讀檔）
```

刻意 mirror `../mini-project/` 三層結構 —— 工作坊講完 agent loop 後，學員可以打開 `backend-node/llm-client.js`，看到跟 Segment 4 投影片裡完全一樣的 20 行核心。

## 4 支 MCP Tool

| Tool | 用途 | 範例查詢 |
|------|------|---------|
| `get_segment(num)` | 取課程某一段（1–5）內容 | 「Segment 2 在講什麼？」 |
| `search_course(query, limit)` | 全文關鍵字搜尋 | 「N×M 痛點是什麼？」 |
| `get_lab_handout(lab)` | Lab 手冊原文 | 「L1 Step 3 docstring 怎麼改？」 |
| `read_mini_project_file(path)` | 讀 mini-project source code（沙盒）| 「llm-client.js 那個 for-loop 解釋」 |

## 快速啟動

> 行前一次：`uv` + Node ≥ 18 + Anthropic API key

```bash
# 1. 抽課程內容（pptx → md），需在 repo root 執行
cd ..
uv run --with python-pptx python3 tools/extract-pptx-to-md.py

# 2. 回到 course-ta-agent，建 .env
cd course-ta-agent
cp .env.example .env
vim .env                       # 填 ANTHROPIC_API_KEY

# 3. 環境預檢
./setup.sh                     # 5/5 ✅

# 4. 啟動
cd backend-node && npm start
# → Course TA Agent: http://localhost:3001
```

## 對學員開放（cloudflared tunnel）

```bash
# 安裝 cloudflared 後：
cloudflared tunnel --url http://localhost:3001
# → https://random.trycloudflare.com  ← 投影 / 寫白板給學員
```

## 跟 mini-project 的關係

| 檔案 | 跟 mini-project 一樣？ |
|------|----------------------|
| `backend-node/mcp-client.js`        | 100% 一樣 |
| `backend-node/llm-client.js`        | 99%（多 1 個 system prompt 參數） |
| `backend-node/llm-client-openai.js` | 99%（同上） |
| `backend-node/server.js`            | 90%（注入 system prompt、port 預設 3001） |
| `backend-node/package.json`         | 90%（改 name） |
| `web/index.html`                    | 70%（重新 brand + 範例題目） |
| `setup.sh`                          | 80%（檢查項目調整） |
| `mcp-server-py/course_tool.py`      | 全新（4 tools） |
| `config.json`                       | 全新（1 server 註冊） |
| `mcp-server-py/data/*.md`           | 全新（由 extract script 產） |

## 維護

每次更新 .pptx 後：
```bash
uv run --with python-pptx python3 tools/extract-pptx-to-md.py
# 重啟 npm start（FastMCP 在 startup 時讀 data/）
```
