#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Course TA — FastMCP server with 4 tools.

工具：
  - get_segment(num)              取得課程某一段（1–5）的完整內容
  - search_course(query, limit)   全文關鍵字搜尋整份課程材料
  - get_lab_handout(lab)          取得 Lab 手冊原文（L1/L2/L3/setup/benchmark）
  - read_mini_project_file(path)  讀 mini-project source code（沙盒）

學員資料來源：mcp-server-py/data/*.md（由 tools/extract-pptx-to-md.py 產生）
程式碼來源：../mini-project/  （只允許這個資料夾底下的檔案）
"""

from __future__ import annotations

import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("course_ta")

# ── 路徑常數 ──────────────────────────────────────────
_HERE = Path(__file__).parent.resolve()
_DATA_DIR = _HERE / "data"
_REPO_ROOT = _HERE.parent.parent.resolve()           # nchu-mcp-workshop-2026/
_MINI_PROJECT = (_REPO_ROOT / "mini-project").resolve()

# read_mini_project_file 沙盒設定
_ALLOWED_EXT = {
    ".py", ".js", ".mjs", ".cjs", ".jsx",
    ".ts", ".tsx", ".json", ".md", ".txt",
    ".html", ".css", ".sh", ".toml", ".yaml", ".yml",
    "",  # README 之類無副檔名的
}
_MAX_FILE_BYTES = 200_000   # 200 KB 上限，避免 uv.lock / lock files DoS
# Lock 檔通過 .json/.yaml 副檔名 allow-list 但對教學沒用，明確擋掉避免灌爆 LLM context
_DENIED_BASENAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock", "Gemfile.lock",
}

# segment number → list of glob patterns under data/
_SEGMENT_FILES = {
    1: ["01-*.md"],
    2: ["02-*.md"],
    3: ["03-*.md"],
    4: ["04-*.md"],
    5: ["05-*.md"],
}

# lab key → glob pattern
_LAB_FILES = {
    "L1":        ["lab-L1.md"],
    "L2":        ["lab-L2.md"],
    "L3":        ["lab-L3.md"],
    "setup":     ["04-hands-on-lab.md"],   # Segment 4 landing page 包含 setup 流程
    "benchmark": ["benchmark-*.md"],
}


def _read_files(patterns: list[str]) -> str:
    """讀符合 glob 的所有檔案，串成單一字串（每檔前面加 ## filename）。"""
    chunks: list[str] = []
    for pat in patterns:
        for p in sorted(_DATA_DIR.glob(pat)):
            chunks.append(f"## {p.name}\n\n{p.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(chunks) if chunks else ""


# ── Tool 1: get_segment ──────────────────────────────
@mcp.tool()
def get_segment(num: int) -> str:
    """取得課程某一段（1–5）的完整內容（投影片文字 + 補充 md）。

    使用情境：學員問「Segment X 在講什麼」「RAG 那段給我看」「3 講的 agentic loop 是什麼」時呼叫。

    Args:
        num: 段落編號，1–5。
            1 = Why MCP（RAG / Tool Use / MCP 三策略比較）
            2 = How MCP Works（JSON-RPC / 連線生命週期）
            3 = Agentic Tool Loop（多輪迭代）
            4 = Hands-on Lab（mini-project 實作）
            5 = Practical Considerations（Scale / Quality / Model / Cost）
    """
    if num not in _SEGMENT_FILES:
        return f"Error: segment 必須是 1–5，收到 {num}"
    content = _read_files(_SEGMENT_FILES[num])
    if not content:
        return f"找不到 segment {num} 的資料檔。請先在 repo root 跑 tools/extract-pptx-to-md.py。"
    return content


# ── Tool 2: search_course ────────────────────────────
@mcp.tool()
def search_course(query: str, limit: int = 5) -> str:
    """關鍵字全文搜尋整份課程材料（5 段 + Lab + benchmark）。

    使用情境：學員問模糊問題、跨段落比較、不確定哪一段時呼叫。
    例：「N×M 痛點是什麼」「Gemma 4 跟 Claude 比誰快」「docstring 怎麼寫」。

    回傳每筆 match 的：來源檔名、行號、該段落（前後 2 行）。

    Args:
        query: 中英關鍵字（不分大小寫）。
        limit: 最多回幾筆，預設 5、上限 20。
    """
    q = query.lower().strip()
    if not q:
        return "Error: query 不能為空"
    limit = max(1, min(int(limit), 20))

    matches: list[str] = []
    for p in sorted(_DATA_DIR.glob("*.md")):
        lines = p.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if q in line.lower():
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                snippet = "\n".join(lines[start:end])
                matches.append(f"### {p.name}:L{i+1}\n```\n{snippet}\n```")
                if len(matches) >= limit:
                    break
        if len(matches) >= limit:
            break

    if not matches:
        return f"沒找到「{query}」相關內容。試試別的關鍵字、或用 search_course 列出大主題。"
    return "\n\n".join(matches)


# ── Tool 3: get_lab_handout ──────────────────────────
@mcp.tool()
def get_lab_handout(lab: str) -> str:
    """取得 Lab 手冊原文。

    使用情境：學員執行 hands-on 時的步驟細節問題。
    例：「L1 Step 3 docstring 怎麼改」「setup.sh 卡住」「Gemma vs Claude benchmark」。

    Args:
        lab: 'L1' / 'L2' / 'L3' / 'setup' / 'benchmark'。
    """
    key = lab.strip()
    if key not in _LAB_FILES:
        return f"Error: lab 必須是 {list(_LAB_FILES.keys())}，收到 '{lab}'"
    content = _read_files(_LAB_FILES[key])
    if not content:
        return f"找不到 {lab} 的手冊檔。請在 repo root 跑 tools/extract-pptx-to-md.py。"
    return content


# ── Tool 4: read_mini_project_file ───────────────────
@mcp.tool()
def read_mini_project_file(path: str) -> str:
    """讀 mini-project source code（沙盒：只允許 mini-project/ 底下檔案）。

    使用情境：學員問程式碼細節時呼叫。
    例：「llm-client.js 那個 for-loop 在做什麼」「config.json 長怎樣」「teachers_tool.py 的 search 邏輯」。

    Args:
        path: 相對於 mini-project/ 的路徑，例如 'backend-node/llm-client.js'、
              'mcp-server-py/teachers_tool.py'、'config.json'、'README.md'。
    """
    # 1. 輸入 sanity（NULL byte / 過長）
    if "\x00" in path or len(path) > 512:
        return "Error: 路徑含非法字元或過長"

    rel = path.strip().lstrip("/")
    if not rel:
        return "Error: path 不能為空"

    # 2. Symlink 防護：每一層 component 都檢查（避免 cool-link/file 走後門）
    cumulative = _MINI_PROJECT
    for part in Path(rel).parts:
        cumulative = cumulative / part
        if cumulative.is_symlink():
            return f"Error: 路徑含 symlink：{part}"

    # 3. 沙盒：resolve 後必須仍在 mini-project/ 底下
    try:
        target = (_MINI_PROJECT / rel).resolve()
        target.relative_to(_MINI_PROJECT)
    except ValueError:
        return f"Error: 路徑超出 mini-project/ 沙盒範圍：{path}"

    # 4. 隱藏檔/目錄（.env / .env.local / .git/ / .vscode/ / .ssh/ ...）一律擋
    rel_parts = target.relative_to(_MINI_PROJECT).parts
    if any(p.startswith(".") for p in rel_parts):
        return "Error: 拒絕讀取隱藏檔或目錄（.env / .git/ 等）"

    if not target.exists():
        return f"Error: 檔案不存在：mini-project/{rel}"
    if not target.is_file():
        return f"Error: 不是檔案：mini-project/{rel}"

    # 5. 副檔名 allow-list（取代原本的 binary deny-list — 預設拒絕、明確允許）
    if target.suffix.lower() not in _ALLOWED_EXT:
        return (
            f"Error: 不支援的副檔名 {target.suffix}（"
            f"允許：py / js / mjs / cjs / jsx / ts / tsx / json / md / sh / toml / yaml / html / css / txt）"
        )

    # 6. lock 檔擋掉（即使副檔名 allow-list 通過）
    if target.name in _DENIED_BASENAMES:
        return f"Error: lock 檔不開放讀取（{target.name}）；請看對應的 package.json / pyproject.toml"

    # 7. 大小上限（防 uv.lock / package-lock.json 灌爆 LLM context）
    size = target.stat().st_size
    if size > _MAX_FILE_BYTES:
        return f"Error: 檔案太大（{size} bytes，上限 {_MAX_FILE_BYTES}）。請指定更具體的檔案"

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: 無法以 UTF-8 讀取：mini-project/{rel}"

    # 加上行號，方便引用
    numbered = "\n".join(f"{i+1:4d}  {line}" for i, line in enumerate(content.splitlines()))
    return f"# mini-project/{rel}\n\n```\n{numbered}\n```"


# ── 啟動 ──────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
