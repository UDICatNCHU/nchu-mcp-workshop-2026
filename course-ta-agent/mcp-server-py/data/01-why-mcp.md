# 01-why-mcp.pptx


## Slide 1

Why MCP
從 LLM 的局限到 Model Context Protocol
MCP 入門工作坊  ｜  第一講（50 min）
國立中興大學  ·  AI 學伴系統實務案例

---

## Slide 2

本講大綱
01
LLM 能做什麼？不能做什麼？
理解大型語言模型的能力邊界
02
三種延伸策略
RAG、Tool Use、MCP 深入比較
03
MCP 核心概念
Host / Client / Server / Tool 架構
04
實際案例：興大 AI 學伴
33 個 MCP 工具的校園應用

---

## Slide 3

LLM 擅長什麼？
語言理解與生成
翻譯、摘要、改寫、
多語言對話
推理與分析
邏輯推導、比較分析、
結構化輸出
程式碼生成
撰寫、除錯、解釋
多種程式語言
知識回答
基於訓練資料的
常識與專業知識
這些能力來自訓練階段學到的「靜態知識」

---

## Slide 4

LLM 的天花板
知識截止日
訓練資料有日期上限，
無法回答「今天」的事
沒有私有資料
不知道你的課表、
圖書館藏書、校內公告
無法執行動作
不能幫你查詢系統、
預約空間、操作 API
會幻覺
不確定時仍自信回答，
編造看起來合理的資訊
核心問題：如何讓 LLM 存取「外部世界」的資訊與功能？

---

## Slide 5

02
三種延伸策略
RAG  ·  Tool Use  ·  MCP

---

## Slide 6

策略 A：RAG（Retrieval-Augmented Generation）
使用者提問
→
Embedding
向量化
→
向量資料庫
相似度搜尋
→
取回相關
文件片段
→
注入 Prompt
+ LLM 回答
優點
降低幻覺 — 有引用來源
存取私有資料（文件、知識庫）
不需重新訓練模型
局限
只能「讀」— 無法執行動作
檢索品質依賴 embedding 與切塊策略
結構化查詢（如 SQL）支援差

---

## Slide 7

RAG — 概念程式碼
# 1. 使用者提問
query = "中興大學圖書館有什麼 AI 相關的書？"

# 2. 轉成向量，在資料庫中搜尋最相似的文件片段
embedding = embed_model.encode(query)
relevant_docs = vector_db.search(embedding, top_k=5)

# 3. 把搜尋結果塞進 prompt，交給 LLM
prompt = f"根據以下資料回答問題:\n{relevant_docs}\n\n問題：{query}"
response = llm.generate(prompt)

---

## Slide 8

策略 B：Tool Use（Function Calling）
使用者提問
→
LLM 分析
選擇工具
→
呼叫外部
API / 函式
→
取得執行
結果
→
LLM 整合
回覆
關鍵差異：LLM 自己決定「要不要用工具」以及「用哪一個」
優點
能「做事」— 查詢、計算、操作
結構化輸入輸出（JSON Schema）
局限
每家 API 格式不同（vendor lock-in）
工具要寫死在應用程式裡

---

## Slide 9

Tool Use — Claude API 範例
// 定義工具
tools: [{
  name: "search_library_books",
  description: "搜尋圖書館館藏",
  input_schema: {
    type: "object",
    properties: { keyword: { type: "string" } }
  }
}]

// LLM 回傳 → tool_use block
{ type: "tool_use",
  name: "search_library_books",
  input: { keyword: "人工智慧" } }

---

## Slide 10

Tool Use — ChatGPT API 範例
// 定義工具 — 注意：欄位名稱和結構都跟 Claude 不同
tools: [{
  type: "function",              // Claude 沒有這個欄位
  function: {                    // 多包一層 function
    name: "search_library_books",
    description: "搜尋圖書館館藏",
    parameters: {                // Claude 叫 input_schema
      type: "object",
      properties: { keyword: { type: "string" } }
    }
  }
}]

// LLM 回傳 → tool_calls (不是 tool_use)
tool_calls: [{
  id: "call_abc123",              // 需要 call ID
  type: "function",
  function: {
    name: "search_library_books",
    arguments: "{\"keyword\": \"人工智慧\"}"  // 字串，不是物件!
  }
}]

---

## Slide 11

