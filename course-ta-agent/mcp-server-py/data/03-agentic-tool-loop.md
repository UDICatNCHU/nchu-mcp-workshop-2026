# 03-agentic-tool-loop.pptx


## Slide 1

Agentic Tool Loop
LLM 如何自主決策、呼叫工具、迭代推理
MCP 入門工作坊  ｜  第三講（50 min）
國立中興大學  ·  AI 學伴系統實務案例

---

## Slide 2

本講大綱
01
什麼是 Agentic Tool Loop？
傳統 LLM vs 自主代理，迴圈的核心概念
02
tool_use 與 tool_result
Claude API 的工具呼叫機制與訊息格式
03
迭代控制機制
maxIterations、強制回覆、metadata 追蹤
04
Live Demo + Running Example
現場操作，搭配動畫逐步解說

---

## Slide 3

01
什麼是 Agentic Tool Loop？
從「被動回答」到「主動行動」

---

## Slide 4

傳統 LLM vs Agentic LLM
傳統 LLM — 單輪問答
使用者 →  提問
LLM    →  回答（僅根據訓練資料）
結束
無法存取外部資料
無法執行動作
一次互動就結束
Agentic LLM — 多輪迭代
使用者 →  提問
LLM    →  分析 → 選工具 → 呼叫
工具   →  回傳結果
LLM    →  再分析 → 可能再呼叫...
LLM    →  整合回覆
自主決策、多輪迭代
存取外部系統、執行動作

---

## Slide 5

Agentic Tool Loop 概念圖
User
Query
Build
Messages
Call
LLM API
Check
stop_reason
tool_use
Execute
MCP Tools
end_turn
← 追加 tool_result 到 messages，回到 LLM
stop_reason
= "tool_use"
stop_reason
= "end_turn"
每一輪稱為一個 iteration，最多執行 maxIterations（預設 7）輪

---

## Slide 6

02
tool_use 與 tool_result
Claude API 的工具呼叫與回傳機制

---

## Slide 7

stop_reason — 迴圈的關鍵判斷
"end_turn"
模型認為已可回覆
結束迴圈，回傳最終回覆給使用者
"tool_use"
模型需要呼叫工具
執行工具 → 追加結果 → 進入下一輪
"max_tokens"
回覆被截斷
視為完成或觸發錯誤處理
核心邏輯：while (stop_reason === "tool_use" && iteration < maxIterations) { ... }

---

## Slide 8

tool_use — LLM 的工具呼叫指令
當 LLM 決定呼叫工具時，response.content 中會包含 tool_use block：
// Claude API response.content 陣列中的一個 block
{
"type": "tool_use",
"id": "toolu_01A09q90qw90lq917835lq9",
"name": "search_library_books",     // MCP 工具名稱
"input": {                          // LLM 自動產生的參數
"keyword": "人工智慧",
"limit": 10
}
}
type
固定為 "tool_use"，
標識這是工具呼叫
id
唯一識別碼，後續
tool_result 必須對應
name
對應 MCP Server
註冊的工具名稱
input
LLM 根據 JSON Schema
自動生成的參數

---

## Slide 9

tool_result — 工具執行結果回傳
Client 執行 MCP 工具後，將結果以 user 角色追加到 messages：
// 追加到 messages 陣列中（role: "user"）
{
"role": "user",
"content": [{
"type": "tool_result",
"tool_use_id": "toolu_01A09q90qw90lq917835lq9",
"content": [{
"type": "text",
"text": "[{\"title\":\"深度學習入門\"},...]"
}],
"is_error": false
}]
}
tool_use_id
必須與 tool_use 的 id 一致
content
MCP 工具的實際回傳值
（JSON 序列化為 text）
is_error
true 時 LLM 會嘗試
錯誤處理或換一個工具
重點：tool_result 以 user 角色送回 — 因為從 LLM 視角，這是「外界提供的新資訊」

---

## Slide 10

Messages 陣列的成長過程
system
System Prompt（角色設定 + 注入資訊）
user
中興大學圖書館有什麼新書？
assistant
我需要查詢... + tool_use: search_new_books
第 1 輪
user
tool_result: [{"title":"深度學習入門",...}]
assistant
以下是圖書館最新書籍：1.《深度學習入門》...
第 2 輪
每一輪迭代都會追加 assistant + user(tool_result) — Messages 陣列持續增長

---

