# MCP 入門工作坊 — 課堂筆記

> 國立中興大學 · AI 學伴系統實務案例  
> 對象：大專院校教師 ｜ 時間：3 小時

---

## 第一段：Why MCP（50 min）

### 1.1 LLM 的能力與天花板

**LLM 擅長的事：** 語言理解與生成、推理與分析、程式碼生成、知識回答。這些能力來自訓練階段學到的「靜態知識」。

**LLM 的天花板：**

| 限制 | 說明 |
|------|------|
| 知識截止日 | 訓練資料有日期上限，無法回答「今天」的事 |
| 沒有私有資料 | 不知道你的課表、圖書館藏書、校內公告 |
| 無法執行動作 | 不能幫你查詢系統、預約空間、操作 API |
| 會幻覺 | 不確定時仍自信回答，編造看起來合理的資訊 |

**核心問題：** 如何讓 LLM 存取「外部世界」的資訊與功能？

### 1.2 策略 A：RAG（Retrieval-Augmented Generation）

**概念：** 使用者提問 → 向量化 → 向量資料庫搜尋 → 取回文件片段 → 注入 Prompt → LLM 回答

```python
# RAG 概念程式碼
query = "中興大學圖書館有什麼 AI 相關的書？"
embedding = embed_model.encode(query)
relevant_docs = vector_db.search(embedding, top_k=5)
prompt = f"根據以下資料回答問題:\n{relevant_docs}\n\n問題：{query}"
response = llm.generate(prompt)
```

**優點：** 降低幻覺（有引用來源）、存取私有資料、不需重新訓練模型  
**局限：** 只能「讀」不能「做」、檢索品質依賴 embedding 與切塊策略、結構化查詢支援差

### 1.3 策略 B：Tool Use（Function Calling）

**概念：** 使用者提問 → LLM 分析選擇工具 → 呼叫外部 API → 取得結果 → LLM 整合回覆

**關鍵差異：** LLM 自己決定「要不要用工具」以及「用哪一個」。

```javascript
// Claude API 的 Tool Use 定義
tools: [{
  name: "search_library_books",
  description: "搜尋圖書館館藏",
  input_schema: {
    type: "object",
    properties: { keyword: { type: "string" } }
  }
}]

// LLM 回傳的 tool_use block
{ type: "tool_use",
  name: "search_library_books",
  input: { keyword: "人工智慧" } }
```

**各家 API 格式不同** — Claude 用 `tool_use` / `input_schema`，ChatGPT 用 `tool_calls` / `parameters`（且 arguments 是字串非物件）。

**優點：** 能「做事」、結構化輸入輸出  
**局限：** 每家 API 格式不同（vendor lock-in）、工具要寫死在應用程式裡

### 1.4 Tool Use 的 N×M 痛點

4 個 AI 應用 × 4 個資料源 = 16 個 connector，每個格式各不相同。

### 1.5 策略 C：MCP — 統一協定

MCP 將 N×M 問題簡化為 N+M：所有 AI 應用透過統一的 JSON-RPC 協定與所有資料源溝通。

### 1.6 三者深入比較

| 面向 | RAG | Tool Use | MCP |
|------|-----|----------|-----|
| 核心能力 | 讀取文件 | 執行動作 | 執行動作（標準化） |
| 整合成本 | 需向量化管線 | 每個 App × 每個工具 | N+M（統一協定） |
| 即時性 | 取決於索引更新頻率 | 即時呼叫 | 即時呼叫 |
| 結構化查詢 | 弱 | 強 | 強 |
| Vendor Lock-in | 低 | 高（格式各異） | 低（統一協定） |
| 適用場景 | 知識庫問答、文件搜尋 | 單一應用整合 | 多工具跨應用 |

> **三者可混用：** 實務上常見 RAG 處理知識庫 + MCP 處理動作型需求，並非互斥。

<!-- 
TODO: 討論 — 這張比較表要不要再加更多面向？
例如：部署複雜度、維護成本、學習曲線、社群生態？
-->

### 1.7 MCP 核心概念

四大角色：

| 角色 | 說明 | 興大案例 |
|------|------|---------|
| **Host** | 使用者操作的應用程式 | 瀏覽器前端（chat interface） |
| **Client** | Host 內建的 MCP 通訊模組 | `raw-mcp-client.js` |
| **Server** | 獨立程序，提供特定能力 | Python 腳本（library/server.py） |
| **Tool** | Server 註冊的具體操作 | `search_library_books` 等 33 個工具 |

