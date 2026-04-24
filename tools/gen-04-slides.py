#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate 04-hands-on-lab.pptx from scratch.

Run:
    uv run --with python-pptx python3 tools/gen-04-slides.py

Output:
    ./04-hands-on-lab.pptx  (12 slides, 16:9)

Style conforms to the repo's visual spec (Ocean Gradient palette).
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

# ── Palette (Ocean Gradient + accents) ──────────────────────────────
NAVY    = RGBColor(0x1E, 0x27, 0x61)
DEEP    = RGBColor(0x06, 0x5A, 0x82)
TEAL    = RGBColor(0x1C, 0x72, 0x93)
ORANGE  = RGBColor(0xE8, 0x79, 0x3A)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
CREAM   = RGBColor(0xFA, 0xF7, 0xF2)
DARK    = RGBColor(0x1A, 0x1A, 0x1A)
MUTED   = RGBColor(0x6B, 0x6B, 0x6B)
SOFT    = RGBColor(0xE8, 0xED, 0xF3)
CODE_BG = RGBColor(0x10, 0x1A, 0x2E)
CODE_FG = RGBColor(0xDD, 0xE4, 0xEE)

FONT_TITLE = 'Arial Black'
FONT_BODY  = 'Calibri'
FONT_CODE  = 'Consolas'

# ── Presentation setup ──────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height

BLANK = prs.slide_layouts[6]


def blank_slide(bg=WHITE):
    s = prs.slides.add_slide(BLANK)
    rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    rect.fill.solid(); rect.fill.fore_color.rgb = bg
    rect.line.fill.background()
    # send to back
    spTree = s.shapes._spTree
    spTree.remove(rect._element); spTree.insert(2, rect._element)
    return s


def add_rect(slide, x, y, w, h, color, line_color=None):
    """Add filled rectangle at (x,y)  inches, (w,h) inches."""
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = color
    if line_color is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line_color
    sh.shadow.inherit = False
    return sh


