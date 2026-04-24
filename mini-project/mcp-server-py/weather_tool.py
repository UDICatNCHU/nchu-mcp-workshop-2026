#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Weather MCP Tool — 教學範例：天氣資訊查詢。

這是一支最小可執行的 FastMCP 工具伺服器。
學生可複製此檔改成自己的工具：改 FastMCP 名稱、改 @mcp.tool 函式、改 JSON 資料。
"""

from __future__ import annotations

import httpx

from mcp.server.fastmcp import FastMCP

# 1. 建立 MCP 伺服器，名稱會顯示在 Client 端。
mcp = FastMCP("weather_tool")


# 2. 用 @mcp.tool 把一般 Python 函式註冊成 MCP 工具。
#    docstring 會自動成為 LLM 看到的 tool description。
@mcp.tool()
def get_weather(city: str) -> str:
    """取得指定城市的單行天氣資訊。

    使用 wttr.in API 取得天氣資訊，格式為單行字串。
    使用情境：使用者詢問某城市天氣狀況時呼叫。
    """
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = httpx.get(url)
        response.raise_for_status()
        return response.text.strip()
    except httpx.RequestError as e:
        return f"無法取得天氣資訊: {e}"
    except httpx.HTTPStatusError as e:
        return f"無法取得天氣資訊: HTTP 錯誤 {e.response.status_code}"


# 3. 用 stdio transport 啟動伺服器，讓 Node.js client 透過 stdin/stdout 溝通。
if __name__ == "__main__":
    mcp.run(transport="stdio")
