# NCHU MCP Workshop 2026

給大專院校教師的三小時 MCP 入門工作坊 —— 不需要資工背景，跟著做就能擁有一個自己領域的 AI 助理。

所有內容以 [NCHU AI 學伴](https://eduxplore.nlpnchu.org) 作為實際案例。

## 課程結構（總 160 min；安排在 3 小時時段）

| 段落 | 時間 | 主題 | 檔案 |
|------|------|------|------|
| 1 | 20 min | Why MCP | `01-why-mcp.pptx`（21 張）+ Why MCP 概念長片（2:35, Manim → YouTube） |
| 2 | 20 min | How MCP Works | `02-how-mcp-works.pptx`（24 張，附錄含 REST vs JSON-RPC）+ handshake 影片（2:14, YouTube）|
| — | 10 min | 休息 | |
| 3 | 30 min | Agentic Tool Loop | `03-agentic-tool-loop.pptx`（8 張，A2 cut）+ Agentic Loop 影片（1:07, YouTube） |
| 4 | 70 min | 動手做（mini-project 實作） | `04-hands-on-lab.pptx`（12 張）+ `04-hands-on-lab.md` + `mini-project/`（含 Colab）+ `infra/` |
| 5 | 10 min | 實務考量（收尾） | `05-practical-considerations.md` + `haiku-alignment-report.md` |

## Repo 結構

```
├── 04-hands-on-lab.md                 # 第四段動手做 landing page（學員入口）
├── 05-practical-considerations.md     # 第五段收尾（規模／品質／模型／成本）
├── haiku-alignment-report.md          # Haiku 優化報告（第五段延伸閱讀）
│
├── slides/                            # 所有講課投影片 .pptx（01–05）
├── videos/                            # 影片生產檔（Manim *.py + *-preview.mp4 + *-youtube.md）
├── scripts/                           # 講師用：live-demo 腳本 + 課堂筆記草稿
│
├── mini-project/                      # 學員端 hands-on：Express + FastMCP + 極簡 UI
│   ├── backend-node/, mcp-server-py/, web/
│   ├── colab/workshop.ipynb           # 零安裝 Colab 版（雲端跑完整 3 層 + L1/L2/L3）
│   ├── docs/labs/                     # L1–L3 實作手冊
│   └── setup.sh                       # 環境預檢
├── infra/                             # 工作坊主辦端：vLLM 啟動腳本
├── docs/                              # GitHub Pages landing page
└── tools/                             # 投影片生成腳本（共用 lib_newstyle.py 設計系統）
    ├── lib_newstyle.py                # 設計系統（violet 色票、版面 primitives）
    ├── build-0X-slides.py             # 各段 .pptx 程式化產生 → 寫入 slides/
    └── sync-to-drive.sh               # rclone 同步教材到 Google Drive
```

> **影片**：Manim 渲染的 `.mp4`（已上 YouTube）；早期的 `*.html` 互動動畫已全部移除。

## 可跑的 hands-on：`mini-project/`

學員在 Segment 4 跟著做的 demo：Express + Claude + FastMCP + 極簡 chat UI。5 支教學工具（hello / teachers / weather / library / course）+ 1 支 L3 練習 stub（arxiv）。`library` 即時查圖書館館藏（免 key 外部 API），`course` 查 3018 門真實課程（大資料集搜尋示範）。

**最簡單：零安裝用 Colab**（課堂推薦）
[▶ Open in Colab](https://colab.research.google.com/github/UDICatNCHU/nchu-mcp-workshop-2026/blob/main/mini-project/colab/workshop.ipynb) — 瀏覽器裡一步步跑完整 3 層 + L1/L3，Mac/Windows 體驗一致。

**在自己電腦跑：**
```bash
cd mini-project
cp .env.example .env && vim .env       # 填 ANTHROPIC_API_KEY
./setup.sh                             # 5/5 ✅
cd backend-node && npm start           # → http://localhost:3000
```

詳見 [`mini-project/README.md`](mini-project/README.md)。

## 投影片怎麼產生

所有 `.pptx` 由 `tools/build-0X-slides.py` 用 python-pptx 程式化生成（共用 `tools/lib_newstyle.py` 設計系統），輸出到 `slides/`。改投影片改腳本、重跑即可，不手動編輯 .pptx：

```bash
uv run --with python-pptx python3 tools/build-01-slides.py   # → slides/01-why-mcp.pptx
```