### 1.8 MCP 通訊協定

MCP 採用 **JSON-RPC 2.0**，所有訊息格式統一：

```json
// Request
{ "jsonrpc": "2.0", "method": "tools/call",
  "params": { "name": "search_books", "arguments": {"keyword": "AI"} },
  "id": 1 }

// Response
{ "jsonrpc": "2.0",
  "result": { "content": [{"type": "text", "text": "..."}] },
  "id": 1 }
```

### 1.9 興大 AI 學伴案例引子

33 個 MCP 工具、9 大分類，涵蓋圖書館查詢、課程查詢、校園活動、法規查詢等。

---

## 第二段：How MCP Works（50 min）

### 2.1 REST vs JSON-RPC

| 面向 | REST | JSON-RPC |
|------|------|----------|
| 核心概念 | 資源（URL + HTTP 動詞） | 動作（method 欄位） |
| 端點 | 每個資源一個 URL | 單一入口，靠 method 區分 |
| 傳輸層 | 綁定 HTTP | 不綁定（stdio / HTTP / WS） |
| 語意 | CRUD 操作 | 呼叫函式 |
| 範例 | `GET /books?keyword=AI` | `{ method: "search_books" }` |

**MCP 選 JSON-RPC 的原因：** 傳輸層不綁 HTTP（可用 stdio），語意是「呼叫工具」而非「操作資源」。

```javascript
// REST — 三個不同的 URL path + HTTP method
GET  /api/books?keyword=AI
POST /api/books  { "title": "深度學習入門" }
DELETE /api/books/123

// JSON-RPC — 同一個入口，換 method 就好
{ "jsonrpc": "2.0", "method": "search_books", "params": { "keyword": "AI" }, "id": 1 }
{ "jsonrpc": "2.0", "method": "create_book", "params": { "title": "深度學習入門" }, "id": 2 }
// → 不需要 HTTP、不需要 URL — 可以透過 stdio 傳送！
```

### 2.2 JSON-RPC 2.0 的三種訊息類型

| 類型 | 方向 | 特徵 | 範例 |
|------|------|------|------|
| **Request** | Client → Server | 帶 `id`，期待回應 | `{ method: "tools/call", id: 1 }` |
| **Response** | Server → Client | 帶相同 `id`，回傳 result/error | `{ result: {...}, id: 1 }` |
| **Notification** | 任一方向 | 沒有 `id`，fire & forget | `{ method: "notifications/initialized" }` |

### 2.3 Server 生命週期

四個階段：**spawn → initialize → ready → shutdown**

```json
// config.json — 定義如何 spawn 每個 MCP Server
{ "mcpServers": {
    "library": {
      "command": "python",
      "args": ["${NCHU_MODULES_PATH}/library/server.py"]
    }
  }
}
// → Python 子程序，透過 stdio 通訊；Client 啟動時自動 spawn
```

**initialize 握手：** Client 與 Server 交換 `protocolVersion` 和 `capabilities`。

```json
// Client → Server
{ "method": "initialize",
  "params": { "protocolVersion": "2024-11-05", "capabilities": {} }, "id": 1 }

// Server → Client
{ "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": { "tools": { "listChanged": true } }
  }, "id": 1 }

// Client 送出 notification 完成握手
{ "method": "notifications/initialized" }
```

> **📺 動畫 Demo：** `mcp-connection-animation.html` — 展示 spawn → initialize → tools/list 完整流程

### 2.4 Tool 註冊與描述

每個 Tool 的三個關鍵欄位：

| 欄位 | 用途 | 重要性 |
|------|------|--------|
| `name` | 唯一識別名稱 | LLM 在 tool_use 時引用 |
| `description` | 自然語言描述 | **LLM 判斷「要不要用」的最重要依據** |
| `inputSchema` | JSON Schema 定義參數 | LLM 據此產生正確的 arguments |

```json
// tools/list 回傳範例（興大系統共 33 個工具）
{ "result": { "tools": [{
    "name": "search_library_books",
    "description": "搜尋中興大學圖書館的館藏書籍，支援關鍵字查詢",
    "inputSchema": {
      "type": "object",
      "properties": {
        "keyword": { "type": "string", "description": "搜尋關鍵字" }
      },
      "required": ["keyword"]
    }
  }]
}}
```

