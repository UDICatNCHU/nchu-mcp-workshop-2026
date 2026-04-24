#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""教授搜尋工具 — Lab 2 的完整實作。

兩支工具：
  - search_teachers(keyword, limit)  依關鍵字（姓名／職稱／研究領域）搜尋
  - get_teacher_detail(name)         取得指定教授完整資料
"""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("teachers_tool")

_DATA_FILE = Path(__file__).parent / "data" / "teachers.json"


def _load() -> list[dict]:
    if not _DATA_FILE.exists():
        return []
    with open(_DATA_FILE, encoding="utf-8") as f:
        return json.load(f).get("teachers", [])


TEACHERS: list[dict] = _load()


@mcp.tool()
def search_teachers(keyword: str, limit: int = 5) -> str:
    """依關鍵字搜尋資工系教授（可搜姓名、職稱、或研究領域）。

    使用情境：使用者詢問某領域的教授、某位教授、或某職稱的教授時呼叫。

    Args:
        keyword: 搜尋關鍵字（例如「電腦視覺」、「張」、「副教授」、「NLP」）。
        limit: 最多回傳幾筆，預設 5。

    回傳：符合條件的教授清單 JSON；若無結果則回空 list。
    """
    k = keyword.lower().strip()
    matches = [
        t for t in TEACHERS
        if k in t["name"].lower()
        or k in t["title"].lower()
        or any(k in area.lower() for area in t.get("areas", []))
    ]
    limit = max(1, min(int(limit), 50))
    return json.dumps(matches[:limit], ensure_ascii=False, indent=2)


@mcp.tool()
def get_teacher_detail(name: str) -> str:
    """取得指定教授的完整資訊（email、辦公室、研究領域）。

    使用情境：使用者問某位教授的聯絡方式或完整資料時呼叫。
    通常在 search_teachers 找到候選名單後再呼叫。

    Args:
        name: 教授姓名（完整中文姓名）。
    """
    for t in TEACHERS:
        if t["name"] == name:
            return json.dumps(t, ensure_ascii=False, indent=2)
    return json.dumps({"error": f"找不到教授：{name}"}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
