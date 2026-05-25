#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 04-hands-on-lab.pptx — Segment 4 hands-on 投影片。

設計成「投影片 ↔ Colab 交錯講」：鏡像 Colab「一個能力的誕生」六步敘事,
每一步一張概念投影片(講為什麼/概念 + takeaway)+ 一條「切到 Colab」提示,
讓講師講完概念就切到 Colab 現場做那一步。

程式化重生,共用 tools/lib_newstyle.py 設計系統(violet 主視覺)。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_newstyle import *  # noqa: E402,F401,F403

REPO = Path(__file__).resolve().parent.parent
PPTX = REPO / "slides" / "04-hands-on-lab.pptx"

TOTAL = 13

STEP_ACCENT = [VIOLET, ORANGE, TEAL, PINK, VIOLET, ORANGE]


# ── 共用：切到 Colab 提示列(固定 teal,讓聽眾學會「teal=去 Colab」)──
def demo_cue(s, text, y=6.55):
    callout_box(s, 0.85, y, 12, 0.6, "切到 Colab　" + text,
                accent=TEAL_DEEP, fill=TEAL_PASTEL, icon="▶", size=15)


def two_cards(s, left, right, y=2.55, h=3.4):
    """左右兩張 pastel card,各 (accent, fill, title, [lines])。"""
    for x, (accent, fill, title, lines) in zip((0.85, 6.95), (left, right)):
        pastel_card(s, x, y, 5.5, h, accent=accent, fill=fill, title=title, title_size=21)
        paras = [{"text": t, "font": FONT_BODY, "size": 15.5,
                  "color": INK_SOFT, "space_after": 8} for t in lines]
        _multi(s, x + 0.3, y + 0.95, 5.0, h - 1.2, paras)


# ── 1. 封面(白底,對齊 01/03 封面慣例)──────────────────
def build_cover(prs):
    s = _blank_slide(prs, BG_WHITE)
    _rect(s, 0.85, 0.55, 0.55, 0.07, VIOLET)
    _text(s, 0.85, 0.75, 12, 0.4, "MCP 入門工作坊  ·  第四講",
          font=FONT_BODY, size=15, color=MUTED, bold=True)
    _text(s, 0.85, 2.0, 12, 1.6, "動手做",
          font=FONT_TITLE, size=80, color=INK, bold=True)
    _text(s, 0.85, 3.55, 12, 0.7,
          "一個能力的誕生 —— 把 AI 能力從「無」變到「有」",
          font=FONT_BODY, size=24, color=VIOLET, bold=True)
    pastel_card(s, 0.85, 4.35, 8.0, 1.15, accent=VIOLET, fill=VIOLET_PASTEL)
    _text(s, 1.1, 4.45, 7.5, 0.55, "投影片講概念  ·  Colab 現場做",
          font=FONT_TITLE, size=22, color=VIOLET_DEEP, bold=True)
    _text(s, 1.1, 5.0, 7.5, 0.45,
          "兩邊交錯進行 —— 看到 teal 提示列就切到 Colab",
          font=FONT_BODY, size=15, color=INK)
    _text(s, 0.85, 6.3, 8, 0.4, "范耀中  Yao-Chung Fan",
          font=FONT_BODY, size=18, color=INK, bold=True)
    _text(s, 0.85, 6.75, 8, 0.4,
          "國立中興大學  ·  AI 學伴系統實務案例",
          font=FONT_BODY, size=14, color=MUTED)