### 2.5 Client 如何把工具清單餵給 LLM

工具定義在 API 呼叫時以 `tools` 參數傳遞，LLM 會根據 `description` 和 `inputSchema` 自行判斷是否使用。

> **📺 動畫 Demo：** `mcp-architecture-animation.html` — 展示 Host / Client / Server 互動全貌

---

## 第三段：Agentic Tool Loop（50 min）

### 3.1 什麼是 Agentic Tool Loop？

**傳統 LLM：** 使用者提問 → LLM 回答 → 結束（單輪、無法存取外部）  
**Agentic LLM：** 使用者提問 → LLM 分析 → 選工具 → 呼叫 → 取得結果 → 再分析 → 可能再呼叫... → 整合回覆

核心概念：LLM 不只回答問題，還能**自主判斷需要什麼資訊、主動呼叫工具取得**。

### 3.2 迴圈流程

```
User Query → Build Messages → Call LLM API → Check stop_reason
                                                    ↓
                                          ┌─ "tool_use"  → Execute MCP Tools ─┐
                                          │                                      │
                                          │  ← 追加 tool_result 到 messages ←──┘
                                          │
                                          └─ "end_turn"  → 回傳最終回覆
```

每一輪稱為一個 **iteration**，最多執行 `maxIterations`（預設 7）輪。

### 3.3 stop_reason — 迴圈的判斷依據

| stop_reason | 意義 | 動作 |
|-------------|------|------|
| `"end_turn"` | 模型認為已可回覆 | 結束迴圈，回傳最終回覆 |
| `"tool_use"` | 模型需要呼叫工具 | 執行工具 → 追加結果 → 進入下一輪 |
| `"max_tokens"` | 回覆被截斷 | 視為完成或觸發錯誤處理 |

### 3.4 tool_use block 格式

```json
// Claude API response.content 中的一個 block
{
  "type": "tool_use",
  "id": "toolu_01A09q90qw90lq917835lq9",   // 唯一識別碼
  "name": "search_library_books",            // MCP 工具名稱
  "input": {                                 // LLM 根據 JSON Schema 自動生成
    "keyword": "人工智慧",
    "limit": 10
  }
}
```

### 3.5 tool_result 格式

```json
// 追加到 messages 陣列（role: "user"）
{
  "role": "user",
  "content": [{
    "type": "tool_result",
    "tool_use_id": "toolu_01A09q90qw90lq917835lq9",  // 必須對應 tool_use 的 id
    "content": [{ "type": "text", "text": "[{\"title\":\"深度學習入門\"},...]" }],
    "is_error": false
  }]
}
```

> **重點：** tool_result 以 **user 角色**送回 — 因為從 LLM 視角，這是「外界提供的新資訊」。

### 3.6 Messages 陣列的成長過程

| # | role | content | iteration |
|---|------|---------|-----------|
| 0 | system | System Prompt（角色設定 + 注入資訊） | — |
| 1 | user | 中興大學圖書館有什麼新書？ | — |
| 2 | assistant | 我需要查詢... + `tool_use: search_new_books` | 第 1 輪 |
| 3 | user | `tool_result: [{"title":"深度學習入門",...}]` | — |
| 4 | assistant | 以下是圖書館最新書籍：1.《深度學習入門》... | 第 2 輪 |

每一輪迭代追加 assistant + user(tool_result)，Messages 陣列持續增長。

### 3.7 一輪中呼叫多個工具

LLM 的 `response.content` 可以同時包含多個 tool_use block：

```javascript
response.content = [
  { type: "text", text: "讓我同時查詢課程和圖書資訊..." },
  { type: "tool_use", name: "search_courses", id: "toolu_001", input: { keyword: "AI" } },
  { type: "tool_use", name: "search_library_books", id: "toolu_002", input: { keyword: "AI" } }
]
// Client 收集所有 tool_use，依序執行每個工具，收集結果
```

### 3.8 核心迴圈程式碼