Tool Use 的痛點：每個應用都要重做
ChatGPT App
Claude App
Gemini App
自建 Agent
圖書館 DB
課程系統
教師資料
校內公告
N × M
個別整合
4 個 AI 應用 × 4 個資料源 = 16 個 connector，而且格式各不相同

---

## Slide 12

策略 C：MCP（Model Context Protocol）
ChatGPT App
Claude App
Gemini App
自建 Agent
MCP
統一協定
JSON-RPC
圖書館 DB
課程系統
教師資料
校內公告
寫一次 MCP Server，所有 AI 應用都能用 — 像 USB-C 一樣的標準介面

---

## Slide 13

三者比較總覽
面向 | RAG | Tool Use | MCP
核心能力 | 檢索文件 | 執行功能 | 檢索 + 執行 + 標準化
LLM 角色 | 只讀 prompt 中的資訊 | 決定呼叫 哪個函式 | 透過 Client 調度 Server
整合方式 | Embedding + 向量 DB | 各家 API 各寫一套 | 統一 JSON-RPC 協定
可重用性 | 綁定單一應用 | 綁定單一應用 | Server 跨 應用共用
即時資料 | 需重新索引 | 可即時查詢 | 可即時查詢
執行動作 | 不能 | 可以 | 可以
維護成本 | 中 | 高（N×M） | 低（N+M）

---

## Slide 14

什麼時候用哪一種？
RAG
適用場景
內部知識庫問答
文件搜尋與摘要
客服 FAQ 系統
最適合：
大量非結構化文本
Tool Use
適用場景
呼叫特定 API
資料庫查詢
計算或產生圖表
最適合：
少量、固定的工具
MCP
適用場景
多系統整合平台
校園/企業助手
跨應用共享工具
最適合：
工具多、需跨應用重用

---

## Slide 15

它們不是互斥的 — 可以混用
RAG
文件知識
語義搜尋
Tool Use
API 呼叫
動作執行
MCP 可以同時提供 RAG 式的檢索資源 和 Tool Use 式的可執行工具
MCP Server
可同時包含兩者

---

## Slide 16

03
MCP 核心概念
Host  ·  Client  ·  Server  ·  Tool

---

## Slide 17

MCP 架構四大角色
Host
使用者介面
（如 Claude Desktop、
自建 Web App）
Client
MCP 協定客戶端
負責與 Server 建立
連線、傳遞訊息
Server
MCP 服務端
包裝外部資源為
標準化工具
Tool
具體功能定義
如 search_books、
get_courses
→
→
→
類比：Host = 瀏覽器、Client = HTTP 客戶端、Server = Web Server、Tool = API Endpoint

---

## Slide 18

MCP 如何溝通？— JSON-RPC 2.0
Client → Server (Request)
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_books",
    "arguments": {
      "keyword": "AI"
    }
},
"id": 1
}
Server → Client (Response)
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{
      "type": "text",
      "text": "找到 3 本..."
    }]
},
"id": 1
}
標準化
所有 MCP 通訊用同一格式
雙向
Client 可呼叫 Server，Server 也可通知 Client
傳輸無關
支援 stdio、HTTP+SSE、WebSocket 等

---

## Slide 19

04
實際案例：興大 AI 學伴
33 個 MCP Tools  ·  9 大類  ·  真實上線運作

---

## Slide 20

33 個 MCP 工具 — 九大分類
課程查詢
8
search_courses
get_department_courses
get_teacher_courses
圖書資源
5
search_library_books
get_loan_history
get_elearning_resources
教師研究
7
search_teachers
get_research_projects
get_teacher_orcid
學術規劃
5
get_cross_program_courses
get_dual_degrees
get_education_programs
校園資源
5
get_activities
get_campus_news
book_space
行政法規
3
search_regulations
get_academic_standards
get_faqs
每一個工具都是獨立的 MCP Server  — 用 Python 寫，透過 stdio 與 Node.js Client 通訊

---

## Slide 21

本講重點回顧
1
LLM 有知識截止、無法存取外部系統的先天限制
2
RAG 解決「讀」的問題，Tool Use 解決「做」的問題
3
但 Tool Use 有 N×M 整合爆炸的痛點
4
MCP 用統一協定解耦 AI 應用與資料源，實現 N+M 整合
5
興大 AI 學伴用 33 個 MCP 工具服務真實校園需求
下一講預告：How MCP Works — 架構與連線機制實作

---