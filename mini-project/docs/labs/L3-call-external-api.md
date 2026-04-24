# Lab 3 — 呼叫外部 API（課後自修，約 60 分鐘）

## 🎯 目標

前兩關的工具只讀**本地 JSON**。真實世界的 AI 助理通常要打**外部 HTTP API**：天氣、論文、股價、CMS、Slack…。本關用 arXiv 論文搜尋當範例，示範：

1. **async tool** — FastMCP 原生支援 `async def`，適合 I/O bound 呼叫
2. **`httpx.AsyncClient`** — 現代 async HTTP client
3. **三層錯誤處理**：timeout / HTTP error / parse error
4. **非 JSON 回應**（XML / RSS / CSV 等）的處理
5. **邊界檢查**：使用者可能傳 `limit=999`，你要夾到合理範圍

## 前置

- 完成 L1、L2
- 已有網路連線
- **不需要 API key**（arXiv 是公開端點）

## 完整範例檔

我們已經幫你寫好 `mcp-server-py/arxiv_tool.py`（~80 行）。**建議你先自己讀一遍**，再回來對照下列重點。

### 新增的依賴

```bash
cd mcp-server-py
uv add httpx   # 已為你執行過；再跑也無害
```
`pyproject.toml` 會自動加入 `"httpx>=0.28.1"`。

### 核心：async tool 函式

```python
@mcp.tool()
async def search_arxiv(keyword: str, limit: int = 5) -> str:
    """..."""
    limit = max(1, min(limit, MAX_LIMIT))  # 邊界夾住
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.get(ARXIV_API, params=params)
        resp.raise_for_status()
    root = ET.fromstring(resp.text)
    papers = [_extract_entry(e) for e in root.findall("atom:entry", ATOM_NS)]
    return json.dumps(papers, ensure_ascii=False, indent=2)
```

**關鍵觀察**：
- `@mcp.tool()` 對 `async def` 完全透明——Claude 不知道、也不需要知道這支工具是 async
- 從 Claude 的視角，tool 就是「丟參數 → 拿 JSON 字串」。async 只是 Python 端的實作細節
- 若你的 tool 要呼叫 3 個 API 可以 `asyncio.gather(...)` 並行，I/O 時間會大幅縮短

### 核心：錯誤處理（實務重點）

```python
try:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(ARXIV_API, params=params)
        resp.raise_for_status()
except httpx.TimeoutException:
    return json.dumps({"error": "arXiv 回應逾時"}, ensure_ascii=False)
except httpx.HTTPError as e:
    return json.dumps({"error": f"API 錯誤：{e}"}, ensure_ascii=False)
```

**為什麼不 raise 而是回錯誤 JSON？** 因為我們要把錯誤訊息**交給 LLM 處理**——Claude 收到 `{"error": "逾時"}` 會自己判斷要「告訴使用者晚點試」或「改用其他工具」。這正是 tool-use paradigm 的彈性：**工具的錯誤也是資訊，不是 exception**。

> 💡 但 tool 的**程式 bug**（例如 `KeyError`）應該讓它拋出。FastMCP 會把 exception 包成 `isError: true` 的 tool_result 回給 Claude，Claude 會 retry 或改用其他工具。

## Steps（整合到現有專案）

### Step 1 — 註冊進 config

編輯 `config.json`，加第三個 entry：

```json
{
  "mcpServers": {
    "hello_tool": {
      "command": "uv",
      "args": ["--directory", "mcp-server-py", "run", "python", "hello_tool.py"]
    },
    "teachers_tool": {
      "command": "uv",
      "args": ["--directory", "mcp-server-py", "run", "python", "teachers_tool.py"]
    },
    "arxiv_tool": {
      "command": "uv",
      "args": ["--directory", "mcp-server-py", "run", "python", "arxiv_tool.py"]
    }
  }
}
```

### Step 2 — 重啟 server

```bash
cd backend-node && npm start
```

應看到：

```
✓ hello_tool → get_lab_info
✓ teachers_tool → search_teachers, get_teacher_detail
✓ arxiv_tool → search_arxiv
```

### Step 3 — 測試

| 問題 | 預期行為 |
|------|---------|
| `retrieval augmented generation 最新論文？` | 呼叫 `search_arxiv` 傳英文 keyword |
| `最近有什麼 transformer 相關研究？` | 呼叫 `search_arxiv` 傳 `"transformer"` |
| `幫我找 5 篇 RAG 論文` | 呼叫時會帶 `limit=5` |
| `研究室招生條件？` | 回去呼叫 L1 的 `get_lab_info` |

**觀察重點**：Claude 會**自動把中文問題翻成英文 keyword** 再呼叫 arXiv，因為 docstring 明寫了「英文效果較好」。這就是 tool description 影響呼叫行為的力量。

## 🐛 Common Pitfalls

| 症狀 | 原因 | 解法 |
|------|------|------|
| `ParseError: no element found` | arXiv 回 301 → 要用 `https://` 而非 `http://` | 永遠用 HTTPS |
| Claude 不呼叫 `search_arxiv` | 和 L2 衝突，或 docstring 太弱 | 明確寫「**論文**」關鍵字 |
| timeout 常發生 | 15 秒對 arXiv 夠，但某些 API 需 30+ | 調 `TIMEOUT_SECONDS` |
| 回傳中文亂碼 | XML 解析出 `中文` | 確保 `ensure_ascii=False` |
| `RuntimeError: no running event loop` | 在 sync 函式內用 `await` | 整支函式要 `async def` |
| rate limit / 403 | arXiv 本身限流（過快不讓打） | 加 retry 或 `await asyncio.sleep(3)` |

