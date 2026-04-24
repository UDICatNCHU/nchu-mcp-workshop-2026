# CLAUDE.md

This file provides guidance to Claude Code / Claude Agent SDK clients when working on this repository.

## 本 repo 目的

這是一份「三小時 MCP 入門工作坊」的教材集散地，受眾為大專院校教師（非必要為資工背景）。所有內容以 [NCHU AI 學伴（UDICatNCHU/claude-mcp-project）](https://github.com/UDICatNCHU/claude-mcp-project) 作為實際案例。

原始素材於 2026-04-24 從 `claude-mcp-project/teaching-materials/` 搬出、獨立成本 repo，便於獨立版控與分享。

## 受眾假設

- 聽眾熟悉 LLM 使用經驗，但對 RAG / Tool Use / MCP 的差異尚未建立清楚的心智模型
- 聽眾不一定每天寫程式，技術細節需「概念為主、關鍵程式片段佐證」，避免逐行解釋
- 期望聽眾課後能自行判斷：自己的研究／教學情境，該選 RAG、Tool Use 還是 MCP

## 課程結構（180 min）

| 段落 | 時間 | 主題 | 主要檔案 | 狀態 |
|------|------|------|---------|------|
| 第一段 | 50 min | **Why MCP** | `01-why-mcp.pptx` | 🔨 製作中 |
| 第二段 | 50 min | **How MCP Works** | `02-how-mcp-works.pptx`、`mcp-architecture-animation.html`、`mcp-connection-animation.html` | 🔨 初稿完成 |
| 休息 | 10 min | | | |
| 第三段 | 50 min | **Agentic Tool Loop** | `03-agentic-tool-loop.pptx`、`sonnet-flow-running-example.html`、`sonnet-running-example.pptx` | 🔨 初稿完成 |
| 第四段 | 40 min | **實務考量** | `04-practical-considerations.pptx`（待新建）、`haiku-alignment-report.pptx`、`haiku-alignment-animation.html` | ⬜ 待開始 |
| Q&A | 20 min | 問答 + 動手指引 | `05-resource-pack.md`（待新建） | ⬜ 待開始 |

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

### 第四段：實務考量（40 min）
- 多模型 fallback 策略（Claude → Gemini → ChatGPT → Ollama）
- Haiku alignment 優化（few-shot + 格式規範，省 73% 成本）
- 33 個 MCP 工具的分類管理與 config 系統
- 搭配素材：`haiku-alignment-report.pptx`、`haiku-alignment-animation.html`

### Q&A + 動手指引（20 min）
- 課後資源包：環境建置步驟、推薦閱讀、簡易 MCP Server 範例

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
- 草稿 / 筆記：`course-notes-*.md`

## 相關 repo

- 原始應用：[UDICatNCHU/claude-mcp-project](https://github.com/UDICatNCHU/claude-mcp-project) — 興大 AI 學伴（Claude + MCP 的 web chat 介面，33 個 MCP 工具）
