# 04-hands-on-lab.pptx


## Slide 1

Segment 4
動手做
Hands-on Lab · 50 minutes
mini-project 實作主場 — 現場跑起你自己領域的 AI agent
NCHU MCP Workshop 2026
github.com/UDICatNCHU/nchu-mcp-workshop-2026

---

## Slide 2

本節產出物
50 分鐘後，你將親手擁有
2 / 15
✓
在你自己電腦上跑起來的 MCP agent
Node.js + Python FastMCP + 極簡 HTML chat，三層完整可運作
✓
一支「屬於你領域」的客製工具
換 JSON 就好，0 行 Python；實驗室介紹 / 課程大綱 / 研究成果清單都行
✓
對 agent 資料流的「實際脈動感」
工具選擇 → 參數綁定 → LLM 摘要這條路，你會在 terminal 看它一次跑通
✓
L2 / L3 的明確挑戰路徑
帶回去繼續深入：加有參數的搜尋工具、呼叫外部 API

---

## Slide 3

50 分鐘時間配置
講師 10 min 引導 + 40 min 巡場陪跑
3 / 15
時段 (min)
做什麼
產出
0–10
講師 demo + 學員同步 ./setup.sh
環境綠燈 5/5 ✅
10–20
L1 Step 1–2：觀察現況 + 換自己 JSON
data/your.json
20–35
L1 Step 3–4：改 docstring + 重啟驗證
問自己資料會答
35–45
交叉展示：3–4 位老師 demo 自己領域
見識不同落地方式
45–50
Q&A + 為 L2/L3 與 Segment 5 鋪陳
清楚下一步
※ 40 分鐘巡場預計 80% 在幫卡住的老師；開場預演越短，越多時間陪跑。

---

## Slide 4

架構快速回顧
不是單向 pipeline — Node ⟷ LLM 的多輪迭代才是 agent
4 / 15
Browser
web/index.html  ·  fetch POST /chat
⇅
Node server
Express  ·  LLMClient  ·  MCPClient
⇅
Python FastMCP
@mcp.tool()  ·  stdio JSON-RPC
⇅
data/
你的 JSON  ·  外部 API
☁  LLM API
Claude · Gemma · GPT · ...
⟷
agent loop · 多輪迭代
關鍵：⇅ 雙向 — Node ⟷ LLM 之間迭代「問 → tool_use → 跑 → 答 → 再問」直到 end_turn

---

## Slide 5

agent loop 真實長這樣
backend-node/llm-client.js — 整個系統的 20 行核心
5 / 15
async chat(messages) {
  const history = [...messages];
  for (let i = 0; i < maxIterations; i++) {           // ← 護欄
    const resp = await anthropic.messages.create({
      model, tools: mcp.getAnthropicTools(),          // ① 餵 tools
      messages: history,
    });
    history.push({ role: "assistant", content: resp.content });

    if (resp.stop_reason !== "tool_use") {            // ② 結束
      return { reply: extractText(resp), messages: history };
    }

    const toolUses = resp.content                     // ③ 跑工具
      .filter(b => b.type === "tool_use");
    const toolResults = await Promise.all(
      toolUses.map(t => mcp.callTool(t.name, t.input))
    );
    history.push({ role: "user", content: toolResults });
  }
}
①
餵
messages + tools 全部重餵 — 
API 是 stateless，每輪都要全 history
②
結束
stop_reason ≠ tool_use
→ 取 text，回給前端
③
工具
tool_use → 平行 callTool
→ 結果 push 回 history
→ 繼續迴圈
🛑 maxIterations=10 是護欄；超過 → 拋錯。整個 agent 沒有 magic — 就是個 for-loop + if-else。

---

## Slide 6

行前準備（請於上課前完成）
這幾步無關概念，但卡住會吃掉現場時間
6 / 15
1
git clone 教材並進到 mini-project
$ git clone https://github.com/UDICatNCHU/nchu-mcp-workshop-2026
$ cd nchu-mcp-workshop-2026/mini-project
2
取得 LLM 存取（二選一）
雲端：Anthropic Console 申請 API key（新帳號送 $5 試用）
本地：確認你會走 NCHU vLLM 路線（細節見下一頁）
3
建 .env 並填入金鑰
$ cp .env.example .env
$ vim .env   # 填 ANTHROPIC_API_KEY 或 OPENAI_BASE_URL
4
跑環境預檢
$ ./setup.sh
    → 看到 5/5 ✅ 代表現場可以直接 npm start
