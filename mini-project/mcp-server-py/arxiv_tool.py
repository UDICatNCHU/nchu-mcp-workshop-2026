#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arXiv 論文搜尋工具 — Lab 3 範例：呼叫外部 API。

示範重點：
  1. async def + httpx.AsyncClient — FastMCP 原生支援 async tools
  2. 呼叫真實 HTTP API（arXiv 的 Atom/XML 端點，免 API key）
  3. XML 解析（標準庫 xml.etree）
  4. 三層錯誤處理：timeout / HTTP error / XML parse
  5. 參數邊界檢查（limit 上下限）
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("arxiv_tool")

ARXIV_API = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
TIMEOUT_SECONDS = 15.0
MAX_LIMIT = 20


def _extract_entry(entry: ET.Element) -> dict[str, Any]:
    """把一個 Atom <entry> 轉成乾淨的 dict。"""
    def txt(tag: str) -> str:
        el = entry.find(f"atom:{tag}", ATOM_NS)
        return (el.text or "").strip() if el is not None else ""

    authors = [
        (a.text or "").strip()
        for a in entry.findall("atom:author/atom:name", ATOM_NS)
    ]
    links = {
        link.get("rel", ""): link.get("href", "")
        for link in entry.findall("atom:link", ATOM_NS)
    }
    # arxiv id 藏在 <id> URL 最後一段
    arxiv_id = txt("id").rsplit("/", 1)[-1]

    return {
        "id": arxiv_id,
        "title": " ".join(txt("title").split()),  # 去多餘換行空白
        "authors": authors,
        "published": txt("published")[:10],  # YYYY-MM-DD
        "summary": " ".join(txt("summary").split()),
        "abs_url": links.get("alternate", ""),
        "pdf_url": links.get("related", ""),
    }


@mcp.tool()
async def search_arxiv(keyword: str, limit: int = 5) -> str:
    """在 arXiv 搜尋近期論文。

    使用情境：使用者詢問學術論文、某研究主題的最新進展、或想找特定作者的論文時呼叫。

    Args:
        keyword: 搜尋關鍵字，**英文效果較好**（例如 "retrieval augmented generation"、
                 "transformer attention mechanism"、"author:Hinton"）。
        limit: 最多回傳幾篇，預設 5，最大 20。

    回傳：論文清單的 JSON，每筆包含 id / title / authors / published / summary /
    abs_url / pdf_url。無結果時回傳空 list。
    """
    limit = max(1, min(limit, MAX_LIMIT))

    params = {
        "search_query": f"all:{keyword}",
        "max_results": str(limit),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            resp = await client.get(ARXIV_API, params=params)
            resp.raise_for_status()
    except httpx.TimeoutException:
        return json.dumps(
            {"error": f"arXiv API 逾時（>{TIMEOUT_SECONDS}s），請稍後再試"},
            ensure_ascii=False,
        )
    except httpx.HTTPError as e:
        return json.dumps(
            {"error": f"arXiv API 錯誤：{type(e).__name__}: {e}"},
            ensure_ascii=False,
        )

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        return json.dumps(
            {"error": f"回應格式錯誤：{e}"}, ensure_ascii=False
        )

    papers = [_extract_entry(e) for e in root.findall("atom:entry", ATOM_NS)]
    return json.dumps(papers, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