```javascript
async chatWithStreaming(messages, options) {
  const maxIterations = options.maxIterations || 7;
  let iteration = 0;

  while (iteration < maxIterations) {
    iteration++;

    // 最後一輪？注入強制回覆提示
    if (iteration === maxIterations) {
      messages.push({ role: "user",
        content: "這是最後一輪，請直接回覆..." });
    }

    response = await callLLM(messages, tools);
    toolCalls = response.content.filter(c => c.type === "tool_use");

    if (toolCalls.length === 0) break;  // end_turn → 結束迴圈

    results = await executeTools(toolCalls);  // 執行 MCP 工具
    messages.push(assistantMsg, toolResultMsg); // 追加結果
  }
}
```

### 3.9 maxIterations 與強制回覆

**問題：** LLM 可能不斷呼叫工具而永遠不回覆，造成 token 成本無限增長。

**解法：** 設定 `maxIterations = 7`，最後一輪注入臨時 user message 強制模型停止使用工具：

```javascript
if (iteration === maxIterations) {
  messagesForRequest = [
    ...currentMessages,
    { role: "user",
      content: "注意：這是最後一輪回應，請不要再使用任何工具，" +
        "直接根據工具回傳的資料整理出結構化的 Markdown 回覆。" }
  ];
}
```

> 注意：這則訊息使用臨時變數，**不會存入資料庫**，避免污染對話歷史。

### 3.10 Metadata 追蹤 — 平行陣列

每輪的 `stop_reason` 和 token usage 需要追蹤，但不能放進 messages（否則送回 API 會出錯）。

解法：**平行陣列**，索引對齊、結構分離。

```javascript
const messageStopReasons = [];  // ["tool_use", null, "end_turn"]
const messageUsages = [];       // [{in:850,out:120}, null, {in:1200,out:350}]
// 索引與 messages 中新追加的訊息一一對應
```

### 3.11 SSE 串流 — 即時回饋使用者

整個 agentic loop 過程透過 **Server-Sent Events** 逐步通知前端：

| SSE 事件 | 說明 | 觸發時機 |
|----------|------|----------|
| `thinking_start` | 第 N 輪思考中... | 每輪開始 |
| `tools_start` | 開始執行工具 | 偵測到 tool_use |
| `tool_executing` | 正在執行 search_books... | 每個工具 |
| `tool_completed` | 工具完成，取得結果 | 工具完成 |
| `text_chunk` | 逐字回傳最終文字 | 最後回覆 |
| `done` | 串流結束 | 全部完成 |

```
// 前端接收格式
data: {"type":"tool_executing","data":{"name":"search_books"}}\n\n
data: {"type":"text_chunk","data":"以下是搜尋結果..."}\n\n
```

> **📺 逐步簡報：** `sonnet-running-example.pptx` — 以「中興大學圖書館有什麼新書？」為例的 9 步驟走過  
> **📺 互動動畫：** `sonnet-flow-running-example.html` — 可暫停 / 步進觀察 messages 陣列與迭代過程

---

## 第四段：實務考量（40 min）

### 4.1 多模型 Fallback 策略

系統支援四個 LLM 提供商，依序嘗試：

```
MODEL_FALLBACK_ORDER=claude,gemini,chatgpt,ollama
```

```javascript
// 外層迴圈：嘗試不同 provider
for (const provider of modelFallbackOrder) {
  const aiClient = aiClients[provider];
  // 內層迴圈：嘗試該 provider 的不同模型
  for (const model of providerConfig.models) {
    try {
      return await chatWithStreamingModel(messages, tools, model);
    } catch (error) {
      // 失敗 → 下一個模型
    }
  }
}
```

**設計重點：**
- 每個 provider 實作相同的 interface（`chatWithStreaming`）
- 沒有 API Key 的 provider 在啟動時自動過濾
- 只在 `enableModelFallback = true` 時啟用備援
- SSE 通知前端目前切換到哪個模型

### 4.2 Haiku Alignment — 用小模型達到大模型品質

**目標：** 從 Claude Sonnet（$3.00/1M tokens）切換至 Claude Haiku（$0.80/1M tokens），**省 73% 成本**。

**挑戰：** Haiku 能力較弱，直接切換會造成工具選擇不精確、回覆格式不一致。

**解法：三層品質保護**