✅ 行前 4 步完成 → 現場只剩「npm start + 開瀏覽器」（下一頁）

---

## Slide 7

現場啟動（5 分鐘）
三條指令 + 對照「該長什麼樣」
7 / 15
▶  你輸入
$ ./setup.sh                            # 1. sanity check 已裝好的環境
$ cd backend-node && npm start          # 2. 啟動 backend + spawn MCP
$ open http://localhost:3000            # 3. 瀏覽器
▶  你應該看到（npm start 印出）
> mini-assistant@1.0.0 start
> node server.js

✓ hello_tool → get_english_center_info
✓ teachers_tool → search_teachers, get_teacher_detail
✓ weather_tool → get_weather
→ Mini AI Assistant: http://localhost:3000
🎉 三行 ✓ + URL → MCP server 都連上了；瀏覽器問「英文中心幾點開門？」會在 terminal 看 [tool_use]
⚠ 沒看到 ✓ 三行：→ Slide 13 卡點速查

---

## Slide 8

選你的 LLM 路線
`.env` 一行切換 — 因為 MCP 工具兩家都認
8 / 15
☁  雲端 · Anthropic Claude
# .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-haiku-4-5
🏠  本地 · NCHU vLLM (Gemma 4)
# .env
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://<ws-host>:8000/v1
OPENAI_API_KEY=dummy
OPENAI_MODEL=gemma-4
💎  N+M 的甜蜜：你的工具一支不變，adapter 差別只在 mcp-client.js 這幾行
// getAnthropicTools()
{
  name,
  description,
  input_schema,   // ← MCP's
}
// getOpenAITools()
{ type: "function",
  function: {
    name, description,
    parameters,   // ← 同一個
} }
📊 2026-04-24 實測：Tool 正確率 Claude 100% · Gemma 4 100%　|　延遲 4.8s vs 3.5s　|　兩者 hallucination 都通過
→ 詳細 benchmark：mini-project/docs/benchmarks/2026-04-24-claude-vs-gemma4.md

---

## Slide 9