def add_text(slide, x, y, w, h, text, *,
             font=FONT_BODY, size=18, color=DARK,
             bold=False, italic=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.bold = bold
    r.font.italic = italic
    return tb


def add_multi(slide, x, y, w, h, paragraphs, *, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """Add a textbox with multiple paragraphs.

    Each element in `paragraphs` is a dict:
      { text, font, size, color, bold, italic, space_after }
    """
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.vertical_anchor = anchor
    for i, spec in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = spec.get('align', align)
        if 'space_after' in spec:
            p.space_after = Pt(spec['space_after'])
        r = p.add_run()
        r.text = spec['text']
        r.font.name = spec.get('font', FONT_BODY)
        r.font.size = Pt(spec.get('size', 18))
        r.font.color.rgb = spec.get('color', DARK)
        r.font.bold = spec.get('bold', False)
        r.font.italic = spec.get('italic', False)
    return tb


def page_chrome(slide, page_num, total, title, subtitle=None):
    """Shared chrome: Navy top bar, title, page number, orange accent."""
    # Navy left accent strip
    add_rect(slide, 0, 0, 0.35, 7.5, NAVY)
    # Title
    add_text(slide, 0.75, 0.35, 11.5, 0.8, title,
             font=FONT_TITLE, size=30, color=NAVY, bold=True)
    if subtitle:
        add_text(slide, 0.75, 1.05, 11.5, 0.4, subtitle,
                 font=FONT_BODY, size=16, color=TEAL, italic=True)
    # Page number (right)
    add_text(slide, 11.8, 6.95, 1.4, 0.4, f'{page_num} / {total}',
             font=FONT_BODY, size=11, color=MUTED, align=PP_ALIGN.RIGHT)
    # Orange thin line under title
    add_rect(slide, 0.75, 1.55, 3, 0.04, ORANGE)


TOTAL = 12


# ── Slide 1: Cover ──────────────────────────────────────────────────
def slide_1_cover():
    s = blank_slide(NAVY)
    # Orange accent square (design flourish)
    add_rect(s, 1.0, 2.3, 0.5, 0.5, ORANGE)
    # Small kicker
    add_text(s, 1.6, 2.35, 5, 0.5, 'Segment 4',
             font=FONT_BODY, size=20, color=ORANGE, bold=True)
    # Main title (Chinese - Calibri for CJK support)
    add_text(s, 1.0, 3.0, 11, 1.5, '動手做',
             font=FONT_TITLE, size=80, color=WHITE, bold=True)
    # Subtitle
    add_text(s, 1.05, 4.3, 11, 0.6, 'Hands-on Lab · 50 minutes',
             font=FONT_BODY, size=26, color=SOFT)
    # Separator
    add_rect(s, 1.0, 5.1, 2.5, 0.04, ORANGE)
    # Tagline
    add_text(s, 1.0, 5.25, 11, 0.5, 'mini-project 實作主場 — 現場跑起你自己領域的 AI agent',
             font=FONT_BODY, size=18, color=SOFT)
    # Footer
    add_text(s, 1.0, 6.85, 6, 0.4, 'NCHU MCP Workshop 2026',
             font=FONT_BODY, size=12, color=TEAL, italic=True)
    add_text(s, 7.0, 6.85, 5.8, 0.4, 'github.com/UDICatNCHU/nchu-mcp-workshop-2026',
             font=FONT_CODE, size=11, color=TEAL, align=PP_ALIGN.RIGHT, italic=True)


# ── Slide 2: 本節產出物 ──────────────────────────────────────────────
def slide_2_outcomes():
    s = blank_slide(WHITE)
    page_chrome(s, 2, TOTAL, '本節產出物',
                subtitle='50 分鐘後，你將親手擁有')

    rows = [
        ('✓', '在你自己電腦上跑起來的 MCP agent',
              'Node.js + Python FastMCP + 極簡 HTML chat，三層完整可運作'),
        ('✓', '一支「屬於你領域」的客製工具',
              '換 JSON 就好，0 行 Python；實驗室介紹 / 課程大綱 / 研究成果清單都行'),
        ('✓', '對 agent 資料流的「實際脈動感」',
              '工具選擇 → 參數綁定 → LLM 摘要這條路，你會在 terminal 看它一次跑通'),
        ('✓', 'L2 / L3 的明確挑戰路徑',
              '帶回去繼續深入：加有參數的搜尋工具、呼叫外部 API'),
    ]
    y = 2.0
    for mark, title, desc in rows:
        # Orange check
        add_text(s, 0.9, y, 0.7, 0.6, mark,
                 font=FONT_TITLE, size=32, color=ORANGE, bold=True)
        # Title + description
        add_multi(s, 1.5, y, 11.3, 1.3, [
            dict(text=title, font=FONT_BODY, size=21, color=DARK, bold=True, space_after=4),
            dict(text=desc,  font=FONT_BODY, size=15, color=MUTED),
        ])
        y += 1.15


# ── Slide 3: 時間配置 ──────────────────────────────────────────────
def slide_3_schedule():
    s = blank_slide(WHITE)
    page_chrome(s, 3, TOTAL, '50 分鐘時間配置',
                subtitle='講師 10 min 引導 + 40 min 巡場陪跑')

    rows = [
        ('0–10',  '講師 demo + 學員同步 ./setup.sh',       '環境綠燈 5/5 ✅',  DEEP),
        ('10–20', 'L1 Step 1–2：觀察現況 + 換自己 JSON',    'data/your.json',   TEAL),
        ('20–35', 'L1 Step 3–4：改 docstring + 重啟驗證',  '問自己資料會答',   TEAL),
        ('35–45', '交叉展示：3–4 位老師 demo 自己領域',    '見識不同落地方式', DEEP),
        ('45–50', 'Q&A + 為 L2/L3 與 Segment 5 鋪陳',      '清楚下一步',       ORANGE),
    ]

    # Table header row
    header_y = 2.0
    add_rect(s, 0.75, header_y, 12.0, 0.55, NAVY)
    add_text(s, 0.95, header_y + 0.08, 1.7, 0.4, '時段 (min)',
             font=FONT_BODY, size=14, color=WHITE, bold=True)
    add_text(s, 2.85, header_y + 0.08, 6.5, 0.4, '做什麼',
             font=FONT_BODY, size=14, color=WHITE, bold=True)
    add_text(s, 9.5,  header_y + 0.08, 3.2, 0.4, '產出',
             font=FONT_BODY, size=14, color=WHITE, bold=True)

    y = 2.55
    for rng, what, out, color in rows:
        add_rect(s, 0.75, y, 12.0, 0.7, CREAM)
        add_rect(s, 0.75, y, 0.12, 0.7, color)  # left accent
        add_text(s, 0.95, y + 0.15, 1.7, 0.4, rng,
                 font=FONT_CODE, size=15, color=color, bold=True)
        add_text(s, 2.85, y + 0.15, 6.5, 0.4, what,
                 font=FONT_BODY, size=15, color=DARK)
        add_text(s, 9.5, y + 0.15, 3.2, 0.4, out,
                 font=FONT_BODY, size=14, color=MUTED, italic=True)
        y += 0.8

    # Footnote
    add_text(s, 0.75, 6.7, 12, 0.4,
             '※ 40 分鐘巡場預計 80% 在幫卡住的老師；開場預演越短，越多時間陪跑。',
             font=FONT_BODY, size=12, color=MUTED, italic=True)


# ── Slide 4: 架構回顧 ──────────────────────────────────────────────
def slide_4_architecture():
    s = blank_slide(WHITE)
    page_chrome(s, 4, TOTAL, '架構快速回顧',
                subtitle='Segment 2 / 3 的動畫，現在你要跑的實體')

    # ASCII-ish box diagram, centered
    boxes = [
        ('Browser', 'web/index.html  ·  fetch POST /chat', DEEP),
        ('Node server', 'Express  ·  LLMClient  ·  MCPClient', TEAL),
        ('Python FastMCP', '@mcp.tool()  ·  stdio JSON-RPC', DEEP),
        ('data/', '你的 JSON  ·  外部 API', NAVY),
    ]
    x0, y0 = 1.2, 2.1
    w, h = 10.9, 0.95
    for i, (title, desc, color) in enumerate(boxes):
        y = y0 + i * (h + 0.15)
        add_rect(s, x0, y, w, h, CREAM)
        add_rect(s, x0, y, 0.15, h, color)
        add_text(s, x0 + 0.35, y + 0.1, 3.5, 0.4, title,
                 font=FONT_TITLE, size=18, color=color, bold=True)
        add_text(s, x0 + 0.35, y + 0.5, w - 0.5, 0.4, desc,
                 font=FONT_CODE, size=14, color=DARK)
        # Arrow (except for last)
        if i < len(boxes) - 1:
            add_text(s, x0 + w/2 - 0.3, y + h - 0.05, 0.6, 0.25, '↓',
                     font=FONT_TITLE, size=20, color=ORANGE,
                     bold=True, align=PP_ALIGN.CENTER)

    add_text(s, 0.75, 6.75, 12, 0.4,
             '關鍵：LLM 回 stop_reason=tool_use → 跑工具 → 結果餵回 → 再問 → 最後 end_turn',
             font=FONT_BODY, size=13, color=MUTED, italic=True)


# ── Slide 5: Quick Start ──────────────────────────────────────────
def slide_5_quickstart():
    s = blank_slide(WHITE)
    page_chrome(s, 5, TOTAL, '快速入門（五步上線）',
                subtitle='預計 10 分鐘，跟著我一起做')

    # Code block container
    add_rect(s, 0.75, 2.0, 12.0, 4.5, CODE_BG)
    code = (
        '# 1. 取得教材\n'
        '$ git clone https://github.com/UDICatNCHU/nchu-mcp-workshop-2026\n'
        '$ cd nchu-mcp-workshop-2026/mini-project\n'
        '\n'
        '# 2. 設定 API key（或等下換成 workshop 本地端點）\n'
        '$ cp .env.example .env && vim .env\n'
        '\n'
        '# 3. 環境檢查（自動裝依賴 + 試啟動）\n'
        '$ ./setup.sh\n'
        '    → 看到 5/5 ✅ 代表 OK\n'
        '\n'
        '# 4. 啟動\n'
        '$ cd backend-node && npm start\n'
        '    → "Mini AI Assistant: http://localhost:3000"\n'
        '\n'
        '# 5. 瀏覽器打開 http://localhost:3000\n'
        '    → 問 "英文中心幾點開門？" 看 AI 答你'
    )
    add_text(s, 1.0, 2.15, 11.5, 4.3, code,
             font=FONT_CODE, size=15, color=CODE_FG)

    add_text(s, 0.75, 6.65, 12, 0.4,
             '看到 AI 答出 JSON 內容 → 恭喜，agent loop 已在你本機跑通 🎉',
             font=FONT_BODY, size=14, color=ORANGE, bold=True, italic=True)


# ── Slide 6: L1 Overview ──────────────────────────────────────────
def slide_6_l1_overview():
    s = blank_slide(WHITE)
    page_chrome(s, 6, TOTAL, 'Lab 1 — 換 JSON 做你領域的助理',
                subtitle='0 行 Python · 40 分鐘 · 現場必做')

    # Big 4-step flow
    steps = [
        ('1', '觀察', '看 [tool_use] log\nAI 摘要 JSON',          '5 min',  DEEP),
        ('2', '換資料', '編輯 data/*.json\n放你的領域內容',       '15 min', TEAL),
        ('3', '改說明書', 'docstring 的使用情境\n決定工具呼叫率', '10 min', ORANGE),
        ('4', '驗證', '重啟 npm start\n問自己資料問題',           '5 min',  DEEP),
    ]
    x0, y = 0.85, 2.3
    box_w, box_h = 2.9, 3.8
    gap = 0.15
    for i, (num, title, desc, dur, color) in enumerate(steps):
        x = x0 + i * (box_w + gap)
        add_rect(s, x, y, box_w, box_h, CREAM)
        add_rect(s, x, y, box_w, 0.75, color)
        # Number (white on color)
        add_text(s, x + 0.3, y + 0.08, 1.0, 0.6, num,
                 font=FONT_TITLE, size=36, color=WHITE, bold=True)
        # Step title
        add_text(s, x + 1.1, y + 0.15, box_w - 1.2, 0.5, title,
                 font=FONT_TITLE, size=22, color=WHITE, bold=True)
        # Description
        add_text(s, x + 0.25, y + 1.0, box_w - 0.5, 2.0, desc,
                 font=FONT_BODY, size=15, color=DARK)
        # Duration badge
        add_rect(s, x + 0.25, y + 3.15, 1.5, 0.45, color)
        add_text(s, x + 0.25, y + 3.2, 1.5, 0.4, dur,
                 font=FONT_CODE, size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

    add_text(s, 0.85, 6.6, 12, 0.5,
             '產出：你的 AI 助理會回答「你自己放進去的資料」— 不是英文中心 demo 了',
             font=FONT_BODY, size=15, color=ORANGE, bold=True, italic=True)


# ── Slide 7: Step 1-2: 觀察 + 換 JSON ──────────────────────────────
def slide_7_step12():
    s = blank_slide(WHITE)
    page_chrome(s, 7, TOTAL, 'Step 1–2：觀察 → 換 JSON',
                subtitle='還沒動到 Python 一個字')

    # Left: Step 1 观察
    add_rect(s, 0.75, 2.0, 6.0, 4.6, CREAM)
    add_rect(s, 0.75, 2.0, 6.0, 0.55, DEEP)
    add_text(s, 1.0, 2.07, 5.8, 0.45, 'Step 1　觀察（5 min）',
             font=FONT_TITLE, size=18, color=WHITE, bold=True)

    add_multi(s, 0.95, 2.75, 5.7, 3.8, [
        dict(text='在瀏覽器問：', size=15, color=DARK, space_after=2),
        dict(text='  「英文中心幾點開門？」', font=FONT_CODE, size=14, color=DEEP, space_after=8),
        dict(text='在 terminal 觀察：', size=15, color=DARK, space_after=2),
        dict(text='  [tool_use] get_english_center_info', font=FONT_CODE, size=13, color=ORANGE, space_after=10),
        dict(text='💡 關鍵觀察', size=15, color=DARK, bold=True, space_after=2),
        dict(text='Claude 不會 dump 整份 JSON。它挑出「開放時間」那一段。',
             size=13, color=MUTED, space_after=4),
        dict(text='這是 LLM 對 tool result 做的「摘要」— agent 的靈魂。',
             size=13, color=MUTED),
    ])

    # Right: Step 2 換 JSON
    add_rect(s, 7.0, 2.0, 5.75, 4.6, CREAM)
    add_rect(s, 7.0, 2.0, 5.75, 0.55, TEAL)
    add_text(s, 7.2, 2.07, 5.5, 0.45, 'Step 2　換 JSON（15 min）',
             font=FONT_TITLE, size=18, color=WHITE, bold=True)

    add_multi(s, 7.15, 2.75, 5.55, 3.8, [
        dict(text='編輯：', size=14, color=DARK, space_after=2),
        dict(text='  mcp-server-py/data/english_center.json',
             font=FONT_CODE, size=12, color=TEAL, space_after=8),
        dict(text='換成你自己的領域資料：', size=14, color=DARK, space_after=2),
        dict(text='• 你的研究室介紹', size=13, color=DARK, space_after=1),
        dict(text='• 你教的一門課（大綱/作業/評分）', size=13, color=DARK, space_after=1),
        dict(text='• 你系所的 FAQ', size=13, color=DARK, space_after=1),
        dict(text='• 你的研究成果清單', size=13, color=DARK, space_after=8),
        dict(text='⚠ JSON 語法錯會卡住：', size=13, color=ORANGE, bold=True, space_after=2),
        dict(text='  python3 -m json.tool data/xxx.json  驗一下',
             font=FONT_CODE, size=12, color=MUTED),
    ])


# ── Slide 8: Step 3 Docstring ──────────────────────────────────────
def slide_8_step3():
    s = blank_slide(WHITE)
    page_chrome(s, 8, TOTAL, 'Step 3：改 docstring（10 min）',
                subtitle='這一步最影響 AI 能否正確呼叫你的工具')

    # Big statement
    add_text(s, 0.75, 1.85, 12, 0.5,
             'docstring 就是 LLM 看到的「工具說明書」— 不是給人類的註解',
             font=FONT_BODY, size=18, color=NAVY, bold=True, italic=True)

    # Left: bad
    add_rect(s, 0.75, 2.5, 6.0, 3.8, CREAM)
    add_rect(s, 0.75, 2.5, 6.0, 0.5, RGBColor(0xC8, 0x3E, 0x3E))
    add_text(s, 1.0, 2.55, 5.8, 0.4, '❌  糟糕寫法',
             font=FONT_TITLE, size=16, color=WHITE, bold=True)
    bad_code = (
        '@mcp.tool()\n'
        'def search(keyword: str) -> str:\n'
        '    """Search."""\n'
        '    ...\n'
        '\n'
        '# 結果：Claude 不知道何時\n'
        '# 該呼叫，常常漏叫。'
    )
    add_text(s, 0.9, 3.1, 5.8, 3.1, bad_code,
             font=FONT_CODE, size=14, color=DARK)

    # Right: good
    add_rect(s, 7.0, 2.5, 5.75, 3.8, CREAM)
    add_rect(s, 7.0, 2.5, 5.75, 0.5, RGBColor(0x2E, 0x8B, 0x4E))
    add_text(s, 7.2, 2.55, 5.5, 0.4, '✅  好寫法',
             font=FONT_TITLE, size=16, color=WHITE, bold=True)
    good_code = (
        '@mcp.tool()\n'
        'def search_teachers(\n'
        '    keyword: str, limit: int = 5\n'
        ') -> str:\n'
        '    """依關鍵字搜尋資工系教授。\n'
        '\n'
        '    使用情境：使用者詢問某\n'
        '    領域教授、某位教授時呼叫。\n'
        '    ...\n'
        '    """'
    )
    add_text(s, 7.15, 3.1, 5.5, 3.1, good_code,
             font=FONT_CODE, size=13, color=DARK)

    # Footer tip
    add_text(s, 0.75, 6.55, 12, 0.5,
             '💡 關鍵 3 件事：① 明寫「使用情境」  ② 說明參數意義  ③ 描述回傳格式',
             font=FONT_BODY, size=15, color=ORANGE, bold=True, italic=True)


# ── Slide 9: Step 4 驗證 ──────────────────────────────────────────
def slide_9_step4():
    s = blank_slide(WHITE)
    page_chrome(s, 9, TOTAL, 'Step 4：重啟 + 驗證（5 min）',
                subtitle='三件事證明你的工具「真的在 work」')

    # Command block
    add_rect(s, 0.75, 2.0, 12.0, 1.3, CODE_BG)
    add_text(s, 1.0, 2.1, 11.5, 1.1,
             '$ Ctrl+C                            # 停掉前一次 server\n'
             '$ cd backend-node && npm start\n'
             '  → ✓ hello_tool → get_lab_info    # 新名字出現代表工具註冊成功',
             font=FONT_CODE, size=15, color=CODE_FG)

    # Three verify cards
    cards = [
        ('①', '問「不相關」的問題',     '「今天天氣？」',  'AI 應該不呼叫你的工具，直接聊天',  DEEP),
        ('②', '問「相關」的問題',       '「研究室招生條件？」',  'AI 會引用 JSON 裡的實際內容',  TEAL),
        ('③', '問「資料沒有」的內容',   '「有實習機會嗎？」（JSON 沒這欄）',
              'AI 應該明說不知道，不會幻想',  ORANGE),
    ]
    y = 3.65
    for num, title, q, expect, color in cards:
        add_rect(s, 0.75, y, 12.0, 0.75, CREAM)
        add_rect(s, 0.75, y, 0.12, 0.75, color)
        add_text(s, 1.0, y + 0.12, 0.5, 0.5, num,
                 font=FONT_TITLE, size=22, color=color, bold=True)
        add_text(s, 1.6, y + 0.06, 4.2, 0.4, title,
                 font=FONT_BODY, size=15, color=DARK, bold=True)
        add_text(s, 1.6, y + 0.4, 4.2, 0.4, q,
                 font=FONT_CODE, size=13, color=MUTED)
        add_text(s, 5.9, y + 0.18, 6.9, 0.5, expect,
                 font=FONT_BODY, size=14, color=DARK)
        y += 0.9

    add_text(s, 0.75, 6.65, 12, 0.4,
             '第 ③ 項過關最關鍵 — 代表 agent 在 tool-grounded，不是在胡謅。',
             font=FONT_BODY, size=13, color=MUTED, italic=True)


# ── Slide 10: 連本地端點 ──────────────────────────────────────────
def slide_10_local_endpoint():
    s = blank_slide(WHITE)
    page_chrome(s, 10, TOTAL, 'Workshop 現場：改用 NCHU 本地模型',
                subtitle='省 API 費 · 延遲更低 · 零配額限制')

    # Env config block
    add_rect(s, 0.75, 2.0, 12.0, 2.4, CODE_BG)
    add_text(s, 1.0, 2.15, 11.5, 2.2,
             '# mini-project/.env\n'
             'LLM_PROVIDER=openai\n'
             'OPENAI_BASE_URL=http://<workshop-server>:8000/v1\n'
             'OPENAI_API_KEY=dummy\n'
             'OPENAI_MODEL=gemma-4',
             font=FONT_CODE, size=16, color=CODE_FG)

    # Benchmark mini-card
    add_rect(s, 0.75, 4.65, 12.0, 1.8, CREAM)
    add_rect(s, 0.75, 4.65, 0.12, 1.8, ORANGE)
    add_text(s, 1.1, 4.75, 11.5, 0.4, '📊  2026-04-24 實測對比',
             font=FONT_BODY, size=16, color=NAVY, bold=True)
    add_multi(s, 1.1, 5.15, 11.5, 1.3, [
        dict(text='Tool 選擇正確率：Claude 100%  ·  Gemma 4 100%  ← 打平',
             font=FONT_CODE, size=14, color=DARK, space_after=4),
        dict(text='Hallucination 抵抗：兩者都通過',
             font=FONT_CODE, size=14, color=DARK, space_after=4),
        dict(text='延遲：Claude 4.8s  vs  Gemma 4 3.5s  ← 本地快 1.4×',
             font=FONT_CODE, size=14, color=DARK),
    ])

    add_text(s, 0.75, 6.65, 12, 0.4,
             '→ 詳見 mini-project/docs/benchmarks/2026-04-24-claude-vs-gemma4.md',
             font=FONT_CODE, size=12, color=MUTED)


# ── Slide 11: 常見卡點 ────────────────────────────────────────────
def slide_11_pitfalls():
    s = blank_slide(WHITE)
    page_chrome(s, 11, TOTAL, '常見卡點速查',
                subtitle='卡住 30 秒就看這頁；更多在 Lab 手冊結尾')

    rows = [
        ('setup.sh 卡 Node 版本',          '本機 Node < 18',            'nvm install 22 && nvm use 22'),
        ('port 3000 已被占',                '其他服務先佔了',            'PORT=3001 npm start'),
        ('瀏覽器問後沒反應',                '.env 的 API key 還是 placeholder', '檢查 sk-ant-... 有沒有填'),
        ('JSON 讀取錯誤',                   '手改 JSON 有語法錯',        'python3 -m json.tool data/xxx.json'),
        ('問相關問題但沒叫工具',            'docstring 寫太短 / 太含糊', '補「使用情境：當使用者問 X 時」'),
    ]

    # Header
    add_rect(s, 0.75, 1.95, 12.0, 0.55, NAVY)
    add_text(s, 0.95, 2.02, 3.8, 0.4, '症狀',
             font=FONT_BODY, size=14, color=WHITE, bold=True)
    add_text(s, 4.9,  2.02, 3.5, 0.4, '原因',
             font=FONT_BODY, size=14, color=WHITE, bold=True)
    add_text(s, 8.6,  2.02, 4.2, 0.4, '解法',
             font=FONT_BODY, size=14, color=WHITE, bold=True)

    y = 2.55
    for sym, cause, fix in rows:
        add_rect(s, 0.75, y, 12.0, 0.75, CREAM)
        add_text(s, 0.95, y + 0.17, 3.8, 0.5, sym,
                 font=FONT_BODY, size=14, color=DARK)
        add_text(s, 4.9,  y + 0.17, 3.5, 0.5, cause,
                 font=FONT_BODY, size=13, color=MUTED)
        add_text(s, 8.6,  y + 0.17, 4.2, 0.5, fix,
                 font=FONT_CODE, size=13, color=DEEP)
        y += 0.85

    add_text(s, 0.75, 6.85, 12, 0.4,
             '卡住超過 3 分鐘：舉手。講師 + 鄰座老師會過來幫你。',
             font=FONT_BODY, size=13, color=ORANGE, bold=True, italic=True)


# ── Slide 12: 結束 & 鋪陳 Segment 5 ────────────────────────────────
def slide_12_end():
    s = blank_slide(NAVY)

    # Big congrats
    add_text(s, 0.75, 1.2, 12, 0.8, '恭喜 — 你剛做出了',
             font=FONT_BODY, size=26, color=SOFT)
    add_text(s, 0.75, 1.9, 12, 1.2, '屬於你自己領域的 AI agent',
             font=FONT_TITLE, size=48, color=WHITE, bold=True)
    add_rect(s, 0.75, 3.1, 2.5, 0.05, ORANGE)

    # Two columns
    # Left: 回家路徑
    add_text(s, 0.75, 3.45, 6, 0.4, '回家路徑（課後自修）',
             font=FONT_TITLE, size=18, color=ORANGE, bold=True)
    add_multi(s, 0.75, 3.9, 6, 2.5, [
        dict(text='🧪  L2 — 加一支有參數的搜尋工具',
             font=FONT_BODY, size=16, color=WHITE, bold=True, space_after=4),
        dict(text='     docs/labs/L2-add-a-search-tool.md  (40 分)',
             font=FONT_CODE, size=12, color=SOFT, space_after=10),
        dict(text='🧪  L3 — 呼叫外部 API（async + XML）',
             font=FONT_BODY, size=16, color=WHITE, bold=True, space_after=4),
        dict(text='     docs/labs/L3-call-external-api.md  (60 分)',
             font=FONT_CODE, size=12, color=SOFT),
    ])

    # Right: 鋪陳 Segment 5
    add_text(s, 7.0, 3.45, 5.8, 0.4, '下一段 Segment 5',
             font=FONT_TITLE, size=18, color=ORANGE, bold=True)
    add_multi(s, 7.0, 3.9, 5.8, 2.5, [
        dict(text='實務考量（10 min 收尾）',
             font=FONT_BODY, size=16, color=WHITE, bold=True, space_after=6),
        dict(text='從「你剛做的 3 個工具」往外擴：',
             font=FONT_BODY, size=14, color=SOFT, space_after=3),
        dict(text='• 239 工具怎麼辦？（Scale）',
             font=FONT_BODY, size=13, color=SOFT, space_after=2),
        dict(text='• 工具描述怎麼寫？（Quality）',
             font=FONT_BODY, size=13, color=SOFT, space_after=2),
        dict(text='• 該用哪個模型？（Model）',
             font=FONT_BODY, size=13, color=SOFT, space_after=2),
        dict(text='• 帳單會有多貴？（Cost）',
             font=FONT_BODY, size=13, color=SOFT),
    ])

    # Footer
    add_text(s, 0.75, 6.7, 12, 0.4,
             'github.com/UDICatNCHU/nchu-mcp-workshop-2026   ·   Issues 歡迎！',
             font=FONT_CODE, size=12, color=TEAL, align=PP_ALIGN.CENTER, italic=True)


# ── Build ───────────────────────────────────────────────────────────
BUILDERS = [
    slide_1_cover, slide_2_outcomes, slide_3_schedule, slide_4_architecture,
    slide_5_quickstart, slide_6_l1_overview, slide_7_step12, slide_8_step3,
    slide_9_step4, slide_10_local_endpoint, slide_11_pitfalls, slide_12_end,
]
for b in BUILDERS:
    b()

out = Path(__file__).resolve().parent.parent / '04-hands-on-lab.pptx'
prs.save(out)
print(f'✓ wrote {out} ({len(prs.slides)} slides)')
