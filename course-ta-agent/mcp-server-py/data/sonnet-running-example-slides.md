# sonnet-running-example.pptx


## Slide 1

Running Example
原始 Sonnet 流程
查詢範例：「中興大學圖書館有什麼新書？」
以下我們將逐步走過這個查詢從使用者送出到收到回覆的完整流程
使用者
Browser
→
ChatController
controllers/
→
raw-mcp-client
.js
→
ClaudeClient
claude-client.js
→
Claude Sonnet
API
→
MCP Tools
mcp/*.js
→
SSE 串流
回覆用戶

---

## Slide 2

1
Step 1：使用者送出查詢
Running Example： 「中興大學圖書館有什麼新書？」
使用者
→
ChatController
controllers/
→
raw-mcp-client
.js
→
ClaudeClient
claude-client.js
→
Claude Sonnet
API
→
MCP Tools
mcp/*.js
→
SSE 串流
回覆用戶
Agentic Loop：
1
2
3
4
5
6
7
說明
瀏覽器透過 POST /api/chat/stream 送出訊息
需攜帶 Chat Token（經 Turnstile 驗證）
API Messages 陣列
（尚未建立 messages）
Step 1 / 9

---

## Slide 3

2
Step 2：ChatController 接收
Running Example： 「中興大學圖書館有什麼新書？」
使用者
Browser
→
ChatController
→
raw-mcp-client
.js
→
ClaudeClient
claude-client.js
→
Claude Sonnet
API
→
MCP Tools
mcp/*.js
→
SSE 串流
回覆用戶
Agentic Loop：
1
2
3
4
5
6
7
說明
驗證 Chat Token → 解析 JWT 取得登入資訊
注入「當前時間」與「登入狀態」到 system prompt
注入後的 System Prompt
你是中興大學智慧助理「TARA」...
[注入] 時間：2026-03-30 10:15
[注入] 登入：SSO user_id: s12345678
API Messages 陣列
（尚未建立 messages）
Step 2 / 9

---

## Slide 4

3
Step 3：raw-mcp-client 準備
Running Example： 「中興大學圖書館有什麼新書？」
使用者
Browser
→
ChatController
controllers/
→
raw-mcp-client
→
ClaudeClient
claude-client.js
→
Claude Sonnet
API
→
MCP Tools
mcp/*.js
→
SSE 串流
回覆用戶
Agentic Loop：
1
2
3
4
5
6
7
說明
建立 messages 陣列
設定 maxIterations = 7，準備進入 agentic loop
API Messages 陣列
System
你是中興大學智慧助理「TARA」... [已注入時間 + 登入資訊]
User
中興大學圖書館有什麼新書？
Step 3 / 9

---

## Slide 5

4
Step 4：第 1 輪 — 送往 Sonnet
Running Example： 「中興大學圖書館有什麼新書？」
使用者
Browser
→
ChatController
controllers/
→
raw-mcp-client
.js
→
ClaudeClient
→
Claude Sonnet
API
→
MCP Tools
mcp/*.js
→
SSE 串流
回覆用戶
Agentic Loop：
1
2
3
4
5
6
7
第 1 輪
說明
ClaudeClient 將 messages 送往 Claude Sonnet API
模型分析問題後，決定呼叫工具
API Messages 陣列
第 1 輪
System
System Prompt（靜態 config）
User
中興大學圖書館有什麼新書？
Step 4 / 9

---

## Slide 6

5
Step 5：Sonnet 回傳 tool_use
Running Example： 「中興大學圖書館有什麼新書？」
使用者
Browser
→
ChatController
controllers/
→
raw-mcp-client
.js
→
ClaudeClient
claude-client.js
→
Claude Sonnet
→
MCP Tools
mcp/*.js
→
SSE 串流
回覆用戶
Agentic Loop：
1
2
3
4
5
6
7
第 1 輪
說明
stop_reason = "tool_use"
模型要呼叫 search_new_books 工具
API Messages 陣列
第 1 輪
System
System Prompt（靜態 config）
User
中興大學圖書館有什麼新書？
Assistant
我需要查詢圖書館的新書資訊。
Tool Call
search_new_books({   "query": "新書", "limit": 10 })
Step 5 / 9

---

## Slide 7

6
Step 6：執行 MCP 工具
Running Example： 「中興大學圖書館有什麼新書？」
使用者
Browser
→
ChatController
controllers/
→
raw-mcp-client
.js
→
ClaudeClient
claude-client.js
→
Claude Sonnet
API
→
MCP Tools
→
SSE 串流
回覆用戶
Agentic Loop：
1
2
3
4
5
6
7
第 1 輪
說明
透過 mcp/server-connection.js 呼叫
search_new_books Python 腳本
自動注入 user_id 給工具
API Messages 陣列
第 1 輪
System
System Prompt（靜態 config）
User
中興大學圖書館有什麼新書？
Assistant
我需要查詢圖書館的新書資訊。
Tool Call
search_new_books({...})
Tool Result
[{"title":"深度學習入門",...},  {"title":"量子計算導論",...},  ...共 10 筆...
Step 6 / 9

---

## Slide 8

7
Step 7：第 2 輪 — 帶工具結果回 Sonnet
Running Example： 「中興大學圖書館有什麼新書？」
使用者
Browser
→
ChatController
controllers/
→
raw-mcp-client
.js
→
ClaudeClient
→
Claude Sonnet
API
→
MCP Tools
mcp/*.js
→
SSE 串流
回覆用戶
Agentic Loop：
1
2
3
4
5
6
7
第 2 輪
說明
工具結果追加到 messages
stop_reason 是 tool_use → 繼續迭代
再次送往 Sonnet
API Messages 陣列
第 2 輪
System
System Prompt（靜態 config）
User
中興大學圖書館有什麼新書？
Assistant
我需要查詢圖書館的新書資訊。
Tool Call
search_new_books({...})
Tool Result
[10 筆新書結果]
Step 7 / 9

---

## Slide 9

8
Step 8：Sonnet 產生最終回覆
Running Example： 「中興大學圖書館有什麼新書？」
使用者
Browser
→
ChatController
controllers/
→
raw-mcp-client
.js
→
ClaudeClient
claude-client.js
→
Claude Sonnet
→
MCP Tools
mcp/*.js
→
SSE 串流
回覆用戶
Agentic Loop：
1
2
3
4
5
6
7
第 2 輪
說明
stop_reason = "end_turn"
模型不再呼叫工具，輸出新書清單
Agentic Loop 結束
API Messages 陣列
第 2 輪
System
System Prompt（靜態 config）
User
中興大學圖書館有什麼新書？
Assistant
我需要查詢圖書館的新書資訊。
Tool Call
search_new_books({...})
Tool Result
[10 筆新書結果]
Assistant
以下是圖書館最新書籍：1.《深度學習入門》2.《量子計算導論》...
Step 8 / 9

---

## Slide 10

9
Step 9：SSE 串流回覆給用戶
Running Example： 「中興大學圖書館有什麼新書？」
使用者
Browser
→
ChatController
controllers/
→
raw-mcp-client
.js
→
ClaudeClient
claude-client.js
→
Claude Sonnet
API
→
MCP Tools
mcp/*.js
→
SSE 串流
Agentic Loop：
1
2
3
4
5
6
7
第 2 輪
說明
回覆透過 SSE 逐段送回瀏覽器
前端即時顯示打字效果
整個流程完成！共 2 輪迭代
SSE 串流事件
response_end  → stop_reason: end_turn
done          → 串流結束，共 2 輪迭代
API Messages 陣列
第 2 輪
System
...
User
中興大學圖書館有什麼新書？
Assistant
（第 1 輪）我需要查詢...
Tool Call
search_new_books({...})
Tool Result
[10 筆結果]
Assistant
以下是圖書館最新書籍：1.《深度學習入門》2.《量子計算導論》...
Step 9 / 9

---

## Slide 11

原始流程回顧
靜態 System Prompt
僅有 config.json 的固定角色設定 + ChatController 注入的時間/登入資訊。沒有工具選擇規則，也沒有回覆格式規範。
Sonnet 模型
使用 Claude Sonnet（$3.00/1M input tokens），能力強但成本高。模型自行判斷要呼叫哪些工具。
無 Few-shot 引導
沒有歷史範例告訴模型「這類問題該怎麼回答」，完全依賴模型本身的能力。
回覆格式不一致
最後一輪只說「不要用工具，直接回覆」，沒有結構化 Markdown 格式要求，回覆品質不穩定。
下一章：Haiku Alignment 如何改善這些問題？

---