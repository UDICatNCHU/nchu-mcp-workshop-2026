# Lab 2 — 加一支有參數的搜尋工具（40 分鐘）

## 🎯 目標

在 L1 的基礎上，新增**第二支工具** `search_xxx(keyword: str, limit: int)`，支援關鍵字搜尋。

做完這關你會理解：
1. Python **type hints 如何自動變成 JSON Schema** 給 LLM 看
2. LLM 怎麼決定「要呼叫哪支工具 + 傳什麼參數」
3. 兩支工具協作（先 `search` 找到候選、再 `get_detail` 取完整資訊）
4. 多個 MCP server 並存的 config 模式

## 前置

- 完成 L1（有你自己的資料）
- 建議準備一份**列表型**資料（10-50 筆），而非單一物件。範例：
  - 實驗室成員清單
  - 你教的課程清單
  - 你讀過的 paper 清單
  - 系所的教授清單

## Steps

### Step 1（5 分鐘）— 準備列表資料

建立 `mcp-server-py/data/teachers.json`（或你的領域資料）：

```json
{
  "metadata": { "source": "NCHU 資工系官網", "updated": "2025-11-15" },
  "teachers": [
    {
      "name": "張小明",
      "title": "教授",
      "areas": ["機器學習", "電腦視覺"],
      "email": "ming@nchu.edu.tw",
      "office": "資電 601",
      "homepage": "https://..."
    },
    {
      "name": "李小華",
      "title": "副教授",
      "areas": ["自然語言處理", "大型語言模型"],
      "email": "hua@nchu.edu.tw",
      "office": "資電 523",
      "homepage": "https://..."
    }
    // ... 至少放 10 筆，讓搜尋有意義
  ]
}
```

### Step 2（15 分鐘）— 新增一個 MCP server

建立 `mcp-server-py/teachers_tool.py`：

```python
#!/usr/bin/env python3
"""教授搜尋工具 — Lab 2 範例"""

from __future__ import annotations

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("teachers_tool")

_DATA_FILE = Path(__file__).parent / "data" / "teachers.json"

def _load() -> list[dict]:
    with open(_DATA_FILE, encoding="utf-8") as f:
        return json.load(f).get("teachers", [])

TEACHERS: list[dict] = _load()


@mcp.tool()
def search_teachers(keyword: str, limit: int = 5) -> str:
    """依關鍵字搜尋教授，可用姓名、職稱或研究領域。

    使用情境：使用者想找「做 X 的老師」或「叫 X 的教授」時呼叫。

    Args:
        keyword: 搜尋關鍵字（例如「電腦視覺」、「張」、「副教授」）。
        limit: 最多回傳幾筆，預設 5 筆。

    回傳：符合條件的教授列表 JSON，若無結果則回傳空 list。
    """
    k = keyword.lower().strip()
    matches = [
        t for t in TEACHERS
        if k in t["name"].lower()
        or k in t["title"].lower()
        or any(k in area.lower() for area in t.get("areas", []))
    ]
    return json.dumps(matches[:limit], ensure_ascii=False, indent=2)


@mcp.tool()
def get_teacher_detail(name: str) -> str:
    """取得指定教授的完整資訊（含 email、office、homepage）。

    使用情境：使用者詢問特定教授的聯絡方式或詳細資料時呼叫。
    通常在 search_teachers 之後使用。

    Args:
        name: 教授姓名（完整）。
    """
    for t in TEACHERS:
        if t["name"] == name:
            return json.dumps(t, ensure_ascii=False, indent=2)
    return json.dumps({"error": f"找不到教授：{name}"}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Step 3（5 分鐘）— 註冊新 server

編輯 `config.json`，加入第二個 entry：

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
    }
  }
}
```

> **設計觀察**：為何不把 `search_teachers` 塞進 `hello_tool.py`？技術上可以。但拆開的好處是：
> 1. 每個 MCP server 是獨立 process，各自 crash 不互相影響
> 2. 可獨立部署（未來某個 tool 要跑 GPU inference、某個要連 DB）
> 3. 團隊分工：你寫一個 server、學生寫一個，合併時改 config.json 即可

