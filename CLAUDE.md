# CLAUDE.md

This file provides guidance to Claude Code / Claude Agent SDK clients when working on this repository.

## 本 repo 目的

這是一份「三小時 MCP 入門工作坊」的教材集散地，受眾為大專院校教師（非必要為資工背景）。所有內容以 [NCHU AI 學伴（UDICatNCHU/claude-mcp-project）](https://github.com/UDICatNCHU/claude-mcp-project) 作為實際案例。

原始素材於 2026-04-24 從 `claude-mcp-project/teaching-materials/` 搬出、獨立成本 repo，便於獨立版控與分享。

## 受眾假設

- 聽眾熟悉 LLM 使用經驗，但對 RAG / Tool Use / MCP 的差異尚未建立清楚的心智模型
- 聽眾不一定每天寫程式，技術細節需「概念為主、關鍵程式片段佐證」，避免逐行解釋
- 期望聽眾課後能自行判斷：自己的研究／教學情境，該選 RAG、Tool Use 還是 MCP

## 課程結構（總 220 min，含 10 min 休息）

| 段落 | 時間 | 主題 | 主要檔案 | 狀態 |
|------|------|------|---------|------|
| 第一段 | 50 min | **Why MCP** | `01-why-mcp.pptx` | 🔨 製作中 |
| 第二段 | 50 min | **How MCP Works** | `02-how-mcp-works.pptx`、`mcp-architecture-animation.html`、`mcp-connection-animation.html` | 🔨 初稿完成 |
| 休息 | 10 min | | | |
| 第三段 | 50 min | **Agentic Tool Loop** | `03-agentic-tool-loop.pptx`、`sonnet-flow-running-example.html`、`sonnet-running-example.pptx` | 🔨 初稿完成 |
| 第四段 | 50 min | **動手做（mini-project 實作）** | `04-hands-on-lab.pptx`、`04-hands-on-lab.md` + `mini-project/` + `infra/` | ✅ 完成 |
| 第五段 | 10 min | **實務考量（收尾）** | `05-practical-considerations.md`、`haiku-alignment-report.pptx`、`haiku-alignment-animation.html` | ✅ 完成（md 版本） |

## 各段內容規劃

### 第一段：Why MCP（50 min）
- LLM 擅長的事（語言理解、推理、程式碼生成、知識回答）
- LLM 的天花板（知識截止、無私有資料、不能執行動作、幻覺）
- 策略 A：RAG — 概念 + 流程圖 + 概念程式碼 + 優缺點
- 策略 B：Tool Use — 概念 + 流程圖 + Claude API 範例 + 優缺點
- Tool Use 的 N×M 痛點（每個 App × 每個資料源都要個別整合）
- 策略 C：MCP — 統一協定解耦，N+M 模式
- **三者深入比較**（比較表 + 適用場景分析 + 可混用說明，5+ 頁）
- MCP 核心概念（Host / Client / Server / Tool 四大角色）
- MCP 通訊協定（JSON-RPC 2.0 範例）
- 興大 AI 學伴案例引子（33 工具、9 大分類）

### 第二段：How MCP Works（50 min）
- JSON-RPC 協定深入（request / response / notification 格式）
- Server 生命週期管理（spawn → initialize → ready → shutdown）
- Tool 註冊與描述格式（JSON Schema、description 對 LLM 的重要性）
- Client 如何把工具清單餵給 LLM（system prompt injection）
- 搭配動畫：`mcp-architecture-animation.html`、`mcp-connection-animation.html`

### 第三段：Agentic Tool Loop（50 min）
- 完整查詢流程 walk-through（使用者提問 → 最終回覆）
- LLM 自主選工具（`tool_use` block → `tool_result` → 多輪迭代）
- `maxIterations` 限制與最後一輪強制回覆機制
- Live Demo：現場操作系統，對照動畫逐步解說
- 搭配素材：`sonnet-flow-running-example.html`、`sonnet-running-example.pptx`

### 第四段：動手做（50 min，hands-on 主場）

現版 `04-hands-on-lab.md` 是學員端 landing page，指向可跑的 `mini-project/`。`04-hands-on-lab.pptx`（12 張）是**現場講師開場用**的投影片，涵蓋本節目標、時間配置、架構回顧、Quick Start、L1 四步驟分解、卡點速查、收尾鋪陳 Segment 5；由 `tools/gen-04-slides.py` 以 python-pptx 自動生成，視覺遵循 repo 的 Ocean Gradient 風格規範。

**作為工作坊的 hands-on 主場**，學員現場完成 L1（換自己領域的 JSON），讓 Segment 1–3 的概念在自己電腦上發生。

**50 分鐘時間配置**：
- 0–10 min：講師 demo + 學員同步 `setup.sh`
- 10–20 min：L1 Step 1–2（觀察 + 換 JSON）
- 20–35 min：L1 Step 3–4（改 docstring + 重啟驗證）
- 35–45 min：交叉展示 — 幾位老師用自己領域資料 demo
- 45–50 min：Q&A + 鋪陳 Segment 5

三關 Lab 路徑：
- **L1**：換 JSON 做你領域的助理（**課堂現場必做**）
- **L2**：加一支有參數的搜尋工具（課後自修）
- **L3**：呼叫外部 API（課後自修）

Workshop 現場可連 NCHU vLLM 端點（`infra/serve-*.sh` 提供 Gemma 4 / Qwen Coder）。

### 第五段：實務考量 收尾（10 min）

現版 `05-practical-considerations.md` 結構為「四大支柱」，**順序從剛做的 mini-project 往外擴**（Scale → Quality → Model → Cost）：

- **§1 Scale 質變**（3 tools → 239 tools 的五個質變：context 爆量 / 語意混淆 / 多輪 context / 安全 / observability）
- **§2 Tool-calling 品質陷阱**（docstring 設計、邊界防禦、錯誤當資料、Gemma 4 thinking marker strip）
- **§3 模型選擇**（Task-complexity gradient；引 benchmark 佐證 Gemma 4 在 tool-calling 任務打平 Claude；multi-provider adapter）
- **§4 成本**（10 人 3 小時 workshop 真實帳、prompt caching、失控情境、Anthropic Console 護欄、本地 vs 雲端長期帳）

**10 分鐘塞不下四支柱**。講師於現場依聽眾屬性**擇一深入 ~7 min**，其餘三節各一句帶過，最後 ~2 min Q&A。md 保留完整四節供課後閱讀。

搭配素材：`haiku-alignment-report.pptx`、`haiku-alignment-animation.html`（可作為 §4 成本中 Haiku alignment 的延伸閱讀）。

## 教材風格規範

- 配色：Ocean Gradient — Navy `#1E2761` / Deep Blue `#065A82` / Teal `#1C7293`；橘色 accent `#E8793A`
- 字型：Arial Black（標題）／ Calibri（內文）／ Consolas（程式碼）
- 簡報以 `.pptx` 產出；動畫以單檔 `.html` 產出（可直接投影、無外部依賴）
- 技術深度：概念為主，穿插關鍵程式片段；RAG / Tool Use / MCP 比較做深入版（5+ 頁）
- 每段至少 1 個來自 NCHU AI 學伴 repo 的具體案例（例如 33 工具分類、Haiku alignment、agentic loop）
- 程式片段以說明「概念」為主，避免逐行解釋；複雜流程用動畫或圖示取代文字

## 檔案命名慣例

- 簡報：`0X-主題.pptx`，直接放在 repo 根目錄
- 動畫：`主題-animation.html`，直接放在 repo 根目錄
- 教材 md：`0X-主題.md`（Segment 4、5 以 md 為主；Segment 4 另有配套 pptx 作為現場講師開場使用）
- 投影片生成腳本：`tools/gen-0X-slides.py`（用 python-pptx 程式化生成，確保視覺風格統一且可重現）
- 草稿 / 筆記：`course-notes-*.md`
- 可跑 code：集中在 `mini-project/` 子目錄，保留階層結構；`setup.sh` 位於其 root
- 工作坊主辦端 infra：集中在 `infra/`，學員端不需要碰

## Repo 結構

```
repo root/
├── 01–03 *.pptx / *-animation.html    講課投影片與動畫（學員端）
├── 04-hands-on-lab.md                 第四段動手做 landing page（現場實作主場）
├── 04-hands-on-lab.pptx               第四段講師開場投影片（12 張，由 tools/ 產出）
├── 05-practical-considerations.md     第五段實務考量收尾
├── haiku-alignment-*                  Haiku 優化報告（第五段 §4 引用）
├── sonnet-*-example.*                 Sonnet 實例（第三段引用）
├── course-notes-draft.md              個人筆記草稿
├── tools/                             投影片生成腳本
│   └── gen-04-slides.py               uv run --with python-pptx 產出 04-hands-on-lab.pptx
├── mini-project/                      學員端 hands-on 可跑 code
│   ├── backend-node/                  Express + LLM client + MCP client
│   ├── mcp-server-py/                 4 支 FastMCP 工具（hello/teachers/weather/arxiv）
│   ├── web/                           極簡 vanilla JS chat UI
│   ├── scripts/                       Claude vs 本地模型 對比腳本
│   ├── docs/labs/                     L1–L3 Lab 手冊
│   ├── docs/benchmarks/               實驗記錄（2026-04-24）
│   └── setup.sh                       環境預檢
└── infra/                             工作坊主辦端 vLLM 啟動
    ├── serve-gemma.sh                 Gemma 4 31B 端點（port 8000）
    └── serve-qwen.sh                  Qwen 2.5-Coder 32B 端點（port 8001）
```

## 相關 repo

- 原始應用：[UDICatNCHU/claude-mcp-project](https://github.com/UDICatNCHU/claude-mcp-project) — 興大 AI 學伴（Claude + MCP 的 web chat 介面，~239 個 MCP 工具）

## 其他 CLAUDE.md（本機同步維護參考）

公開讀者可忽略本節。若您是 NCHU 內部開發者，本 repo 通常與 `AiLearningMate/` 並列為 sibling 目錄，本機會有另外兩份 CLAUDE.md 各司其職：

| 路徑（從本 repo 看） | 焦點 |
|------|------|
| `../AiLearningMate/CLAUDE.md` | NCHU AI 學伴 monorepo 總覽（claude-mcp-project + library + mini-project + qwen-coding）|
| `../AiLearningMate/library/CLAUDE.md` | `library/` sub-project 專屬：Python / uv / FastMCP 環境與工具分類，獨立於本 workshop 維護 |

三份 CLAUDE.md 各自作為其所在目錄的 Claude Code context；不互相衝突，只是工作 scope 不同。本機工作時可三份並讀，**公開發佈只有本檔**。