# ── 2. 六步旅程地圖(脊椎)─────────────────────────────
def build_journey(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "00", "T H E   J O U R N E Y", accent=VIOLET)
    slide_title(s, "今天的旅程：六步", y=0.95)
    slide_subtitle(s, "先架好環境(第 0 步),然後一步一步看「能力」長出來", y=1.85, size=17)

    steps = [
        ("1", "給工具", "它就連上世界"),
        ("2", "換你的資料", "L1 · 零邏輯改動"),
        ("3", "選工具填參數", "L2 · LLM 自己抓"),
        ("4", "接外部 API", "L3 · 圖書館"),
        ("5", "撐大資料", "L4 · 3018 門課"),
        ("6", "親手造工具", "L5 · 高潮"),
    ]
    cw, gap, y, h = 1.92, 0.12, 2.7, 2.7
    x = 0.55
    for i, (n, title, sub) in enumerate(steps):
        accent = STEP_ACCENT[i]
        pastel_card(s, x, y, cw, h, accent=accent, fill=pastel_for(accent))
        _text(s, x, y + 0.3, cw, 0.7, n, font=FONT_TITLE, size=34, color=accent,
              bold=True, align=PP_ALIGN.CENTER)
        _text(s, x + 0.1, y + 1.15, cw - 0.2, 0.9, title, font=FONT_BODY, size=15,
              color=INK, bold=True, align=PP_ALIGN.CENTER)
        _text(s, x + 0.1, y + 1.95, cw - 0.2, 0.6, sub, font=FONT_BODY, size=11.5,
              color=MUTED, align=PP_ALIGN.CENTER)
        x += cw + gap

    callout_box(s, 0.85, 6.55, 12, 0.6,
                "每一步都「看得見背後的 loop」—— Segment 2／3 講的 tool_use ↔ tool_result,在你畫面上跑",
                accent=VIOLET, fill=VIOLET_PASTEL, icon="▶", size=14)
    page_number(s, 2, TOTAL)


# ── 3. 怎麼配合 Colab + 時間配置 ──────────────────────
def build_howto(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "00 · ①", "H O W   T O   U S E", accent=ORANGE)
    slide_title(s, "投影片講概念，Colab 現場做", y=0.95)
    slide_subtitle(s, "看到 teal 提示列就切到 Colab；做完再切回來講下一步", y=1.85, size=17)

    two_cards(s,
              (VIOLET, VIOLET_PASTEL, "投影片（這裡）", [
                  "• 講「為什麼」與概念", "• 一步一張,看完就切過去",
                  "• 每張底下 teal 列 = 該切 Colab 了"]),
              (TEAL, TEAL_PASTEL, "Colab（現場做）", [
                  "• 零安裝,瀏覽器就跑", "• 左側 目錄當投影片導覽",
                  "• 程式碼收在標題列,點 ▶ 就執行"]),
              y=2.5, h=2.7)

    callout_box(s, 0.85, 5.5, 12, 1.05,
                "70 分鐘配置： 0–10 環境＋第1步 demo ｜ 10–25 第2步 L1(學員必做) ｜ "
                "25–45 第3–4步 L2/L3 ｜ 45–60 交叉展示＋第5–6步 ｜ 60–70 Q&A＋鋪陳 Segment 5",
                accent=ORANGE, fill=ORANGE_PASTEL, icon="▶", size=14)
    page_number(s, 3, TOTAL)


# ── 4. 第 0 步 環境 ───────────────────────────────────
def build_step0(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "第 0 步", "S E T U P", accent=MUTED)
    slide_title(s, "先把工作台架起來", y=0.95)
    slide_subtitle(s, "跟故事無關的「準備材料」—— 跑一次就好,約 3 分鐘", y=1.85, size=17)

    code_block(s, 0.85, 2.6, 12, 2.4, [
        ("# 三格,從上到下按 ▶", CODE_COMMENT),
        ("① 下載教材 + 裝 Node 20 / uv", CODE_FG),
        ("② 安裝相依套件 (npm + uv sync)", CODE_FG),
        ("③ 設定 Claude API key", CODE_FG),
        ("   — Colab 左側 Secrets 設一次,或當場貼上", CODE_COMMENT),
    ], size=16)

    demo_cue(s, "— 第 0 步：跑環境三格(學員同步開 Colab)")
    page_number(s, 4, TOTAL)


