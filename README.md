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
| 4 | 50 min | 動手做（mini-project 實作） | `04-hands-on-lab.pptx`（15 張）+ `04-hands-on-lab.md` + `mini-project/` + `infra/` |
| 5 | 10 min | 實務考量（收尾） | `05-practical-considerations.md` + `haiku-alignment-report.pptx` + `haiku-alignment-animation.html` |

## Repo 結構

```
├── 01–03-*.pptx / *-animation.html    # 講課用投影片與動畫
├── 04-hands-on-lab.md / .pptx         # 第四段動手做 landing page + 講師開場 15 張
├── 05-practical-considerations.md     # 第五段收尾（規模／品質／模型／成本）
├── mini-project/                      # 學員端 hands-on：Express + FastMCP + 極簡 UI
│   ├── backend-node/, mcp-server-py/, web/
│   ├── docs/labs/                     # L1–L3 實作手冊
│   ├── docs/benchmarks/               # 2026-04-24 Claude vs Gemma4 實驗記錄
│   ├── scripts/                       # Claude vs 本地模型 對比腳本
│   └── setup.sh                       # 環境預檢
├── course-ta-agent/                   # 課程 TA Agent（學員直接問問題的 web bot）
│   ├── backend-node/                  # Express + Claude（mirror mini-project 架構）
│   ├── mcp-server-py/                 # FastMCP — 4 支 tool（segment/search/lab/source）
│   │   └── data/                      # 由 tools/extract-pptx-to-md.py 產出
│   ├── web/                           # 簡易 chat UI + 範例題目
│   └── README.md                      # 啟動 + 維護
├── infra/                             # 工作坊主辦端：vLLM 啟動腳本
└── tools/
    ├── gen-04-slides.py               # 第四段 .pptx 程式化產生
    ├── extract-pptx-to-md.py          # 把 6 個 pptx 抽成 md，餵 course-ta-agent
    └── sync-to-drive.sh               # rclone 同步教材到 Google Drive（需先 rclone config）
```

## 兩個可跑的子專案

### `mini-project/` — 工作坊 hands-on 主場

學員在 Segment 4 跟著做的 demo：Express + Claude + FastMCP + 極簡 chat UI。3 支教學工具（hello / teachers / weather）+ 1 支 L3 練習 stub（arxiv）。

```bash
cd mini-project
cp .env.example .env && vim .env       # 填 ANTHROPIC_API_KEY
./setup.sh                             # 5/5 ✅
cd backend-node && npm start           # → http://localhost:3000
```

詳見 [`mini-project/README.md`](mini-project/README.md)。

### `course-ta-agent/` — 課程小助教

工作坊現場，學員開 URL 直接問問題：「Segment 2 在講什麼？」「L1 Step 3 怎麼改 docstring？」「llm-client.js 那個 for-loop 解釋一下」。

架構刻意 mirror `mini-project/` —— 學員看完 Segment 4 投影片後可以打開 `course-ta-agent/backend-node/llm-client.js`，看到跟剛剛投影片裡完全一樣的 20 行 agent loop。

4 支 MCP tool：
- `get_segment(num)` — 取課程某一段內容
- `search_course(query)` — 全文搜尋
- `get_lab_handout(lab)` — Lab 手冊
- `read_mini_project_file(path)` — 沙盒讀程式碼

```bash
# 先抽課程內容（每次 .pptx 改完都要重跑）
uv run --with python-pptx python3 tools/extract-pptx-to-md.py

# 啟動 agent
cd course-ta-agent
cp .env.example .env && vim .env       # 填 ANTHROPIC_API_KEY
./setup.sh                             # 5/5 ✅
cd backend-node && npm start           # → http://localhost:3001
```

⚠ 公開暴露給學員前，務必先做 rate limit + 認證 + `.env` deny-list（詳見 review 結果）。詳見 [`course-ta-agent/README.md`](course-ta-agent/README.md)。

## 風格規範

- 配色：Ocean Gradient — Navy `#1E2761`、Deep Blue `#065A82`、Teal `#1C7293`；橘色 accent `#E8793A`
- 字型：Arial Black（標題）／ Calibri（內文）／ Consolas（程式碼）
- 簡報以 `.pptx` 產出；動畫以單檔 `.html` 產出（可直接投影、無外部依賴）
- 第四、五段以 `.md` 產出；動手部分以可跑的 `mini-project/` + `course-ta-agent/` 呈現

## 目前進度

- 第一段：`01-why-mcp.pptx`（21 張）初稿完成
- 第二段：`02-how-mcp-works.pptx`（20 張）+ 2 動畫初稿完成
- 第三段：`03-agentic-tool-loop.pptx`（20 張）+ sonnet 動畫初稿完成
- 第四段（動手做）：`04-hands-on-lab.pptx`（**15 張**，code-truth 對齊 mini-project）+ `04-hands-on-lab.md` + 完整可跑 `mini-project/`（28 檔 + 三關 Lab 手冊）
- 第五段（實務考量收尾）：`05-practical-considerations.md` 完成（四大支柱：規模／品質／模型／成本）
- **`course-ta-agent/`：完成**（4 工具、~70% reuse mini-project、Boot 驗證 OK；公開部署前需補 rate limit + 認證）
- `infra/`：Gemma 4 / Qwen 2.5-Coder vLLM 啟動腳本完成
