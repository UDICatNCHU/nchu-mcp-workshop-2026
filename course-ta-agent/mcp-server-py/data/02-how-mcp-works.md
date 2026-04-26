# 02-how-mcp-works.pptx


## Slide 1

How MCP Works
架構、協定與連線機制
MCP 入門工作坊  ｜  第二講（50 min）
國立中興大學  ·  AI 學伴系統實務案例

---

## Slide 2

本講大綱
01
通訊協定
REST vs JSON-RPC，為什麼 MCP 選 JSON-RPC
02
Server 生命週期
spawn → initialize → ready → shutdown
03
Tool 註冊與描述
JSON Schema、description 如何影響 LLM 選擇
04
Client 整合機制
工具清單如何注入 LLM 的 system prompt

---

## Slide 3

01
通訊協定
REST  vs  JSON-RPC

---

## Slide 4

REST vs JSON-RPC — 一張表看懂差異
面向 | REST | JSON-RPC
核心概念 | 資源（URL + HTTP 動詞） | 動作（method 欄位）
端點 | 每個資源一個 URL | 單一入口，靠 method 區分
傳輸層 | 綁定 HTTP | 不綁定（stdio / HTTP / WS）
語意 | CRUD 操作 | 呼叫函式
範例 | GET /books?keyword=AI | { method: "search_books" }
MCP 選 JSON-RPC 的原因：  傳輸層不綁 HTTP（可用 stdio），語意是「呼叫工具」而非「操作資源」

---

## Slide 5

REST — 每個資源有自己的路徑
// 搜尋書籍
GET /api/books?keyword=AI
Host: library.nchu.edu.tw
// 新增一本書
POST /api/books
Content-Type: application/json
{ "title": "深度學習入門", "author": "..." }
// 刪除
DELETE /api/books/123
// → 三個不同的 URL path + 三個不同的 HTTP method，必須透過 HTTP

---

## Slide 6

JSON-RPC — 單一入口，靠 method 區分
// 搜尋書籍
{ "jsonrpc": "2.0",
"method": "search_books",
"params": { "keyword": "AI" },
"id": 1 }
// 新增一本書 — 同一個入口，換 method 就好
{ "jsonrpc": "2.0",
"method": "create_book",
"params": { "title": "深度學習入門" },
"id": 2 }
// → 不需要 HTTP、不需要 URL — 可以透過 stdio 傳送！

---

## Slide 7

JSON-RPC 2.0 的三種訊息類型
Request
Client → Server
帶有 id 欄位
期待回應
{ method: "tools/call",
params: {...},
id: 1 }
Response
Server → Client
帶有相同 id
回傳 result 或 error
{ result: {
content: [...]
},
id: 1 }
Notification
任一方向
沒有 id 欄位
不期待回應（fire & forget）
{ method:
"notifications/
initialized" }

---

## Slide 8

02
Server 生命週期
spawn  →  initialize  →  ready  →  shutdown

---

## Slide 9

MCP Server 的四個階段
spawn
Client 啟動子程序
（Python / Node）
→
initialize
交換版本與
capabilities
→
ready
工具已註冊
開始接受請求
→
shutdown
Client 送出關閉
子程序結束
// config.json — 定義如何 spawn 每個 MCP Server
{ "mcpServers": {
"library": {
"command": "python",
"args": ["${NCHU_MODULES_PATH}/library/server.py"]
} } }
// → Python 子程序，透過 stdio 通訊；Client 啟動時自動 spawn

---

## Slide 10

initialize 握手 — 交換 capabilities
Client → Server
{ "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {}
  }, "id": 1 }
Server → Client
{ "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": { "listChanged": true }
    }
}, "id": 1 }
→
握手完成後，Client 送出 notification：
{ "method": "notifications/initialized" }
沒有 id → 單向通知，不期待回應。接下來 Client 呼叫 tools/list 取得工具清單。

---

## Slide 11

→  切換到互動動畫 Demo
mcp-connection-animation.html
展示重點：
1. spawn 子程序的實際流程（config.json → child_process.spawn）
2. initialize 握手的 JSON-RPC 訊息往返
3. notifications/initialized 通知
4. tools/list 載入工具清單
5. isConnected = true 的判定時機