### Step 4（10 分鐘）— 重啟並測試「工具選擇」能力

重啟 `npm start`，應看到：

```
✓ hello_tool → get_lab_info
✓ teachers_tool → search_teachers, get_teacher_detail
```

在瀏覽器依序問：

| 問題 | 預期行為 |
|------|---------|
| `有誰在做電腦視覺？` | 呼叫 `search_teachers` 傳 `keyword="電腦視覺"` |
| `張小明老師 email？` | 呼叫 `get_teacher_detail` 傳 `name="張小明"` |
| `有做 CV 的老師嗎？他們的 email？` | **兩次** tool call：先 search 再 detail |
| `研究室招生名額？` | 呼叫 `get_lab_info`（L1 那支） |
| `今天天氣？` | 不呼叫任何工具，直接回答 |

**Terminal log 裡你會看到 Claude 真的在「選工具」**。這就是 agent behavior。

## ✅ Verify

最後那個「先 search 再 detail」的問題是本關核心驗收：
- [ ] log 應顯示 **兩行** `[tool_use]`
- [ ] 第一次傳 `keyword`，第二次傳 `name`（名字取自第一次的結果）
- [ ] Claude 自主決定參數，你沒寫任何 orchestration 程式碼

如果成功，你剛剛**看到了 agent loop 的本質**：LLM 是 planner，tools 是 effectors，中間那個 `llm-client.js` 的 20 行 while loop 就是 runtime。

## 🐛 Common Pitfalls

| 症狀 | 原因 | 解法 |
|------|------|------|
| `search_teachers` 一直不被叫 | docstring 沒寫「使用情境」 | 明確寫：「當使用者想找 X 時呼叫」 |
| Claude 傳錯參數型別 | Python type hint 寫錯（用 `str` 但標了 `int`） | `limit: int = 5` 會生成 integer schema |
| `limit` 參數被 ignore | docstring 沒解釋 | 加上 `Args: limit: 最多幾筆` |
| 工具名衝突 | 兩個 server 有同名函式 | 工具名需全域唯一 |
| 第二支工具啟動失敗 | config.json 格式錯 | `python3 -m json.tool config.json` |

## 🚀 Stretch Goals

1. **加 Optional 參數**：`search_teachers(keyword: str, department: str | None = None, limit: int = 5)`，觀察 Claude 會不會主動填 department
2. **複合條件**：改成支援多關鍵字 `search(keywords: list[str])`，看 type hint 產生的 schema
3. **模糊比對**：用 `difflib.get_close_matches` 支援錯字
4. **中英雙語**：docstring 寫英文，看效果差異
5. **排序參數**：加 `sort_by: Literal["name", "title"]` — 測試 LLM 是否懂 enum schema
6. **壓力測試**：把 teachers 擴充到 300 筆，問「做 AI 的教授」看 Claude 會不會呼叫多次取全部，還是設 `limit=10` 取前幾名（觀察它的推理）

## 🤔 Reflection

1. 為什麼 `docstring` 比參數名本身重要？（Hint：LLM 看不到你的變數命名美學）
2. 如果兩個工具的 description 寫得太像（例如 `search_teachers` vs `find_teachers`），會發生什麼？
3. 真實系統若有 **50 支工具**（像正式版 AiLearningMate 有 239 支），Claude 還能準確挑對嗎？有哪些解法？（→ Advanced topic: tool routing / retrieval）
4. 如果學生作業要交一個 5 工具 agent，你會怎麼設計 rubric？
   - 工具數量？docstring 品質？是否有 orchestration？錯誤處理？

---

**下一關（課後自修）**：L3 呼叫外部 API（weather/arxiv）、L4 有副作用的工具（human-in-the-loop）、L5 寫 MCP 工具的 unit test。