# ── 5. 第 1 步 給工具 → 連上世界 ──────────────────────
def build_step1(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "第 1 步", "T O O L   =   B R I D G E", accent=VIOLET)
    slide_title(s, "給 LLM 一支工具，它就連上世界了", y=0.95)
    slide_subtitle(s, "工具就是那座橋 —— 而且你看得見它在背後呼叫", y=1.85, size=17)

    # 上方:沒工具 vs 掛工具(精簡兩卡)
    pastel_card(s, 0.85, 2.4, 5.5, 1.55, accent=PINK, fill=PINK_PASTEL, title="沒有工具", title_size=18)
    _multi(s, 1.15, 3.08, 5.0, 0.8, [
        {"text": "✗ 不知道今天幾號、查不到館藏", "font": FONT_BODY, "size": 13.5, "color": INK_SOFT, "space_after": 3},
        {"text": "→ 只能用舊知識,或亂猜", "font": FONT_BODY, "size": 13.5, "color": INK_SOFT}])
    pastel_card(s, 6.95, 2.4, 5.5, 1.55, accent=TEAL, fill=TEAL_PASTEL, title="掛上工具", title_size=18)
    _multi(s, 7.25, 3.08, 5.0, 0.8, [
        {"text": "✓ 自己呼叫工具、拿真實資料再答", "font": FONT_BODY, "size": 13.5, "color": INK_SOFT, "space_after": 3},
        {"text": "→ 這就是 agentic loop", "font": FONT_BODY, "size": 13.5, "color": INK_SOFT}])

    # 真實 artifact:Colab「看得見的 loop」那格會印出的軌跡
    _text(s, 0.85, 4.15, 12, 0.35, "在 Colab「看得見的 loop」那格,你會親眼看到這串：",
          font=FONT_BODY, size=13, color=MUTED)
    code_block(s, 0.85, 4.55, 12, 1.5, [
        ("# 你問:「資工系深度學習的課,老師有什麼論文?」", CODE_COMMENT),
        ("[tool_use] search_courses", CODE_FG),
        ("[tool_use] search_arxiv", CODE_FG),
        ("(stop_reason: end_turn  →  LLM 整合成一段回覆)", CODE_COMMENT),
    ], size=13)

    demo_cue(s, "— 第 1 步：跑「啟動 server」→ 問一題 →「看得見的 loop」")
    page_number(s, 5, TOTAL)


# ── 6. 第 2 步 換你的資料(L1)─────────────────────────
def build_step2(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "第 2 步 · L1", "M A K E   I T   Y O U R S", accent=ORANGE)
    slide_title(s, "把它換成「你的」世界", y=0.95)
    slide_subtitle(s, "不寫一行新邏輯,只動兩樣：換資料 + 改說明書", y=1.85, size=17)

    # ① 換資料(左卡)
    pastel_card(s, 0.85, 2.45, 4.2, 3.5, accent=ORANGE, fill=ORANGE_PASTEL, title="① 換資料", title_size=19)
    _multi(s, 1.15, 3.2, 3.7, 2.6, [
        {"text": "把 data/ 裡的 JSON", "font": FONT_BODY, "size": 14, "color": INK_SOFT, "space_after": 5},
        {"text": "換成你的領域：", "font": FONT_BODY, "size": 14, "color": INK_SOFT, "space_after": 5},
        {"text": "實驗室 / 課程 /", "font": FONT_BODY, "size": 14, "color": INK_SOFT, "space_after": 5},
        {"text": "研究成果 …", "font": FONT_BODY, "size": 14, "color": INK_SOFT, "space_after": 12},
        {"text": "（0 行 Python）", "font": FONT_BODY, "size": 13, "color": MUTED}])

    # ② 真實 docstring 程式碼(右)
    _text(s, 5.35, 2.45, 7.1, 0.4, "② 改說明書 docstring —— LLM 靠這段決定何時呼叫這支工具",
          font=FONT_BODY, size=13, color=VIOLET_DEEP, bold=True)
    code_block(s, 5.35, 2.95, 7.1, 3.0, [
        ('"""取得 XXX 研究室完整資訊。', CODE_STRING),
        ("", CODE_FG),
        ("使用情境:使用者詢問研究方向、", CODE_STRING),
        ("PI 聯絡方式、招生名額時呼叫。", CODE_STRING),
        ("", CODE_FG),
        ('回傳 JSON 字串。"""', CODE_STRING),
    ], size=14)

    demo_cue(s, "— 第 2 步：L1「換資料」→「改 docstring」→「重啟」（學員必做）")
    page_number(s, 6, TOTAL)