| 層次 | 機制 | 檔案 |
|------|------|------|
| 工具選擇規則 | `ALIGNMENT_RULES`（4 條核心規則） | `config/alignment-rules.js` |
| 回覆格式規範 | `RESPONSE_FORMAT_RULES`（5 類 Markdown 模板） | `config/response-format-rules.js` |
| Few-shot 範例 | 從 3,200+ 歷史 trace 檢索 top-9 相似範例 | `api/alignment-middleware.js` |

**System Prompt 組成對比：**

| 層次 | 原始（Sonnet） | 新流程（Haiku） |
|------|---------------|----------------|
| 基礎角色設定 | config.json 靜態 prompt | 同左 |
| 時間/登入資訊 | ChatController 注入 | 同左 |
| 工具選擇規則 | 無 | ALIGNMENT_RULES |
| 回覆格式規範 | 幾句模糊指示 | RESPONSE_FORMAT_RULES（5 類模板） |
| Few-shot 範例 | 無 | 歷史 trace 檢索 top-9 |

**成本影響：**

| 項目 | 數值 |
|------|------|
| Sonnet input 價格 | $3.00 / 1M tokens |
| Haiku input 價格 | $0.80 / 1M tokens |
| 格式規範額外 token | ~300 tokens/request |
| Few-shot 額外 token | ~1,200 tokens/request |
| 每次請求額外成本 | ~$0.0012（可忽略） |

> **📺 動畫 Demo：** `haiku-alignment-animation.html`  
> **📺 完整報告：** `haiku-alignment-report.pptx`

### 4.3 33 個 MCP 工具的分類管理

**工具配置系統：**
- `config.json` — 定義所有 MCP Server（command、args、env）
- `config.local.json` — per-tool enabled/disabled（AdminController 管理）
- `${VAR_NAME}` 語法支援環境變數替換

**工具自動註冊流程：**

```
啟動 → 讀取 config.json
     → 對每個 server: spawn → initialize → tools/list
     → 所有工具註冊到 MCPToolManager
     → 自動注入 user_id / reader_id（SSO 使用者）
```

<!-- 
TODO: 討論 — 這裡要不要放 9 大分類的工具清單？
例如：圖書館（search_books, search_new_books, ...）、課程（get_courses, ...）等等
會不會太細節？
-->

### 4.4 已知限制

| 限制 | 嚴重度 | 說明 |
|------|--------|------|
| 多語系影響 | 中 | Trace 和格式規範為中文，非中文使用者匹配率較低 |
| 工具選擇差異 | 低 | Haiku 選擇的工具與 Sonnet 不完全一致，但方向正確 |
| 部分功能未套用 | 低 | AdminController 等後台功能仍用原版 Client |

---

## 第五段：Q&A + 動手指引（20 min）

### 5.1 環境建置速查

**系統需求：** Node.js ≥ 18.0.0、MongoDB（可選）、Redis（可選）

```bash
# 1. Clone 專案
git clone <repo-url>
cd claude-mcp-project

# 2. 安裝依賴
npm install

# 3. 設定環境變數（複製範本後編輯）
cp .env.example .env
# 必填：ANTHROPIC_API_KEY, NCHU_MODULES_PATH, JWT_SECRET

# 4. 啟動開發模式
npm run dev

# 5. 執行測試
npm test
```

### 5.2 寫一個最簡 MCP Server

以下提供兩個版本：**概念版**讓你快速理解協定結構，**可執行版**可以直接複製跑起來。

#### 概念版（~20 行，理解用）

這個版本省略所有防禦性程式碼，只保留最核心的協定骨架：

```python
# minimal_server.py — 概念版：只看協定結構
import json, sys

def handle(method, params):
    if method == "initialize":
        return {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    if method == "tools/list":
        return {"tools": [{
            "name": "hello",
            "description": "回傳打招呼訊息",
            "inputSchema": {"type": "object",
                            "properties": {"name": {"type": "string"}},
                            "required": ["name"]}
        }]}
    if method == "tools/call":
        name = params["arguments"].get("name", "世界")
        return {"content": [{"type": "text", "text": f"你好，{name}！"}]}

for line in sys.stdin:
    msg = json.loads(line)
    if "id" in msg:  # Request → 要回覆（Notification 沒有 id，直接忽略）
        result = handle(msg["method"], msg.get("params", {}))
        print(json.dumps({"jsonrpc": "2.0", "result": result, "id": msg["id"]}), flush=True)
```

