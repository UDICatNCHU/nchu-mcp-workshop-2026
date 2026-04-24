# NCHU MCP Workshop 2026

三小時 MCP 入門工作坊教材，受眾為大專院校教師（非必要為資工背景）。

所有內容以 [NCHU AI 學伴](https://github.com/UDICatNCHU/claude-mcp-project) 作為實際案例。

## 課程結構（180 min）

| 段落 | 時間 | 主題 | 檔案 |
|------|------|------|------|
| 1 | 50 min | Why MCP | `01-why-mcp.pptx` |
| 2 | 50 min | How MCP Works | `02-how-mcp-works.pptx` + `mcp-architecture-animation.html` + `mcp-connection-animation.html` |
| — | 10 min | 休息 | |
| 3 | 50 min | Agentic Tool Loop | `03-agentic-tool-loop.pptx` + `sonnet-flow-running-example.html` |
| 4 | 40 min | 實務考量 | `04-practical-considerations.md` + `haiku-alignment-report.pptx` + `haiku-alignment-animation.html` |
| 5 | 20 min | Q&A + 動手指引 | `05-hands-on-lab.md` + `mini-project/` + `infra/` |

## Repo 結構

```
├── 01–03-*.pptx / *-animation.html    # 講課用投影片與動畫
├── 04-practical-considerations.md     # 第四段講義（成本／模型／品質／規模）
├── 05-hands-on-lab.md                 # 第五段動手指引 landing page
├── mini-project/                      # 學員端 hands-on：Express + FastMCP + 極簡 UI
│   ├── backend-node/, mcp-server-py/, web/
│   ├── docs/labs/                     # L1–L3 實作手冊
│   ├── docs/benchmarks/               # 2026-04-24 Claude vs Gemma4 實驗記錄
│   ├── scripts/                       # Claude vs 本地模型 對比腳本
│   └── setup.sh                       # 環境預檢
└── infra/                             # 工作坊主辦端：vLLM 啟動腳本
```

## 風格規範

- 配色：Ocean Gradient — Navy `#1E2761`、Deep Blue `#065A82`、Teal `#1C7293`；橘色 accent `#E8793A`
- 字型：Arial Black（標題）／ Calibri（內文）／ Consolas（程式碼）
- 簡報以 `.pptx` 產出；動畫以單檔 `.html` 產出（可直接投影、無外部依賴）
- 第四、五段以 `.md` 產出；動手部分以可跑的 `mini-project/` 呈現

## 目前進度

- 第一、二段：簡報初稿完成
- 第三段：pptx 初稿完成
- 第四段：`04-practical-considerations.md` 完成（四大支柱：成本／模型／品質／規模）
- 第五段：`05-hands-on-lab.md` 完成，並附完整可跑 `mini-project/`（28 檔 + 三關 Lab 手冊）
- `infra/`：Gemma 4 / Qwen 2.5-Coder vLLM 啟動腳本完成