# ── 7. 第 3 步 自己選工具、填參數(L2)─────────────────
def build_step3(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "第 3 步 · L2", "L L M   P I C K S   A R G S", accent=TEAL)
    slide_title(s, "讓它自己選工具、填參數", y=0.95)
    slide_subtitle(s, "真實工具常常要帶參數 —— 看 LLM 自己從句子抓出來", y=1.85, size=17)

    two_cards(s,
              (MUTED, VIOLET_PASTEL, "直接呼叫（你來）", [
                  'search_teachers("電腦視覺", 3)',
                  "↑ 你自己決定關鍵字、自己呼叫",
                  "只是讓你看清工具本體"]),
              (TEAL, TEAL_PASTEL, "透過 agent（LLM 來）", [
                  "你問：「有誰在做電腦視覺？」",
                  "↑ LLM 自己萃取 keyword=電腦視覺",
                  "自己決定呼叫哪支、要不要再追問"]),
              y=2.5, h=2.7)

    callout_box(s, 0.85, 5.45, 12, 0.55,
                "agent 的價值不是「能呼叫工具」,而是 LLM 自己判斷該用哪支、填什麼、下一步要不要再查",
                accent=TEAL_DEEP, fill=TEAL_PASTEL, icon="▶", size=14)
    demo_cue(s, "— 第 3 步：L2 在聊天問「有做 CV 的老師？email？」,看它連兩次 tool call")
    page_number(s, 7, TOTAL)


# ── 8. 第 4 步 接外部 API(L3)─────────────────────────
def build_step4(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "第 4 步 · L3", "R E A C H   T H E   W O R L D", accent=PINK)
    slide_title(s, "接上真實的外部世界", y=0.95)
    slide_subtitle(s, "前面讀本機資料,真實工具常常要打外部 API", y=1.85, size=17)

    pastel_card(s, 0.85, 2.5, 12, 1.7, accent=PINK, fill=PINK_PASTEL,
                title="例：圖書館館藏查詢", title_size=21)
    _multi(s, 1.15, 3.45, 11.4, 0.7, [{
        "text": "library_tool 即時打中央大學圖書館的 Primo 公開端點（免 API key）,"
                "查到真實館藏再回給你 —— 不是假資料。",
        "font": FONT_BODY, "size": 16, "color": INK_SOFT}])

    callout_box(s, 0.85, 4.55, 12, 1.0,
                "工具背後可以是「任何外部系統」：圖書館、天氣、你系上的選課 API、實驗數據庫 …… "
                "對 LLM 來說都長一樣 —— 一個它能呼叫、會回 JSON 的工具。",
                accent=PINK, fill=PINK_PASTEL, icon="▶", size=14)
    demo_cue(s, "— 第 4 步：L3 問「圖書館有沒有《原子習慣》」+ 直接呼叫看它打 API")
    page_number(s, 8, TOTAL)


# ── 9. 第 5 步 撐大資料(L4)───────────────────────────
def build_step5(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "第 5 步 · L4", "S C A L E", accent=VIOLET)
    slide_title(s, "撐住幾千筆大資料", y=0.95)
    slide_subtitle(s, "course_tool 查中興 114-2 全部 3018 門真實課程", y=1.85, size=17)

    two_cards(s,
              (PINK, PINK_PASTEL, "為什麼不全塞給 LLM？", [
                  "3018 筆全丟進去", "→ context 直接爆掉",
                  "→ 又慢又貴又不準"]),
              (TEAL, TEAL_PASTEL, "工具端先篩再回", [
                  "工具在 3018 筆裡搜尋", "只回前幾筆相關的",
                  "LLM 只看這份篩過的小清單"]),
              y=2.5, h=2.7)

    callout_box(s, 0.85, 5.45, 12, 0.55,
                "「工具負責檢索、LLM 負責理解」—— 這就是 Segment 5 要談的 scale 議題的縮影",
                accent=VIOLET, fill=VIOLET_PASTEL, icon="▶", size=14)
    demo_cue(s, "— 第 5 步：L4 問「有沒有教深度學習的課？」「資工系有哪些選修？」")
    page_number(s, 9, TOTAL)