> 這個版本可以跑，但缺少 error handling 和 notification 回應（如 `notifications/initialized`）。
> 用來**對照簡報理解協定流程**最適合。

#### 可執行版（~50 行，可直接搭配 Client 測試）

加入 error handling、正確處理 notification、支援多工具：

```python
#!/usr/bin/env python3
"""minimal_mcp_server.py — 可直接搭配 MCP Client 測試的最簡 Server"""
import json, sys, traceback

# ── 工具定義 ──
TOOLS = [
    {
        "name": "hello",
        "description": "回傳打招呼訊息，可指定姓名",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "要打招呼的姓名"}
            },
            "required": ["name"]
        }
    },
    {
        "name": "add",
        "description": "計算兩個數字的加總",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "第一個數字"},
                "b": {"type": "number", "description": "第二個數字"}
            },
            "required": ["a", "b"]
        }
    }
]

def handle_request(method, params):
    if method == "initialize":
        return {"protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "minimal-server", "version": "0.1.0"}}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        tool_name = params["name"]
        args = params.get("arguments", {})
        if tool_name == "hello":
            return {"content": [{"type": "text", "text": f"你好，{args['name']}！"}]}
        elif tool_name == "add":
            result = args["a"] + args["b"]
            return {"content": [{"type": "text", "text": f"{args['a']} + {args['b']} = {result}"}]}
        else:
            raise ValueError(f"未知工具: {tool_name}")
    raise ValueError(f"未知方法: {method}")

# ── stdio 主迴圈 ──
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        continue  # 略過無法解析的行

    if "id" not in msg:
        continue  # Notification（如 notifications/initialized）→ 不需回覆

    try:
        result = handle_request(msg["method"], msg.get("params", {}))
        resp = {"jsonrpc": "2.0", "result": result, "id": msg["id"]}
    except Exception as e:
        resp = {"jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": msg["id"]}
        print(traceback.format_exc(), file=sys.stderr)

    print(json.dumps(resp), flush=True)
```

**搭配 config.json 註冊：**

```json
{
  "mcpServers": {
    "minimal": {
      "command": "python3",
      "args": ["minimal_mcp_server.py"]
    }
  }
}
```

> 啟動後，Client 會自動 spawn → initialize → tools/list，
> 你的 `hello` 和 `add` 工具就會出現在 LLM 的可用工具清單中。

### 5.3 推薦閱讀

| 資源 | 連結 | 說明 |
|------|------|------|
| MCP 官方規格 | https://spec.modelcontextprotocol.io | 完整協定定義 |
| MCP GitHub | https://github.com/modelcontextprotocol | SDK、範例、官方 Server |
| Claude Tool Use 文件 | https://docs.anthropic.com/en/docs/build-with-claude/tool-use | Claude API 的工具使用指南 |
| JSON-RPC 2.0 規格 | https://www.jsonrpc.org/specification | 底層通訊協定 |

<!-- 
TODO: 討論 — 延伸閱讀要不要加入以下？
- Anthropic Cookbook 的 MCP 教學
- 社群常用 MCP Server 列表
- 類似系統的論文（如果有的話）
-->

### 5.4 課後練習建議

1. **入門：** 修改上面的 minimal_server.py，加入一個新的工具（例如「查天氣」），並在 config.json 中註冊
2. **進階：** 閱讀 `raw-mcp-client.js` 的 `_chatWithStreamingModel()` 方法，追蹤一次完整的 agentic loop
3. **挑戰：** 嘗試新增一個 MCP Server，串接你自己學校的某個 API（如圖書館 OPAC、選課系統）

---

## 附錄：關鍵檔案索引

| 檔案 | 用途 |
|------|------|
| `raw-mcp-client.js` | 核心 MCP Client，agentic loop、多模型 fallback |
| `api/claude-client-aligned.js` | Haiku alignment 專用 Client |
| `api/alignment-middleware.js` | Few-shot 檢索中間件 |
| `mcp/server-connection.js` | MCP Server spawn / initialize / shutdown |
| `mcp/tool-manager.js` | 工具註冊與管理 |
| `config/environment.js` | 環境變數、MCP config 載入 |
| `config.json` | MCP Server 定義（command、args） |
| `controllers/chat-controller.js` | HTTP handler，context injection |
| `services/chat-service.js` | 無聊偵測、對話摘要注入 |
