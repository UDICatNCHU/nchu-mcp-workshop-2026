"""
03-agentic-loop-video.py

~2:45 long video for Workshop Segment 3: Agentic Tool Loop.
Topic: how the LLM-driven while loop (tool_use → execute → tool_result → next
iteration → end_turn) actually runs, plus the maxIterations safety valve.

Two acts (Plan C — hybrid concept→trace):
  Act 1 — Concept: the 5-node loop crystallizes; stop_reason as the gate;
          maxIterations as the safety valve.
  Act 2 — One concrete iteration: LLM emits tool_use → tool executes →
          tool_result appended to messages → iteration 2 → end_turn → answer
          streams out.

Visual continuity with 01/02 videos (dark cinema palette, progress bar,
subtitle band, ACT badge).

Render:
  manim -ql --disable_caching 03-agentic-loop-video.py AgenticLoop
  manim -qh 03-agentic-loop-video.py AgenticLoop                # final 1080p60
"""

from manim import *
import numpy as np

# ----- Palette (matches 01/02 dark cinema, NOT the deck violet) -----
BG          = "#0a0a10"
DEEP_BLUE   = "#065A82"
TEAL        = "#2DB5C9"
INK         = "#FFFFFF"
NEUTRAL     = "#B4BED2"
BLUE        = "#5B8DE8"
ORANGE      = "#E8793A"
GREEN       = "#5CB85C"
RED         = "#D9534F"
DIM         = "#3A4A6A"
SHADOW      = "#000000"

CN_FONT     = "Noto Sans CJK TC"
SERIF_FONT  = "Noto Serif CJK TC"
MONO_FONT   = "DejaVu Sans Mono"

config.frame_width  = 16
config.frame_height = 9
config.pixel_width  = 1920
config.pixel_height = 1080