---

## Slide 12

03
Tool 註冊與描述
JSON Schema  ·  description  ·  LLM 的唯一線索

---

## Slide 13

tools/list — Server 回傳工具定義
// Client 發送 tools/list request
{ "method": "tools/list", "id": 2 }
// Server 回傳所有可用工具（興大系統共 33 個）
{ "result": { "tools": [{
"name": "search_library_books",
"description": "搜尋中興大學圖書館的館藏書籍，支援關鍵字查詢",
"inputSchema": {
"type": "object",
"properties": {
"keyword": { "type": "string", "description": "搜尋關鍵字" }
}, "required": ["keyword"]
}
}, { "name": "get_department_courses", ... }, // ...共 33 個
] }, "id": 2 }

---

## Slide 14

每個 Tool 的三個關鍵欄位
name
工具的唯一識別名稱
LLM 在 tool_use 回傳時引用這個名稱
"search_library_books"
description
自然語言描述工具的用途
這是 LLM 判斷「要不要用」的最重要依據
"搜尋中興大學圖書館的館藏書籍"
inputSchema
JSON Schema 定義參數格式
LLM 據此產生正確的 arguments
{ type: "object", properties: {...} }

---

## Slide 15

description 寫得好不好，決定 LLM 選不選得對
✕  模糊的 description
"搜尋課程"
問題：有 8 個課程相關工具
（關鍵字 / 系所 / 教師 / 類型…）
LLM 分不清楚要用哪一個
✓  精確的 description
"依系所代碼查詢該系所的
 所有課程，回傳課程名稱、
 學分數、授課教師"
LLM 一看就知道：
「電機系有哪些課」→ 用這個
關鍵洞察
LLM 從來不會直接接觸 MCP Server。
它看到的就只有 name + description + inputSchema 這三個欄位的文字。
→ description 的品質 = 工具被正確使用的機率

---

## Slide 16

04
Client 整合機制
工具清單如何餵給 LLM

---

## Slide 17

工具清單 → LLM 的 tools 參數
33 個
MCP Servers
→
Client
收集工具清單
→
轉換 →
LLM API 呼叫
// raw-mcp-client.js — 呼叫 Claude API 時注入工具
const response = await anthropic.messages.create({
model: "claude-sonnet-4-20250514",
messages: conversationHistory,
tools: allMcpTools.map(t => ({
name: t.name,              // 來自 MCP Server
description: t.description, // 來自 MCP Server
input_schema: t.inputSchema // 來自 MCP Server
}))
});

---

## Slide 18

LLM 眼中的世界 — 只看到工具描述
LLM 看到的
Available tools:

1. search_library_books
   搜尋圖書館館藏書籍

2. get_department_courses
   依系所代碼查詢課程

3. search_teachers
   搜尋教師資訊與研究

... 共 33 個
LLM 看不到的
✕ Server 怎麼啟動的

✕ Server 用什麼語言

✕ 資料庫連線方式

✕ 網路拓撲

✕ 認證機制

✕ JSON-RPC 細節

---

## Slide 19

→  切換到互動動畫 Demo
mcp-architecture-animation.html
展示重點：
1. Host → Client → Server → Tool 四層架構的完整互動
2. 使用者提問後，LLM 如何透過 Client 呼叫 Server 的工具
3. 工具執行結果如何回傳給 LLM 整合成最終回覆
4. 對照剛剛學到的 JSON-RPC 格式，看實際訊息往返

---

## Slide 20

本講重點回顧
1
MCP 用 JSON-RPC 2.0 通訊 — 不綁 HTTP，支援 stdio / WebSocket
2
Server 生命週期四階段：spawn → initialize → ready → shutdown
3
每個 Tool 由 name / description / inputSchema 三個欄位定義
4
description 的品質直接決定 LLM 能否正確選用工具
5
Client 把所有工具定義轉換後注入 LLM API 的 tools 參數
下一講預告：Agentic Tool Loop — 讓 AI 自己決定用什麼工具、用幾次

---