## 🚀 Stretch Goals

### A. 替代 API — wttr.in（更簡單）

`wttr.in` 回純文字天氣，免 key、無 XML。適合做 L3 的「縮減版」，只要 20 行：

```python
@mcp.tool()
async def get_weather(city: str) -> str:
    """查詢城市天氣概況。"""
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"https://wttr.in/{city}", params={"format": "j1"})
        r.raise_for_status()
    return r.text  # 已是 JSON string
```

### B. 需要 API key 的 API（示範 secrets 管理）

挑一個需要 key 的 API（如 OpenWeatherMap、Alpha Vantage、News API），示範：

```python
import os
API_KEY = os.environ.get("OPENWEATHER_API_KEY")

@mcp.tool()
async def get_weather_detailed(city: str) -> str:
    """..."""
    if not API_KEY:
        return json.dumps({"error": "缺少 OPENWEATHER_API_KEY"}, ensure_ascii=False)
    async with httpx.AsyncClient() as c:
        r = await c.get("https://api.openweathermap.org/...",
                        params={"q": city, "appid": API_KEY})
        ...
```

然後在 `.env` 加 `OPENWEATHER_API_KEY=...`，記得 `.gitignore` 有擋 `.env`（L0 已設）。

### C. 並行呼叫（效能示範）

讓 tool 同時打三個 API：

```python
async def get_trends(keyword: str) -> str:
    async with httpx.AsyncClient() as c:
        arxiv_task, hn_task, gh_task = await asyncio.gather(
            c.get(f"https://export.arxiv.org/api/query?search_query={keyword}"),
            c.get(f"https://hn.algolia.com/api/v1/search?query={keyword}"),
            c.get(f"https://api.github.com/search/repositories?q={keyword}"),
        )
    # 合併三個來源
    ...
```

三個 API 總耗時 ≈ 最慢那個，不是總和。這是 async 帶來的顯著收益。

### D. 結合 L2：搜尋 → 充實

把 L2 的 `search_teachers` 回傳的教授名字餵給 `search_arxiv(author:Name)`，做一條「查教授論文」的資料流。Claude 會自動串起兩個 tool：

> 「李小華老師最近有什麼論文？」
> → `search_teachers` 找到全名
> → `search_arxiv(keyword="author:李小華")` 取論文清單

這就是 **agent 的 tool orchestration**。

### E. 快取（效能 + rate-limit 友善）

重複關鍵字 30 秒內不要重打 API：

```python
from functools import lru_cache
from datetime import datetime, timedelta

_cache: dict[str, tuple[datetime, str]] = {}

async def search_arxiv_cached(keyword: str, limit: int = 5) -> str:
    key = f"{keyword}|{limit}"
    if key in _cache:
        ts, result = _cache[key]
        if datetime.now() - ts < timedelta(seconds=30):
            return result
    result = await search_arxiv.__wrapped__(keyword, limit)
    _cache[key] = (datetime.now(), result)
    return result
```

## 🤔 Reflection

1. **安全**：若學生寫的 tool 呼叫 `os.system(user_input)`，會發生什麼？MCP 能阻止嗎？（→ L4 主題：tool sandbox）
2. **冪等性**：`search_arxiv` 是 read-only 所以可重試；若是 `create_issue` 呢？Retry 可能造成重複建立。怎麼設計 idempotency key？
3. **觀測**：真實系統要知道每支 tool 的 latency、error rate、cost。你會怎麼 instrument 這些 async tools？（Hint: OpenTelemetry + semantic conventions）
4. **成本分析**：若有 1000 個同時使用者，每天 5 次對話、每次平均觸發 3 次 tool_call，你的 API quota 和 Claude API 花費分別是多少？
5. **教學**：你會怎麼**評分**學生交的 external-API tool？我的建議 rubric：
   - [ ] 正確解析（30%）
   - [ ] 錯誤處理完整（25%）
   - [ ] docstring 品質（20%）
   - [ ] 邊界檢查（15%）
   - [ ] 非功能（cache / retry / observability）（10%）

## 🎓 學到這裡，你能做的事

做完 L1-L3，你已具備做任何 **domain-specific AI assistant** 的能力：
- 有靜態資料 → L1 模式
- 有資料列表、需搜尋 → L2 模式
- 要打外部 API → L3 模式
- 組合以上 → 真實系統（例如 NCHU 正式版 AiLearningMate 用了 ~50 支各種模式的工具）

**接下來的方向（自修）**：
- **L4**：有副作用的 tool（寫檔、發 email、建 issue）+ 人類確認機制
- **L5**：寫 MCP tool 的 pytest 單元測試
- **L6**：把 Claude 換成 Ollama 本地模型（Llama 3.1 也支援 tool use）
- **L7**：streaming response（SSE） — 讓使用者看到 LLM 邊想邊打字
- **L8**：把 MCP server 包 Docker + 橫向擴展部署