# ── 10. 第 6 步 親手造工具(L5,高潮)──────────────────
def build_step6(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "第 6 步 · L5", "B U I L D   Y O U R   O W N", accent=ORANGE)
    slide_title(s, "你親手造一支工具", y=0.95)
    slide_subtitle(s, "給 LLM 一個它本來辦不到的能力 —— 旅程的高潮", y=1.85, size=17)

    # ① 先問失敗(左卡)
    pastel_card(s, 0.85, 2.45, 4.2, 3.5, accent=PINK, fill=PINK_PASTEL, title="① 先問,它辦不到", title_size=18)
    _multi(s, 1.15, 3.2, 3.7, 2.6, [
        {"text": "問：「今天星期幾？」", "font": FONT_BODY, "size": 14, "color": INK_SOFT, "space_after": 8},
        {"text": "✗ LLM 沒有「現在」概念", "font": FONT_BODY, "size": 13.5, "color": INK_SOFT, "space_after": 5},
        {"text": "✗ 沒時鐘 → 亂猜或說不知道", "font": FONT_BODY, "size": 13.5, "color": INK_SOFT}])

    # ② 學員親手寫的真實工具(右)
    _text(s, 5.35, 2.45, 7.1, 0.4, "② 你親手寫這幾行 → 它就有了新能力",
          font=FONT_BODY, size=13.5, color=TEAL_DEEP, bold=True)
    code_block(s, 5.35, 2.95, 7.1, 3.0, [
        ("@mcp.tool()", CODE_ORANGE),
        ("def get_today() -> str:", CODE_FG),
        ('    """回傳今天日期與星期幾。', CODE_STRING),
        ('    使用情境:問今天幾號/星期幾時呼叫。"""', CODE_STRING),
        ("    t = datetime.date.today()", CODE_FG),
        ('    wd = "一二三四五六日"[t.weekday()]', CODE_FG),
        ('    return json.dumps(', CODE_FG),
        ('        {"今天": t.isoformat(), "星期": wd})', CODE_FG),
    ], size=12.5)

    demo_cue(s, "— 第 6 步：「先問失敗」→「造 today_tool」→ 再問答對 = MCP 的全部意義")
    page_number(s, 10, TOTAL)


# ── 11. 收尾(白底三卡 + 橋接,對齊 03 結尾慣例)─────────
def build_finale(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "收尾", "W R A P   U P", accent=VIOLET)
    slide_title(s, "你剛剛走完的旅程", y=0.95)
    slide_subtitle(s, "從「給一支工具」到「親手造一支」—— 六步,一個能力從無到有", y=1.85, size=17)

    cards = [
        (VIOLET, VIOLET_PASTEL, "1–2 · 連上你的世界",
         ["看見 loop 在背後跑", "把它換成你的資料", "（零邏輯改動,L1）"]),
        (ORANGE, ORANGE_PASTEL, "3–5 · 更真實的工具",
         ["LLM 自己選工具填參數", "接真實外部 API", "撐住 3018 筆大資料"]),
        (TEAL, TEAL_PASTEL, "6 · 親手造一支",
         ["寫一支 LLM 辦不到的工具", "→ 它有了新能力", "這 = MCP 的全部意義"]),
    ]
    cw, gap, y, h = 3.85, 0.2, 2.55, 3.4
    for i, (accent, fill, title, lines) in enumerate(cards):
        x = 0.85 + i * (cw + gap)
        pastel_card(s, x, y, cw, h, accent=accent, fill=fill, title=title, title_size=18)
        _multi(s, x + 0.28, y + 0.95, cw - 0.5, h - 1.2,
               [{"text": t, "font": FONT_BODY, "size": 14.5,
                 "color": INK_SOFT, "space_after": 8} for t in lines])

    callout_box(s, 0.85, 6.5, 12, 0.6,
                "從 3 支工具 到 239 支 —— Segment 5：真實上線的 scale / 品質 / 模型選擇 / 成本",
                accent=VIOLET, fill=VIOLET_PASTEL, icon="▶", size=14)
    page_number(s, 11, TOTAL)