## Slide 11

一輪中呼叫多個工具
LLM 的 response.content 可以同時包含多個 tool_use block — 平行執行！
response.content = [
{ type: "text", text: "讓我同時查詢課程和圖書資訊..." },
{ type: "tool_use", name: "search_courses",
id: "toolu_001", input: { keyword: "AI" } },
{ type: "tool_use", name: "search_library_books",
id: "toolu_002", input: { keyword: "AI" } }
]
// Client 端收集所有 tool_use：
const toolCalls = response.content
.filter(c => c.type === "tool_use");
// → 依序執行每個工具，收集結果
興大 AI 學伴：「幫我查 AI 課程和相關書籍」→ 一輪同時呼叫 search_courses + search_library_books

---

## Slide 12

03
迭代控制機制
maxIterations · 強制回覆 · Metadata 追蹤

---

## Slide 13

chatWithStreaming() — 核心迴圈
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

---

## Slide 14

maxIterations 與強制回覆機制
問題：無限迴圈風險
LLM 可能不斷呼叫工具而永遠
不回覆使用者，造成：
• Token 成本無限增長
• 回應時間過長
• 使用者體驗極差
解法：maxIterations = 7
設定最大迭代次數上限
第 7 輪（最後一輪）時注入臨時
user message 強制模型停止使用
工具，直接整理回覆
if (iteration === maxIterations) {
messagesForRequest = [
...currentMessages,
{ role: "user",
content: "注意：這是最後一輪回應，" +
"請不要再使用任何工具，" +
"直接根據工具回傳的資料" +
"整理出結構化的 Markdown 回覆。"
}
];
}

---

## Slide 15

Metadata 追蹤 — 不污染 Messages
問題：每輪的 stop_reason 和 token usage 需要追蹤，但不能放進 messages（否則送回 API 會出錯）
messages[]
messageStopReasons[]
messageUsages[]
assistant
(tool_use)
"tool_use"
{ in: 850,
out: 120 }
user
(tool_result)
null
null
assistant
(end_turn)
"end_turn"
{ in: 1200,
out: 350 }
平行陣列模式：索引對齊，結構分離 — 乾淨且不影響 API 呼叫格式

---

## Slide 16

SSE 串流 — 即時回饋使用者
整個 agentic loop 過程中，透過 Server-Sent Events 逐步通知前端：
thinking_start
第 N 輪思考中...
每輪開始
tools_start
開始執行工具
偵測到 tool_use
tool_executing
正在執行 search_books...
每個工具
tool_completed
工具完成，取得結果
工具完成
text_chunk
逐字回傳最終文字
最後回覆
done
串流結束
全部完成
// 前端接收格式
data: {"type":"tool_executing","data":{"name":"search_books"}}\n\n
data: {"type":"text_chunk","data":"以下是搜尋結果..."}\n\n

---

## Slide 17

04
Live Demo + Running Example
搭配動畫與逐步簡報，完整走過一次查詢流程

---

## Slide 18

→  切換到逐步簡報
sonnet-running-example.pptx
展示重點：
Step 1-3：使用者提問 → Controller → 建立 messages 陣列
Step 4-5：第 1 輪 — 送往 Sonnet → 回傳 tool_use block
Step 6：MCP 工具執行（auto-inject user_id）
Step 7-8：第 2 輪 — 帶結果回 Sonnet → end_turn
Step 9：SSE 串流回傳完整回覆

---

## Slide 19

→  切換到互動動畫 Demo
sonnet-flow-running-example.html
展示重點：
即時觀察 messages 陣列如何隨迭代增長
tool_use → tool_result 的資料流動（可暫停 / 步進）
Agentic Loop 的 iteration 計數器視覺化
stop_reason 從 tool_use 變為 end_turn 的轉折點
SSE 事件時序：thinking → tool → text_chunk → done

---

## Slide 20

本講回顧
Agentic = 自主決策
LLM 不只回答問題，還能判斷需要什麼資訊、主動呼叫工具取得
tool_use / tool_result
Claude API 的核心機制 — stop_reason 驅動整個迴圈
maxIterations 安全閥
預設 7 輪上限 + 最後一輪強制回覆，平衡能力與安全
SSE 即時串流
每個步驟（思考、執行工具、回覆）都即時通知前端
下一講：實務考量 — 多模型 fallback、Haiku Alignment 優化、工具分類管理

---