class AgenticLoop(Scene):
    SUBTITLE_MAX_WIDTH = 14.0
    TOTAL_SECONDS = 165.0

    TITLE     = "Agentic Tool Loop"
    SUBTITLE  = "LLM 如何自主決策、呼叫工具、迭代推理"

    def construct(self):
        self.camera.background_color = BG
        self._cur_subtitle = None
        self._init_progress_bar()

        # Persistent stage actors (Act 2)
        self.llm_box = None
        self.tool_box = None
        self.messages_panel = None
        self.messages_items = []          # list of VGroups stacked top→bottom
        self.iter_counter = None          # VGroup
        self.stop_badge = None            # VGroup

        self.scene_intro()       # 0:00–0:08   (8s)
        self.scene_scenario()    # 0:08–0:18   (10s)
        self.scene_act1()        # 0:18–1:18   (60s)
        self.scene_act2()        # 1:18–2:33   (75s)
        self.scene_outro()       # 2:33–2:45   (12s)

    # ============================================================
    # Progress bar
    # ============================================================
    def _init_progress_bar(self):
        self._bar_total_width = config.frame_width - 1.6
        self._bar_height = 0.05
        self._bar_y = -config.frame_height / 2 + 0.25
        self._bar_left = -self._bar_total_width / 2

        self.progress_bg = Rectangle(
            width=self._bar_total_width, height=self._bar_height,
            stroke_width=0, fill_color=NEUTRAL, fill_opacity=0.55,
        ).move_to([0, self._bar_y, 0])

        self.progress_fill = Rectangle(
            width=0.001, height=self._bar_height,
            stroke_width=0, fill_color=ORANGE, fill_opacity=1.0,
        )
        self._set_fill_width(0.001)
        self.add(self.progress_bg, self.progress_fill)

    def _set_fill_width(self, w):
        w = max(w, 0.001)
        self.progress_fill.stretch_to_fit_width(w)
        self.progress_fill.move_to([self._bar_left + w / 2, self._bar_y, 0])

    def advance_progress(self, target_seconds):
        target_w = self._bar_total_width * (target_seconds / self.TOTAL_SECONDS)
        self._set_fill_width(target_w)

    # ============================================================
    # Subtitle
    # ============================================================
    def _build_subtitle(self, text):
        sub = Text(text, font=CN_FONT, font_size=30, color=INK, weight=MEDIUM)
        if sub.width > self.SUBTITLE_MAX_WIDTH:
            sub.scale_to_fit_width(self.SUBTITLE_MAX_WIDTH)
        sub.to_edge(DOWN, buff=0.7)
        return sub

    def show_subtitle(self, text, run_time=0.35):
        new_sub = self._build_subtitle(text)
        if self._cur_subtitle is not None:
            self.play(FadeOut(self._cur_subtitle), FadeIn(new_sub),
                      run_time=run_time)
        else:
            self.play(FadeIn(new_sub), run_time=run_time)
        self._cur_subtitle = new_sub

    def clear_subtitle(self, run_time=0.3):
        if self._cur_subtitle is not None:
            self.play(FadeOut(self._cur_subtitle), run_time=run_time)
            self._cur_subtitle = None

    # ============================================================
    # ACT badge (top-right)
    # ============================================================
    def _make_act_badge(self, text):
        box = RoundedRectangle(width=1.6, height=0.55, corner_radius=0.10,
                               stroke_color=ORANGE, stroke_width=2,
                               fill_color=ORANGE, fill_opacity=0.20)
        lbl = Text(text, font=MONO_FONT, font_size=22,
                   color=ORANGE, weight=BOLD).move_to(box.get_center())
        badge = VGroup(box, lbl).move_to([6.8, 3.9, 0])
        badge.set_z_index(100)
        return badge

    # ============================================================
    # Helper: rounded box with header bar (shared visual idiom)
    # ============================================================
    def make_process_box(self, label_top, label_bot, color, pos,
                         width=2.8, height=1.7):
        corner = 0.20

        shadow = RoundedRectangle(
            width=width, height=height, corner_radius=corner,
            stroke_width=0, fill_color=SHADOW, fill_opacity=0.55,
        ).shift(RIGHT * 0.10 + DOWN * 0.10)

        box = RoundedRectangle(
            width=width, height=height, corner_radius=corner,
            stroke_color=color, stroke_width=3,
            fill_color=BG, fill_opacity=1.0,
        )

        header_h = 0.52
        header_pad = 0.06
        header = Rectangle(
            width=width - 2 * header_pad, height=header_h,
            stroke_width=0, fill_color=color, fill_opacity=0.55,
        )
        header.move_to(box.get_top() + DOWN * (header_h / 2 + header_pad))

        sep = Line(
            start=header.get_bottom() + LEFT * (width / 2 - header_pad - 0.02),
            end=header.get_bottom() + RIGHT * (width / 2 - header_pad - 0.02),
            color=color, stroke_width=1.2,
        )

        top = Text(label_top, font=CN_FONT, font_size=22, color=INK,
                   weight=BOLD).move_to(header.get_center())
        body_top_y = header.get_bottom()[1]
        body_bot_y = box.get_bottom()[1]
        body_center_y = (body_top_y + body_bot_y) / 2
        bot = Text(label_bot, font=MONO_FONT, font_size=16,
                   color=NEUTRAL).move_to([0, body_center_y, 0])

        group = VGroup(shadow, box, header, sep, top, bot).move_to(pos)
        return group

    # ============================================================
    # Helper: JSON snippet card
    # ============================================================
    def make_json_snippet(self, lines, color=NEUTRAL, width=5.5, height=None,
                          size=18):
        text = VGroup()
        for line, line_color in lines:
            t = Text(line, font=MONO_FONT, font_size=size,
                     color=line_color, weight=MEDIUM)
            text.add(t)
        text.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        h = height if height else text.height + 0.5
        box = RoundedRectangle(width=width, height=h, corner_radius=0.12,
                               stroke_color=color, stroke_width=1.5,
                               fill_color=BG, fill_opacity=0.92)
        text.move_to(box.get_center())
        return VGroup(box, text)

    # ============================================================
    # Helper: pill capsule
    # ============================================================
    def _make_pill(self, label, color, size=18, mono=True):
        font = MONO_FONT if mono else CN_FONT
        txt = Text(label, font=font, font_size=size,
                   color=INK, weight=BOLD)
        pad_w = txt.width + 0.5
        pad_h = txt.height + 0.28
        pill = RoundedRectangle(
            width=pad_w, height=pad_h, corner_radius=pad_h / 2,
            stroke_color=color, stroke_width=2.5,
            fill_color=color, fill_opacity=0.85,
        )
        txt.move_to(pill.get_center())
        return VGroup(pill, txt)

    # ============================================================
    # INTRO (8s) — title card
    # ============================================================
    def scene_intro(self):
        title = Text(self.TITLE, font=SERIF_FONT, font_size=110,
                     color=INK, weight=BOLD).move_to(UP * 0.6)
        subtitle = Text(self.SUBTITLE, font=CN_FONT, font_size=36,
                        color=NEUTRAL).move_to(DOWN * 1.0)
        accent = Line(start=LEFT * 1.5, end=RIGHT * 1.5,
                      color=ORANGE, stroke_width=3).move_to(DOWN * 0.25)

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=1.0)
        self.play(GrowFromCenter(accent), run_time=0.3)
        self.play(FadeIn(subtitle, shift=UP * 0.15), run_time=0.6)
        self.wait(5.1)
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(accent),
                  run_time=0.5)
        self.advance_progress(8)

    # ============================================================
    # SCENARIO (10s) — naive single-turn LLM can't answer
    # ============================================================
    def scene_scenario(self):
        # Query bubble (top center)
        query_text = Text("中興大學圖書館有什麼新書?",
                          font=CN_FONT, font_size=28, color=INK,
                          weight=MEDIUM)
        q_pad_w = query_text.width + 0.7
        q_pad_h = query_text.height + 0.55
        q_bubble = RoundedRectangle(
            width=q_pad_w, height=q_pad_h, corner_radius=0.22,
            stroke_color=BLUE, stroke_width=2.5,
            fill_color=BLUE, fill_opacity=0.22,
        )
        query_text.move_to(q_bubble.get_center())
        query_group = VGroup(q_bubble, query_text).move_to(UP * 2.4)

        q_lbl = Text("使用者", font=CN_FONT, font_size=20,
                     color=NEUTRAL)
        q_lbl.next_to(query_group, UP, buff=0.18)
        q_lbl.align_to(query_group, LEFT)

        self.show_subtitle("使用者問了一個 LLM 不知道答案的問題")
        self.play(FadeIn(q_lbl, shift=DOWN * 0.1),
                  FadeIn(query_group, shift=DOWN * 0.2),
                  run_time=0.6)
        self.wait(1.8)

        # Naive LLM shrug
        shrug = Text("…我的訓練資料沒有最新館藏",
                     font=CN_FONT, font_size=24, color=INK)
        arrow = Text("→ 一次回答就結束,使用者只拿到「我不知道」",
                     font=CN_FONT, font_size=22, color=RED,
                     weight=BOLD)
        shrug_block = VGroup(shrug, arrow).arrange(DOWN, buff=0.22,
                                                   aligned_edge=LEFT)
        s_pad_w = shrug_block.width + 0.8
        s_pad_h = shrug_block.height + 0.55
        s_box = RoundedRectangle(
            width=s_pad_w, height=s_pad_h, corner_radius=0.20,
            stroke_color=DIM, stroke_width=2.0,
            fill_color=DIM, fill_opacity=0.18,
        )
        shrug_block.move_to(s_box.get_center())
        naive_group = VGroup(s_box, shrug_block).move_to(DOWN * 0.6)

        n_lbl = Text("傳統單輪 LLM", font=CN_FONT, font_size=20,
                     color=NEUTRAL)
        n_lbl.next_to(naive_group, UP, buff=0.18)
        n_lbl.align_to(naive_group, LEFT)

        connector = Arrow(
            start=query_group.get_bottom() + DOWN * 0.05,
            end=naive_group.get_top() + UP * 0.05,
            color=NEUTRAL, stroke_width=2.5, buff=0.1,
            max_tip_length_to_length_ratio=0.08,
        )

        self.show_subtitle("單輪問答撞牆 —— 需要工具、需要迭代")
        self.play(GrowArrow(connector), run_time=0.4)
        self.play(FadeIn(n_lbl, shift=UP * 0.1),
                  FadeIn(naive_group, shift=UP * 0.2),
                  run_time=0.6)
        self.wait(5.0)

        self.play(FadeOut(q_lbl), FadeOut(query_group),
                  FadeOut(connector),
                  FadeOut(n_lbl), FadeOut(naive_group),
                  run_time=0.6)
        self.clear_subtitle(0.3)
        self.advance_progress(18)

    # ============================================================
    # ACT 1 — Concept (60s)
    # 0:18–0:38 (20s) loop crystallization (5 nodes)
    # 0:38–0:58 (20s) stop_reason gate zoom
    # 0:58–1:18 (20s) maxIterations safety valve
    # ============================================================
    def scene_act1(self):
        act_badge = self._make_act_badge("ACT 1")
        self.play(FadeIn(act_badge), run_time=0.3)
        self.show_subtitle("Agentic Loop —— 概念")
        self.wait(1.2)

        # ---------- Beat 1.1: 5-node loop crystallization (18s) ----------
        nodes_data = [
            ("使用者\nQuery",   BLUE,   LEFT * 5.6 + UP * 1.4),
            ("Build\nMessages", BLUE,   LEFT * 2.8 + UP * 1.4),
            ("Call\nLLM API",   ORANGE, ORIGIN    + UP * 1.4),
            ("Check\nstop_reason", ORANGE, RIGHT * 2.8 + UP * 1.4),
            ("Execute\nMCP Tool", TEAL,  RIGHT * 5.6 + UP * 1.4),
        ]
        nodes = []
        for label, color, pos in nodes_data:
            n = self._make_loop_node(label, color).move_to(pos)
            nodes.append(n)

        # Forward arrows between consecutive nodes
        fwd_arrows = []
        for i in range(4):
            a = Arrow(
                start=nodes[i].get_right() + RIGHT * 0.05,
                end=nodes[i + 1].get_left() + LEFT * 0.05,
                color=NEUTRAL, stroke_width=3.0, buff=0.05,
                max_tip_length_to_length_ratio=0.18,
            )
            fwd_arrows.append(a)

        # Loop-back arrow from Execute MCP Tool back to Call LLM API
        loop_back = CurvedArrow(
            start_point=nodes[4].get_bottom() + DOWN * 0.05,
            end_point=nodes[2].get_bottom() + DOWN * 0.05,
            angle=PI / 2.5, color=ORANGE, stroke_width=3.0,
            tip_length=0.22,
        )
        loop_back_lbl = Text("追加 tool_result,回到 LLM",
                             font=CN_FONT, font_size=20, color=ORANGE,
                             weight=BOLD)
        loop_back_lbl.next_to(loop_back, DOWN, buff=0.18)

        self.show_subtitle("整個流程是 5 個節點的迴圈")
        for i, n in enumerate(nodes):
            self.play(FadeIn(n, shift=DOWN * 0.15), run_time=0.35)
            if i < len(fwd_arrows):
                self.play(GrowArrow(fwd_arrows[i]), run_time=0.25)
        self.wait(1.0)

        self.show_subtitle("關鍵在最後 —— 工具結果回到 LLM,進入下一輪")
        self.play(Create(loop_back), run_time=1.0)
        self.play(FadeIn(loop_back_lbl, shift=UP * 0.1), run_time=0.4)
        self.wait(2.5)

        loop_group = VGroup(*nodes, *fwd_arrows, loop_back, loop_back_lbl)
        self.advance_progress(38)

        # ---------- Beat 1.2: stop_reason gate zoom (20s) ----------
        self.show_subtitle("迴圈是否繼續,由 LLM 回傳的 stop_reason 決定")
        # Fade everything except the LLM and Check nodes; bring Check center
        keep = VGroup(nodes[2], nodes[3], fwd_arrows[2])
        fade_set = VGroup(nodes[0], nodes[1], nodes[4],
                          fwd_arrows[0], fwd_arrows[1], fwd_arrows[3],
                          loop_back, loop_back_lbl)
        self.play(FadeOut(fade_set), run_time=0.5)

        self.play(keep.animate.shift(LEFT * 1.4 + DOWN * 0.3),
                  run_time=0.6)

        # Two outgoing paths from Check node
        check_node = nodes[3]
        path_up_end = check_node.get_right() + RIGHT * 4.0 + UP * 0.9
        path_dn_end = check_node.get_right() + RIGHT * 4.0 + DOWN * 0.9

        path_up = Arrow(
            start=check_node.get_right() + RIGHT * 0.05,
            end=path_up_end, color=ORANGE, stroke_width=3,
            buff=0.05, max_tip_length_to_length_ratio=0.10,
        )
        path_dn = Arrow(
            start=check_node.get_right() + RIGHT * 0.05,
            end=path_dn_end, color=GREEN, stroke_width=3,
            buff=0.05, max_tip_length_to_length_ratio=0.10,
        )

        tu_pill = self._make_pill('"tool_use"', ORANGE, size=18)
        tu_pill.move_to(path_up_end + RIGHT * 0.7)
        tu_lbl = Text("→ 執行工具 → 下一輪",
                      font=CN_FONT, font_size=20, color=ORANGE)
        tu_lbl.next_to(tu_pill, DOWN, buff=0.15).align_to(tu_pill, LEFT)

        et_pill = self._make_pill('"end_turn"', GREEN, size=18)
        et_pill.move_to(path_dn_end + RIGHT * 0.7)
        et_lbl = Text("→ 結束迴圈,回覆使用者",
                      font=CN_FONT, font_size=20, color=GREEN)
        et_lbl.next_to(et_pill, DOWN, buff=0.15).align_to(et_pill, LEFT)

        self.play(GrowArrow(path_up), FadeIn(tu_pill, shift=LEFT * 0.2),
                  run_time=0.6)
        self.play(FadeIn(tu_lbl, shift=UP * 0.1), run_time=0.4)
        self.wait(1.8)
        self.play(GrowArrow(path_dn), FadeIn(et_pill, shift=LEFT * 0.2),
                  run_time=0.6)
        self.play(FadeIn(et_lbl, shift=UP * 0.1), run_time=0.4)
        self.wait(2.5)

        self.show_subtitle("一句話:Agentic 就是 stop_reason 驅動的 while 迴圈")
        # Tiny code line
        code = Text("while (stop_reason === 'tool_use' "
                    "&& iter < maxIter) { ... }",
                    font=MONO_FONT, font_size=20, color=NEUTRAL,
                    weight=MEDIUM)
        code.move_to(DOWN * 2.3)
        self.play(FadeIn(code, shift=UP * 0.1), run_time=0.5)
        self.wait(3.0)

        gate_group = VGroup(keep, path_up, path_dn,
                            tu_pill, tu_lbl, et_pill, et_lbl, code)
        self.advance_progress(58)

        # ---------- Beat 1.3: maxIterations safety valve (20s) ----------
        self.show_subtitle("但 LLM 可能無限呼叫工具 —— 需要安全閥")
        self.play(FadeOut(gate_group), run_time=0.5)

        # Iteration ticker (1/7 → 7/7)
        ticker = self._make_iter_ticker(1)
        ticker.move_to(LEFT * 4.5 + UP * 0.8)
        ticker_lbl = Text("iteration", font=MONO_FONT, font_size=22,
                          color=NEUTRAL)
        ticker_lbl.next_to(ticker, UP, buff=0.20)

        self.play(FadeIn(ticker_lbl, shift=DOWN * 0.1),
                  FadeIn(ticker, shift=DOWN * 0.1), run_time=0.5)

        # 7 step pips arranged horizontally
        pips = VGroup()
        for i in range(7):
            dot = Circle(radius=0.22, stroke_color=NEUTRAL, stroke_width=2,
                         fill_color=BG, fill_opacity=1.0)
            num = Text(str(i + 1), font=MONO_FONT, font_size=18,
                       color=NEUTRAL, weight=BOLD).move_to(dot.get_center())
            pips.add(VGroup(dot, num))
        pips.arrange(RIGHT, buff=0.40).move_to(UP * 0.8 + RIGHT * 0.4)
        self.play(FadeIn(pips, shift=UP * 0.1), run_time=0.5)

        # Fill in pips 1–6 (LLM keeps calling tools)
        self.show_subtitle("第 1、2、3 … 輪都呼叫工具,迴圈沒停下來")
        for i in range(6):
            dot = pips[i][0]
            num = pips[i][1]
            self.play(
                dot.animate.set_fill(ORANGE, opacity=0.85)
                          .set_stroke(ORANGE),
                num.animate.set_color(INK),
                self._update_iter_ticker(ticker, i + 1),
                run_time=0.35,
            )

        self.wait(0.8)

        # Iteration 7 hits — red gate slams shut
        self.show_subtitle("第 7 輪,maxIterations 安全閥啟動,強制 LLM 回覆")
        gate_box = RoundedRectangle(
            width=2.4, height=1.1, corner_radius=0.18,
            stroke_color=RED, stroke_width=3,
            fill_color=RED, fill_opacity=0.25,
        ).move_to(pips[6].get_center() + DOWN * 1.4)
        gate_lbl_top = Text("強制回覆",
                            font=CN_FONT, font_size=22,
                            color=INK, weight=BOLD)
        gate_lbl_bot = Text("不准再呼叫工具",
                            font=CN_FONT, font_size=18,
                            color=NEUTRAL)
        gate_lbl = VGroup(gate_lbl_top, gate_lbl_bot).arrange(
            DOWN, buff=0.12).move_to(gate_box.get_center())

        gate_arrow = Arrow(
            start=pips[6].get_bottom() + DOWN * 0.05,
            end=gate_box.get_top() + UP * 0.05,
            color=RED, stroke_width=3, buff=0.05,
            max_tip_length_to_length_ratio=0.18,
        )

        self.play(
            pips[6][0].animate.set_fill(RED, opacity=0.85).set_stroke(RED),
            pips[6][1].animate.set_color(INK),
            self._update_iter_ticker(ticker, 7),
            run_time=0.4,
        )
        self.play(GrowArrow(gate_arrow), run_time=0.3)
        self.play(FadeIn(gate_box, scale=0.85), FadeIn(gate_lbl),
                  run_time=0.5)
        self.wait(3.5)

        act1_cleanup = VGroup(ticker, ticker_lbl, pips,
                              gate_arrow, gate_box, gate_lbl, act_badge)
        self.play(FadeOut(act1_cleanup), run_time=0.5)
        self.clear_subtitle(0.3)
        self.advance_progress(78)

    # ----- Act 1 helpers -----
    def _make_loop_node(self, label, color):
        # Two-line label inside a small rounded rect
        lines = label.split("\n")
        if len(lines) == 1:
            lines = [lines[0], ""]
        t1 = Text(lines[0], font=CN_FONT, font_size=18,
                  color=INK, weight=BOLD)
        t2 = Text(lines[1], font=MONO_FONT, font_size=16,
                  color=NEUTRAL)
        txt = VGroup(t1, t2).arrange(DOWN, buff=0.06)
        w = max(txt.width + 0.55, 1.85)
        h = txt.height + 0.55
        box = RoundedRectangle(
            width=w, height=h, corner_radius=0.15,
            stroke_color=color, stroke_width=2.5,
            fill_color=color, fill_opacity=0.20,
        )
        txt.move_to(box.get_center())
        return VGroup(box, txt)

    def _make_iter_ticker(self, n, total=7):
        digits = Text(f"{n} / {total}", font=MONO_FONT, font_size=44,
                      color=ORANGE, weight=BOLD)
        return VGroup(digits)

    def _update_iter_ticker(self, ticker, new_n, total=7):
        new_digits = Text(f"{new_n} / {total}", font=MONO_FONT, font_size=44,
                          color=ORANGE if new_n < 7 else RED, weight=BOLD)
        new_digits.move_to(ticker.get_center())
        return Transform(ticker[0], new_digits)

    # ============================================================
    # ACT 2 — One concrete iteration (75s)
    # 1:18–1:30 (12s) stage setup + user message appended
    # 1:30–1:48 (18s) LLM emits tool_use → appended to messages
    # 1:48–2:02 (14s) Tool executes (auto-inject user_id animation)
    # 2:02–2:18 (16s) tool_result returns → appended → iteration 2
    # 2:18–2:33 (15s) end_turn → final answer streams out
    # ============================================================
    def scene_act2(self):
        act_badge = self._make_act_badge("ACT 2")
        self.play(FadeIn(act_badge), run_time=0.3)
        self.show_subtitle("跑一輪看看 —— 從 user message 到 end_turn")
        self.wait(1.0)

        # ---------- Beat 2.1: stage setup (12s) ----------
        # LLM box (left) + Tool box (right) + messages panel (far right)
        self.llm_box = self.make_process_box(
            "LLM", "Claude Sonnet", ORANGE,
            LEFT * 5.0 + UP * 0.5, width=2.8, height=1.7,
        )
        self.tool_box = self.make_process_box(
            "MCP Tool", "search_new_books", TEAL,
            LEFT * 1.0 + UP * 0.5, width=3.0, height=1.7,
        )

        # Messages panel header
        panel_w = 5.4
        panel_h = 5.6
        panel = RoundedRectangle(
            width=panel_w, height=panel_h, corner_radius=0.18,
            stroke_color=NEUTRAL, stroke_width=2,
            fill_color=BG, fill_opacity=0.55,
        ).move_to(RIGHT * 4.3 + UP * 0.1)
        panel_hdr = Text("messages[]", font=MONO_FONT, font_size=22,
                         color=NEUTRAL, weight=BOLD)
        panel_hdr.move_to(panel.get_top() + DOWN * 0.32)
        self.messages_panel = VGroup(panel, panel_hdr)
        self._messages_top_y = panel.get_top()[1] - 0.75
        self._messages_x = panel.get_center()[0]
        self.messages_items = []

        # Iteration counter (top center)
        iter_lbl = Text("iteration", font=MONO_FONT, font_size=20,
                        color=NEUTRAL)
        iter_num = Text("1", font=MONO_FONT, font_size=36,
                        color=ORANGE, weight=BOLD)
        iter_num.next_to(iter_lbl, RIGHT, buff=0.25)
        self.iter_counter = VGroup(iter_lbl, iter_num)
        self.iter_counter.move_to(UP * 3.0)

        # stop_reason badge (under iteration)
        self.stop_badge = self._make_stop_badge("--", NEUTRAL)
        self.stop_badge.next_to(self.iter_counter, DOWN, buff=0.20)

        self.play(
            FadeIn(self.llm_box, shift=RIGHT * 0.2),
            FadeIn(self.tool_box, shift=LEFT * 0.2),
            FadeIn(self.messages_panel, shift=LEFT * 0.2),
            FadeIn(self.iter_counter, shift=DOWN * 0.1),
            FadeIn(self.stop_badge, shift=DOWN * 0.1),
            run_time=0.8,
        )

        # Append user message: query
        self.show_subtitle("使用者訊息進到 messages[]")
        user_item = self._make_message_item(
            "user", "中興大學圖書館有什麼新書?", BLUE,
        )
        self.wait(0.8)
        self._append_message(user_item, run_time=0.7)
        self.wait(2.5)

        self.advance_progress(90)

        # ---------- Beat 2.2: LLM emits tool_use (18s) ----------
        self.show_subtitle("第 1 輪:LLM 判斷需要呼叫工具,回傳 tool_use")

        # Pulse the LLM box
        llm_main = self.llm_box[1]  # the main box (index 1, after shadow)
        self.play(Indicate(llm_main, scale_factor=1.06, color=ORANGE),
                  run_time=1.0)

        # tool_use JSON snippet emitted from LLM
        tu_lines = [
            ('{ "type": "tool_use",',                 ORANGE),
            ('  "id": "toolu_01A09q...",',            NEUTRAL),
            ('  "name": "search_new_books",',         INK),
            ('  "input": { "keyword": "新書" } }',     INK),
        ]
        tu_snippet = self.make_json_snippet(
            tu_lines, color=ORANGE, width=4.4, size=16,
        )
        tu_snippet.move_to(self.llm_box.get_right() + RIGHT * 2.5)
        tu_snippet.set_z_index(50)

        self.play(FadeIn(tu_snippet, shift=RIGHT * 0.3), run_time=0.6)

        # Update stop_reason badge to tool_use
        self.play(self._replace_stop_badge("tool_use", ORANGE), run_time=0.4)
        self.wait(2.5)

        # The tool_use block flies into the messages panel as assistant
        assistant_item = self._make_message_item(
            "assistant", "tool_use: search_new_books({keyword:'新書'})",
            ORANGE,
        )
        # Position assistant_item at the next slot in panel
        target_pos = self._next_message_slot(assistant_item)
        self.play(
            Transform(tu_snippet, assistant_item.copy().move_to(target_pos)),
            run_time=0.9,
        )
        self.remove(tu_snippet)
        assistant_item.move_to(target_pos)
        self.add(assistant_item)
        self.messages_items.append(assistant_item)
        self.wait(2.0)

        self.advance_progress(108)

        # ---------- Beat 2.3: Tool execution (14s) ----------
        self.show_subtitle("Client 取出工具名稱+參數,呼叫 MCP Tool")

        # tool_use travels from LLM (visual: spawn a pill from LLM → Tool)
        tu_pill = self._make_pill("tool_use", ORANGE, size=16)
        tu_pill.move_to(self.llm_box.get_right() + RIGHT * 0.4)
        tu_pill.set_z_index(60)
        self.play(FadeIn(tu_pill, scale=0.7), run_time=0.3)
        self.play(
            tu_pill.animate.move_to(self.tool_box.get_left() + LEFT * 0.4),
            run_time=1.0,
        )
        self.play(FadeOut(tu_pill, scale=0.7), run_time=0.2)

        # Pulse tool box, show 3 dots cycling
        tool_main = self.tool_box[1]
        self.play(Indicate(tool_main, scale_factor=1.06, color=TEAL),
                  run_time=0.6)

        dots = VGroup(*[
            Dot(radius=0.10, color=TEAL).move_to(
                self.tool_box.get_center() + DOWN * 1.4 + RIGHT * (i - 1) * 0.35
            )
            for i in range(3)
        ])
        self.show_subtitle("MCP Tool 在 Python 那邊查 SQL...")
        self.play(FadeIn(dots), run_time=0.3)
        for _ in range(2):
            for d in dots:
                self.play(d.animate.set_fill(INK, opacity=1.0), run_time=0.15)
                self.play(d.animate.set_fill(TEAL, opacity=0.7), run_time=0.10)
        self.play(FadeOut(dots), run_time=0.3)
        self.wait(0.5)

        # tool_result pill flies back
        tr_pill = self._make_pill("tool_result", TEAL, size=16)
        tr_pill.move_to(self.tool_box.get_left() + LEFT * 0.4)
        tr_pill.set_z_index(60)
        self.play(FadeIn(tr_pill, scale=0.7), run_time=0.3)
        self.advance_progress(122)

        # ---------- Beat 2.4: tool_result appended → iteration 2 (16s) ----------
        self.show_subtitle("工具回傳結果,以 role: user 追加到 messages[]")

        tr_lines = [
            ('{ "role": "user",',                                NEUTRAL),
            ('  "content": [{',                                  NEUTRAL),
            ('    "type": "tool_result",',                       TEAL),
            ('    "tool_use_id": "toolu_01A09q...",',            NEUTRAL),
            ('    "content": [{ "text":',                        NEUTRAL),
            ('      "[{\\"title\\":\\"深度學習入門\\"}, ...]" }] }] }',  INK),
        ]
        tr_snippet = self.make_json_snippet(
            tr_lines, color=TEAL, width=5.6, size=14,
        )
        tr_snippet.move_to(LEFT * 1.0 + DOWN * 1.4)
        tr_snippet.set_z_index(50)

        # Pill morphs into snippet
        self.play(
            Transform(tr_pill, tr_snippet),
            run_time=0.9,
        )
        self.wait(2.0)

        # tool_result item appended (role: user)
        tr_item = self._make_message_item(
            "user (tool_result)",
            "[{title:'深度學習入門'}, ...10 筆]", TEAL,
        )
        target_pos = self._next_message_slot(tr_item)
        self.play(
            Transform(tr_pill, tr_item.copy().move_to(target_pos)),
            run_time=0.8,
        )
        self.remove(tr_pill)
        tr_item.move_to(target_pos)
        self.add(tr_item)
        self.messages_items.append(tr_item)

        # Iteration counter bumps to 2
        new_num = Text("2", font=MONO_FONT, font_size=36,
                       color=ORANGE, weight=BOLD)
        new_num.move_to(self.iter_counter[1].get_center())
        self.play(Transform(self.iter_counter[1], new_num),
                  run_time=0.5)
        self.show_subtitle("第 2 輪:把 messages[] 再送一次給 LLM")
        self.wait(2.5)

        self.advance_progress(138)

        # ---------- Beat 2.5: end_turn + final answer streams (15s) ----------
        self.show_subtitle("LLM 看到工具結果,生成最終回覆")
        self.play(Indicate(llm_main, scale_factor=1.06, color=ORANGE),
                  run_time=1.0)

        # stop_reason badge flips to end_turn
        self.play(self._replace_stop_badge("end_turn", GREEN), run_time=0.5)

        # Append assistant final message — typewriter style
        final_text_str = "以下是圖書館最新書籍:\n1.《深度學習入門》..."
        final_item = self._make_message_item(
            "assistant (final)", final_text_str, GREEN,
        )
        target_pos = self._next_message_slot(final_item)
        final_item.move_to(target_pos)

        self.show_subtitle("end_turn → 跳出迴圈,回覆使用者")
        # Reveal the final assistant card
        self.play(FadeIn(final_item, shift=UP * 0.2), run_time=0.7)
        self.messages_items.append(final_item)
        self.wait(2.5)

        # Highlight the final item
        self.play(Indicate(final_item, scale_factor=1.04, color=GREEN),
                  run_time=1.0)
        self.wait(2.0)

        # Clean up the act
        act2_objs = [
            self.llm_box, self.tool_box, self.messages_panel,
            self.iter_counter, self.stop_badge, act_badge,
            *self.messages_items,
        ]
        # tr_snippet may still be visible (left side); fade if present
        try:
            self.play(FadeOut(VGroup(*act2_objs, tr_snippet)), run_time=0.6)
        except Exception:
            self.play(FadeOut(VGroup(*act2_objs)), run_time=0.6)
        self.clear_subtitle(0.3)
        self.advance_progress(153)

    # ----- Act 2 helpers -----
    def _make_message_item(self, role_label, body_text, color, width=4.9):
        role = Text(role_label, font=MONO_FONT, font_size=14,
                    color=color, weight=BOLD)
        body = Text(body_text, font=CN_FONT, font_size=14,
                    color=INK)
        if body.width > width - 0.6:
            body.scale_to_fit_width(width - 0.6)
        block = VGroup(role, body).arrange(DOWN, buff=0.10,
                                           aligned_edge=LEFT)
        h = block.height + 0.35
        bg = RoundedRectangle(
            width=width, height=h, corner_radius=0.10,
            stroke_color=color, stroke_width=1.5,
            fill_color=color, fill_opacity=0.18,
        )
        block.move_to(bg.get_center())
        block.align_to(bg, LEFT).shift(RIGHT * 0.18)
        return VGroup(bg, block)

    def _next_message_slot(self, item):
        # Stack items top → down inside the messages panel
        spacing = 0.12
        if not self.messages_items:
            y = self._messages_top_y - item.height / 2
        else:
            last = self.messages_items[-1]
            y = last.get_bottom()[1] - spacing - item.height / 2
        return [self._messages_x, y, 0]

    def _append_message(self, item, run_time=0.6):
        target = self._next_message_slot(item)
        item.move_to(target)
        self.play(FadeIn(item, shift=DOWN * 0.2), run_time=run_time)
        self.messages_items.append(item)

    def _make_stop_badge(self, label, color):
        txt = Text(f'stop_reason: "{label}"',
                   font=MONO_FONT, font_size=18,
                   color=color if color != NEUTRAL else NEUTRAL,
                   weight=BOLD)
        pad_w = txt.width + 0.5
        pad_h = txt.height + 0.25
        box = RoundedRectangle(
            width=pad_w, height=pad_h, corner_radius=pad_h / 2,
            stroke_color=color, stroke_width=2,
            fill_color=color, fill_opacity=0.15,
        )
        txt.move_to(box.get_center())
        return VGroup(box, txt)

    def _replace_stop_badge(self, label, color):
        new_badge = self._make_stop_badge(label, color)
        new_badge.move_to(self.stop_badge.get_center())
        return Transform(self.stop_badge, new_badge)

    # ============================================================
    # OUTRO (12s) — one-line recap
    # ============================================================
    def scene_outro(self):
        line1 = Text("Agentic = stop_reason 驅動的 while 迴圈",
                     font=CN_FONT, font_size=44, color=INK,
                     weight=BOLD).move_to(UP * 0.6)
        line2 = Text("+ maxIterations 安全閥 + 最後一輪強制回覆",
                     font=CN_FONT, font_size=32, color=ORANGE,
                     weight=BOLD).move_to(DOWN * 0.3)
        accent = Line(start=LEFT * 1.8, end=RIGHT * 1.8,
                      color=ORANGE, stroke_width=3).move_to(UP * 0.1)

        self.play(FadeIn(line1, shift=DOWN * 0.2), run_time=0.7)
        self.play(GrowFromCenter(accent), run_time=0.3)
        self.play(FadeIn(line2, shift=UP * 0.15), run_time=0.6)
        self.wait(7.4)
        self.play(FadeOut(line1), FadeOut(line2), FadeOut(accent),
                  run_time=0.5)
        self.advance_progress(self.TOTAL_SECONDS)
        self.wait(1.0)