Lab 1 — 換 JSON 做你領域的助理
0 行 Python · 40 分鐘 · 現場必做
9 / 15
1
觀察
看 [tool_use] log
AI 摘要 JSON
5 min
2
換資料
編輯 data/*.json
放你的領域內容
15 min
3
改說明書
docstring 的使用情境
決定工具呼叫率
10 min
4
驗證
重啟 npm start
問自己資料問題
5 min
產出：你的 AI 助理會回答「你自己放進去的資料」— 不是英文中心 demo 了

---

## Slide 10

Step 1–2：觀察 → 換 JSON
還沒動到 Python 一個字
10 / 15
Step 1　觀察（5 min）
在瀏覽器問：
「英文中心幾點開門？」
在 terminal 觀察：
[tool_use] get_english_center_info
💡 關鍵觀察
Claude 不會 dump 整份 JSON。它挑出「開放時間」那一段。
這是 LLM 對 tool result 做的「摘要」— agent 的靈魂。
Step 2　換 JSON（15 min）
編輯：
mcp-server-py/data/english_center.json
換成你自己的領域資料：
• 你的研究室介紹
• 你教的一門課（大綱/作業/評分）
• 你系所的 FAQ
• 你的研究成果清單
⚠ JSON 語法錯會卡住：
python3 -m json.tool data/xxx.json  驗一下

---

## Slide 11

Step 3：改 docstring（10 min）
直接拿 repo 兩支真實工具對照 — 同樣語法、教 LLM 不同事
11 / 15
📝  minimal — hello_tool.py
@mcp.tool()
def get_english_center_info() -> str:
    """取得中興大學英語自學暨
    檢定中心的完整資訊。

    回傳 JSON 字串，包含：
    名稱、開放時間、地點、設備…
    使用情境：使用者詢問英語
    自學中心相關問題時呼叫。
    """
📖  rich — teachers_tool.py
@mcp.tool()
def get_teacher_detail(name: str) -> str:
    """取得指定教授的完整資訊
    （email、辦公室、研究領域）。

    使用情境：使用者問某位教授
    的聯絡方式或完整資料時呼叫。
    通常在 search_teachers 找到
    候選名單後再呼叫。 ←跨工具線索

    Args:
        name: 教授姓名（完整中文）。
    """
影響 LLM 行為的 3 個元素： ① 使用情境 → 該不該叫    ② Args 描述 → 怎麼填參數    ③ 跨工具線索 → 多輪呼叫順序

---

## Slide 12

Step 4：重啟 + 驗證（5 min）
三件事證明你的工具「真的在 work」
12 / 15
$ Ctrl+C                            # 停掉前一次 server
$ cd backend-node && npm start
  → ✓ hello_tool → get_lab_info    # 新名字出現代表工具註冊成功
①
問「不相關」的問題
「今天天氣？」
AI 應該不呼叫你的工具，直接聊天
②
問「相關」的問題
「研究室招生條件？」
AI 會引用 JSON 裡的實際內容
③
問「資料沒有」的內容
「有實習機會嗎？」（JSON 沒這欄）
AI 應該明說不知道，不會幻想
第 ③ 項過關最關鍵 — 代表 agent 在 tool-grounded，不是在胡謅。

---

## Slide 13

常見卡點速查
卡住 30 秒就看這頁；更多在 Lab 手冊結尾
13 / 15
症狀
原因
解法
setup.sh 卡 Node 版本
本機 Node < 18
nvm install 22 && nvm use 22
port 3000 已被占
其他服務先佔了
PORT=3001 npm start
瀏覽器問後沒反應
.env 的 API key 還是 placeholder
檢查 sk-ant-... 有沒有填
JSON 讀取錯誤
手改 JSON 有語法錯
python3 -m json.tool data/xxx.json
問相關問題但 LLM 不叫工具
docstring 寫太短 / 太含糊
補「使用情境：當使用者問 X 時」
npm start 看不到工具列表
config.json 的 server key
與 FastMCP("...") 名稱對不上
兩邊改成同一個字串
Could not find tool / 啟動失敗
mcp-server-py 沒裝依賴
cd mcp-server-py && uv sync
卡住超過 3 分鐘：舉手。講師 + 鄰座老師會過來幫你。

---

## Slide 14

交叉展示 — Show & Tell
35–45 min · 看 3 位老師把同一支 mini-project 變成自己的 agent
14 / 15
🎤  請 3 位老師上來（每人 3 分鐘）
① 一句話介紹你的領域 + 你放了什麼 JSON
例：「我教植物分類學，JSON 是 50 種校園樹木」
② 問你的 agent 一個你自己關心的問題
例：「校門口那棵開白花的是什麼？」
③ 講一個你踩到的雷（30 秒）
docstring 寫太短？JSON 結構太深？編碼錯？
💡  為什麼花 10 分鐘做這件事
看見落地的多樣性
醫學人文 / 物理 / 語言學 / 行政 FAQ —
同一支 code 在不同領域的形狀。
偷學別人 docstring 寫法
10 個老師有 10 種「使用情境」描述法 —
看誰的 AI 最聽話。
提早為 L2 / L3 預警
別人卡的雷，可能就是你下午自修會踩到的。
※ 沒上台的老師不是觀眾 — 把對你「最有啟發」的那個 demo 記下來，課後試試

---

## Slide 15

恭喜 — 你剛做出了
屬於你自己領域的 AI agent
回家路徑（課後自修）
🧪  L2 — 加一支有參數的搜尋工具
docs/labs/L2-add-a-search-tool.md  (40 分)
🧪  L3 — 呼叫外部 API（async + XML）
docs/labs/L3-call-external-api.md  (60 分)
下一段 Segment 5
實務考量（10 min 收尾）
從「你剛做的 3 個工具」往外擴：
• 239 工具怎麼辦？（Scale）
• 工具描述怎麼寫？（Quality）
• 該用哪個模型？（Model）
• 帳單會有多貴？（Cost）
github.com/UDICatNCHU/nchu-mcp-workshop-2026   ·   Issues 歡迎！

---