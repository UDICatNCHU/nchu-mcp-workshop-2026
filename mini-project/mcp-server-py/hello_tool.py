#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hello MCP Tool — 教學範例：英語自學中心資訊查詢。

這是一支最小可執行的 FastMCP 工具伺服器。
學生可複製此檔改成自己的工具：改 FastMCP 名稱、改 @mcp.tool 函式、改 JSON 資料。
"""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# 1. 建立 MCP 伺服器，名稱會顯示在 Client 端。
mcp = FastMCP("hello_tool")

# 2. 資料檔路徑（相對於本 .py 檔所在目錄）。
_DATA_FILE = Path(__file__).parent / "data" / "english_center.json"


def _load_data() -> dict:
    """模組載入時讀取 JSON 一次，後續工具呼叫直接用快取。"""
    if not _DATA_FILE.exists():
        return {}
    with open(_DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


INFO: dict = _load_data()


# 3. 用 @mcp.tool 把一般 Python 函式註冊成 MCP 工具。
#    docstring 會自動成為 LLM 看到的 tool description。
@mcp.tool()
def get_english_center_info() -> str:
    """取得中興大學英語自學暨檢定中心的完整資訊。

    回傳 JSON 字串，包含：名稱、開放時間、地點、設備、聯絡方式、注意事項。
    使用情境：使用者詢問英語自學中心相關問題時呼叫。
    """
    if not INFO:
        return json.dumps({"error": "資料檔不存在"}, ensure_ascii=False)
    return json.dumps(INFO, ensure_ascii=False, indent=2)


# 4. 用 stdio transport 啟動伺服器，讓 Node.js client 透過 stdin/stdout 溝通。
if __name__ == "__main__":
    mcp.run(transport="stdio")