# ── 12–13. 附錄(本機 / 卡點)──────────────────────────
def build_appendix_local(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "附錄 A", "R U N   L O C A L L Y", accent=MUTED)
    slide_title(s, "想在自己電腦跑（課後）", y=0.95)
    slide_subtitle(s, "Colab 是零安裝版;要在本機跑完整 web 版照這四步", y=1.85, size=17)

    code_block(s, 0.85, 2.6, 12, 2.7, [
        ("git clone <repo> && cd mini-project", CODE_FG),
        ("./setup.sh                 # 預檢 Node / uv / 套件", CODE_FG),
        ("cp .env.example .env       # 填入你的 ANTHROPIC_API_KEY", CODE_FG),
        ("cd backend-node && npm start", CODE_FG),
        ("# 開 http://localhost:3000", CODE_COMMENT),
    ], size=15)

    callout_box(s, 0.85, 5.6, 12, 0.55,
                "完整說明見 mini-project/README.md;三關 Lab 手冊在 docs/labs/",
                accent=VIOLET, fill=VIOLET_PASTEL, icon="▶", size=14)
    page_number(s, 12, TOTAL)


def build_appendix_trouble(prs):
    s = _blank_slide(prs, BG_WHITE)
    metadata_bar(s, "附錄 B", "T R O U B L E S H O O T I N G", accent=MUTED)
    slide_title(s, "卡點速查", y=0.95)
    slide_subtitle(s, "現場最常遇到的幾個", y=1.85, size=17)

    items = [
        ("聊天介面打不開 / 卡住", "跑 Colab 附錄 A：cloudflared 開公開網址（新分頁）"),
        ("EADDRINUSE / port 被佔", "重跑「啟動 server」那格即可（會自動殺舊的再起）"),
        ("key 格式錯", "確認以 sk-ant- 開頭;或用 Colab Secrets 設 ANTHROPIC_API_KEY"),
        ("改了檔卻沒生效", "回去重跑「啟動 / 重啟 server」那格讓改動套用"),
    ]
    y = 2.55
    for q, a in items:
        pastel_card(s, 0.85, y, 12, 0.95, accent=VIOLET, fill=VIOLET_PASTEL)
        _text(s, 1.15, y + 0.13, 11.4, 0.4, q, font=FONT_BODY, size=15,
              color=VIOLET_DEEP, bold=True)
        _text(s, 1.15, y + 0.5, 11.4, 0.4, "→ " + a, font=FONT_BODY, size=14,
              color=INK_SOFT)
        y += 1.07
    page_number(s, 13, TOTAL)


def main():
    prs = make_presentation()
    build_cover(prs)              # 1
    build_journey(prs)            # 2  六步地圖
    build_howto(prs)              # 3  怎麼配合 Colab + 時間
    build_step0(prs)              # 4  第0步 環境
    build_step1(prs)              # 5  第1步 給工具
    build_step2(prs)              # 6  第2步 L1 換資料
    build_step3(prs)              # 7  第3步 L2 參數
    build_step4(prs)              # 8  第4步 L3 外部 API
    build_step5(prs)              # 9  第5步 L4 大資料
    build_step6(prs)              # 10 第6步 L5 造工具
    build_finale(prs)             # 11 收尾
    build_appendix_local(prs)     # 12 附錄 A 本機
    build_appendix_trouble(prs)   # 13 附錄 B 卡點
    prs.save(str(PPTX))
    print(f"saved → {PPTX.name} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
