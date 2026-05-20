#!/usr/bin/env python3
"""Build a PowerPoint presentation about the やさしい日本語 前例リファレンス project.

Targeted at 市役所 staff and managers. Core message: empower human
decision-making with data and 前例 (precedent).

Usage:
    pip install python-pptx
    python3 build_presentation.py
"""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Constants ──────────────────────────────────────────────────────────

OUTPUT = Path("data") / "やさしい日本語_前例リファレンス.pptx"

# Colours
GREEN = RGBColor(0x3B, 0x7A, 0x28)
DARK_GREEN = RGBColor(0x2A, 0x57, 0x1C)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x33, 0x33, 0x33)
GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)
LIGHT_GREEN = RGBColor(0xE8, 0xF5, 0xE2)
MEDIUM_GREEN = RGBColor(0xC8, 0xE6, 0xC0)

SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)


# ── Helpers ────────────────────────────────────────────────────────────

def _set_slide_bg(slide, color):
    """Set the background colour of a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_textbox(slide, left, top, width, height, text, *,
                 font_size=18, bold=False, color=BLACK,
                 alignment=PP_ALIGN.LEFT, font_name="メイリオ",
                 anchor=MSO_ANCHOR.TOP):
    """Add a textbox with a single run of text."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name
    try:
        tf.paragraphs[0].anchor = anchor
    except Exception:
        pass
    return txBox, tf


def _add_rich_textbox(slide, left, top, width, height):
    """Add an empty textbox and return (shape, text_frame) for manual population."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    return txBox, tf


def _add_run(paragraph, text, *, font_size=18, bold=False, color=BLACK,
             font_name="メイリオ"):
    """Append a run to an existing paragraph."""
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name
    return run


def _new_paragraph(tf, *, alignment=PP_ALIGN.LEFT, space_before=Pt(6),
                   space_after=Pt(0), level=0):
    """Add a new paragraph to a text frame."""
    p = tf.add_paragraph()
    p.alignment = alignment
    p.space_before = space_before
    p.space_after = space_after
    p.level = level
    return p


def _add_rounded_rect(slide, left, top, width, height, fill_color):
    """Add a rounded rectangle shape."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _add_rect(slide, left, top, width, height, fill_color):
    """Add a plain rectangle shape."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def _shape_text(shape, text, *, font_size=18, bold=False, color=BLACK,
                alignment=PP_ALIGN.CENTER, font_name="メイリオ"):
    """Set text inside a shape."""
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name
    return tf


def _stat_card(slide, left, top, width, height, number, label):
    """Draw a stat card: large number + smaller label underneath."""
    shape = _add_rounded_rect(slide, left, top, width, height, LIGHT_GREEN)
    tf = shape.text_frame
    tf.word_wrap = True

    # Number
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(12)
    run = p.add_run()
    run.text = number
    run.font.size = Pt(44)
    run.font.bold = True
    run.font.color.rgb = GREEN
    run.font.name = "メイリオ"

    # Label
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(4)
    run2 = p2.add_run()
    run2.text = label
    run2.font.size = Pt(16)
    run2.font.color.rgb = DARK_GREEN
    run2.font.name = "メイリオ"


# ── Slide builders ─────────────────────────────────────────────────────

def slide_title(prs):
    """Slide 1: Title."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    _set_slide_bg(slide, GREEN)

    # Green bar accent at top
    _add_rect(slide, Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.15), DARK_GREEN)

    # Main title
    _add_textbox(
        slide, Inches(1), Inches(1.8), Inches(11.3), Inches(2),
        "やさしい日本語\n前例リファレンス",
        font_size=52, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER
    )

    # Subtitle
    _add_textbox(
        slide, Inches(1.5), Inches(4.2), Inches(10.3), Inches(1.2),
        "データで支える、やさしい日本語への書き換え",
        font_size=28, color=WHITE, alignment=PP_ALIGN.CENTER
    )

    # Bottom line
    _add_rect(slide, Inches(4), Inches(5.8), Inches(5.3), Inches(0.04), WHITE)


def slide_problem(prs):
    """Slide 2: 課題."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, WHITE)

    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "課題", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    _add_textbox(
        slide, Inches(0.8), Inches(1.6), Inches(11), Inches(0.8),
        "やさしい日本語の書き換えは、なぜ難しいのか？",
        font_size=24, bold=True, color=BLACK
    )

    problems = [
        ("正解がひとつではない",
         "同じ言葉でも、文脈や対象者によって書き換え方は異なる"),
        ("判断に時間がかかる",
         "「この言葉は書き換えるべき？」の議論で会議が長引く"),
        ("部署ごとにバラバラ",
         "同じ市役所内でも、担当者によって書き換え方が異なる"),
        ("根拠が示しにくい",
         "「なぜこの書き換えにしたのか」を説明する材料がない"),
    ]

    y = Inches(2.6)
    for title, desc in problems:
        # Icon-like circle
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(1.2), y + Inches(0.08), Inches(0.35), Inches(0.35)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = RGBColor(0xE8, 0x44, 0x44)
        circle.line.fill.background()
        _shape_text(circle, "✕", font_size=16, bold=True, color=WHITE)

        _add_textbox(
            slide, Inches(1.9), y - Inches(0.05), Inches(9.5), Inches(0.5),
            title, font_size=20, bold=True, color=BLACK
        )
        _add_textbox(
            slide, Inches(1.9), y + Inches(0.4), Inches(9.5), Inches(0.5),
            desc, font_size=16, color=GRAY
        )
        y += Inches(1.15)


def slide_solution(prs):
    """Slide 3: 解決策."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, WHITE)

    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "解決策", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    _add_textbox(
        slide, Inches(0.8), Inches(1.6), Inches(11), Inches(0.8),
        "前例に基づくアプローチ",
        font_size=24, bold=True, color=BLACK
    )

    # Flow diagram: 3 boxes with arrows
    box_w = Inches(3.2)
    box_h = Inches(3)
    gap = Inches(0.6)
    start_x = Inches(0.8)
    box_y = Inches(2.8)

    items = [
        ("① 集める", "全国の自治体・学術機関が\n公開したやさしい日本語の\n書き換え事例を収集"),
        ("② 整理する", "用語・文例をデータベース化\nJLPT難易度を自動判定\n出典ごとの書き換え率を算出"),
        ("③ 活用する", "Excelで検索するだけで\n前例に基づく判断材料が\nすぐに手に入る"),
    ]

    for i, (title, desc) in enumerate(items):
        x = start_x + i * (box_w + gap)
        box = _add_rounded_rect(slide, x, box_y, box_w, box_h, LIGHT_GREEN)
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.space_before = Pt(20)
        _add_run(p, title, font_size=22, bold=True, color=GREEN)

        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(16)
        _add_run(p2, desc, font_size=15, color=BLACK)

        # Arrow between boxes
        if i < 2:
            arrow_x = x + box_w + Inches(0.08)
            _add_textbox(
                slide, arrow_x, box_y + Inches(1.2), gap - Inches(0.16), Inches(0.6),
                "→", font_size=32, bold=True, color=GREEN,
                alignment=PP_ALIGN.CENTER
            )

    # Bottom note
    _add_textbox(
        slide, Inches(0.8), Inches(6.2), Inches(11), Inches(0.6),
        "人の判断を置き換えるものではなく、判断を支えるツール",
        font_size=18, bold=True, color=GREEN, alignment=PP_ALIGN.CENTER
    )


def slide_data_sources(prs):
    """Slide 4: データの出典."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    _set_slide_bg(slide, WHITE)

    # Title + underline
    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "データの出典", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    # Subtitle
    _add_textbox(
        slide, Inches(0.8), Inches(1.5), Inches(11), Inches(0.5),
        "3種類のデータを組み合わせて、幅広い前例を提供",
        font_size=20, bold=True, color=BLACK
    )

    # Corpus explainer
    _add_textbox(
        slide, Inches(0.8), Inches(2.1), Inches(11.5), Inches(0.9),
        "コーパスとは、言語研究のために体系的に集められた大量のテキストデータのこと。"
        "本ツールでは「原文」と「やさしい日本語」のペア（対訳）を集めた"
        "パラレルコーパスを活用しています。",
        font_size=14, color=GRAY
    )

    # 3-column cards
    card_w = Inches(3.7)
    card_h = Inches(4.0)
    gap = Inches(0.35)
    start_x = Inches(0.8)
    card_y = Inches(3.1)

    cards = [
        {
            "category": "行政ガイドライン",
            "rows": [
                ("作成者", "各自治体・省庁の職員"),
                ("内容", "用語の書き換え例"),
                ("件数", "17機関・2,800+語"),
                ("特徴", "公式な行政判断に基づく"),
            ],
        },
        {
            "category": "MATCHA コーパス",
            "rows": [
                ("作成者", "愛媛大学 + MATCHA社ライター"),
                ("内容", "旅行・文化記事の文の書き換え"),
                ("件数", "14,700+文対"),
                ("特徴", "プロのライターが実読者向けに作成"),
            ],
        },
        {
            "category": "JADES データセット",
            "rows": [
                ("作成者", "奈良先端大の専門家1名"),
                ("内容", "ニュース記事の文の書き換え"),
                ("件数", "3,900+文対"),
                ("特徴", "語彙＋文法の両方を平易化"),
            ],
        },
    ]

    for i, card in enumerate(cards):
        x = start_x + i * (card_w + gap)
        box = _add_rounded_rect(slide, x, card_y, card_w, card_h, LIGHT_GREEN)
        tf = box.text_frame
        tf.word_wrap = True

        # Category header
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.space_before = Pt(16)
        _add_run(p, card["category"], font_size=20, bold=True, color=GREEN)

        # Divider line (visual separator via a thin rect on the slide)
        _add_rect(slide, x + Inches(0.4), card_y + Inches(0.7),
                  card_w - Inches(0.8), Inches(0.03), MEDIUM_GREEN)

        # Detail rows
        for label, value in card["rows"]:
            p_label = tf.add_paragraph()
            p_label.alignment = PP_ALIGN.LEFT
            p_label.space_before = Pt(14)
            _add_run(p_label, f"  {label}", font_size=13, bold=True, color=DARK_GREEN)

            p_value = tf.add_paragraph()
            p_value.alignment = PP_ALIGN.LEFT
            p_value.space_before = Pt(2)
            _add_run(p_value, f"  {value}", font_size=14, color=BLACK)


def slide_data_scale(prs):
    """Slide 5: データの規模."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, WHITE)

    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "データの規模", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    # 4 stat cards
    card_w = Inches(2.6)
    card_h = Inches(2.4)
    gap = Inches(0.4)
    start_x = Inches(0.8)
    card_y = Inches(2.0)

    stats = [
        ("19", "出典"),
        ("2,800+", "用語ペア"),
        ("18,800+", "文例ペア"),
        ("22,000+", "JLPT語彙"),
    ]

    for i, (num, label) in enumerate(stats):
        x = start_x + i * (card_w + gap)
        _stat_card(slide, x, card_y, card_w, card_h, num, label)

    # Explanation row
    details = [
        "自治体・学術機関の\nガイドライン等",
        "「避難→にげる」のような\n語レベルの書き換え例",
        "文レベルの\nやさしい日本語書き換え例",
        "N1〜N5の難易度判定に\n使用する語彙データ",
    ]
    for i, detail in enumerate(details):
        x = start_x + i * (card_w + gap)
        _add_textbox(
            slide, x, card_y + card_h + Inches(0.2), card_w, Inches(1),
            detail, font_size=13, color=GRAY, alignment=PP_ALIGN.CENTER
        )


def slide_usage_search(prs):
    """Slide 6: 使い方① 検索タブ."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, WHITE)

    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "使い方 ①：検索", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    # Simulated search UI
    # Search box
    search_box = _add_rounded_rect(
        slide, Inches(1.2), Inches(1.8), Inches(4), Inches(0.7), RGBColor(0xFF, 0xFF, 0xCC)
    )
    _shape_text(search_box, "避難", font_size=22, bold=True, color=BLACK,
                alignment=PP_ALIGN.LEFT)

    _add_textbox(
        slide, Inches(5.5), Inches(1.85), Inches(4), Inches(0.6),
        "← 調べたい語を入力", font_size=16, color=GRAY
    )

    # Results area
    results_y = Inches(2.9)
    result_items = [
        ("難易度", "N2", "JLPTレベルに基づく難易度"),
        ("判定", "ほぼいつも言い換えられている", "文例での書き換え率に基づく判定"),
        ("用語ヒット", "8 件", "用語レベルの書き換え例の件数"),
        ("文例ヒット", "24 件", "文レベルの書き換え例の件数"),
    ]

    for i, (label, value, explanation) in enumerate(result_items):
        y = results_y + i * Inches(0.8)

        # Label
        label_box = _add_rounded_rect(
            slide, Inches(1.2), y, Inches(2), Inches(0.55), LIGHT_GREEN
        )
        _shape_text(label_box, label, font_size=16, bold=True, color=DARK_GREEN)

        # Value
        _add_textbox(
            slide, Inches(3.4), y + Inches(0.05), Inches(4), Inches(0.5),
            value, font_size=17, bold=True, color=BLACK
        )

        # Explanation
        _add_textbox(
            slide, Inches(7.5), y + Inches(0.05), Inches(5), Inches(0.5),
            explanation, font_size=14, color=GRAY
        )

    # Bottom: term results preview
    _add_rect(slide, Inches(0.8), Inches(5.7), Inches(11.7), Inches(0.04), MEDIUM_GREEN)
    _add_textbox(
        slide, Inches(0.8), Inches(5.9), Inches(11), Inches(0.5),
        "▼ 用語の書き換え結果（出典数の多い順に表示）",
        font_size=15, bold=True, color=GREEN
    )

    # Example row
    cols = ["検索語", "やさしい日本語", "出典数", "出典"]
    vals = ["避難", "にげる", "5", "入管庁、川崎市、札幌市…"]
    col_x = [Inches(1.2), Inches(3.5), Inches(6.5), Inches(8)]
    for j, (col, val) in enumerate(zip(cols, vals)):
        _add_textbox(
            slide, col_x[j], Inches(6.3), Inches(2), Inches(0.35),
            col, font_size=12, bold=True, color=GREEN
        )
        _add_textbox(
            slide, col_x[j], Inches(6.6), Inches(2), Inches(0.35),
            val, font_size=13, color=BLACK
        )


def slide_usage_examples(prs):
    """Slide 7: 使い方② 文例タブ."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, WHITE)

    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "使い方 ②：文例", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    _add_textbox(
        slide, Inches(0.8), Inches(1.6), Inches(11), Inches(0.8),
        "文レベルの書き換え例で、実際の使い方を確認",
        font_size=20, color=BLACK
    )

    # Example cards
    examples = [
        ("原文", "地震が発生した場合は、速やかに避難してください。",
         "やさしい日本語", "地震が　おきたら、すぐ　にげて　ください。",
         "言い換え"),
        ("原文", "本届出は、転入の届出と同時にすることができます。",
         "やさしい日本語", "この届出は、引っ越しの届出と一緒に出すことができます。",
         "言い換え"),
    ]

    y = Inches(2.5)
    for orig_label, orig, yasa_label, yasa, status in examples:
        # Card background
        _add_rounded_rect(
            slide, Inches(1), y, Inches(11), Inches(2), LIGHT_GRAY
        )

        # Original
        _add_textbox(
            slide, Inches(1.3), y + Inches(0.2), Inches(1.8), Inches(0.4),
            orig_label, font_size=13, bold=True, color=GRAY
        )
        _add_textbox(
            slide, Inches(1.3), y + Inches(0.55), Inches(8), Inches(0.5),
            orig, font_size=17, color=BLACK
        )

        # Arrow
        _add_textbox(
            slide, Inches(1.3), y + Inches(1.0), Inches(1), Inches(0.4),
            "↓", font_size=20, bold=True, color=GREEN
        )

        # Yasashii
        _add_textbox(
            slide, Inches(1.3), y + Inches(1.3), Inches(1.8), Inches(0.4),
            yasa_label, font_size=13, bold=True, color=GREEN
        )
        _add_textbox(
            slide, Inches(1.3), y + Inches(1.6), Inches(8), Inches(0.5),
            yasa, font_size=17, bold=True, color=GREEN
        )

        # Status badge
        badge = _add_rounded_rect(
            slide, Inches(10.2), y + Inches(0.8), Inches(1.5), Inches(0.5), GREEN
        )
        _shape_text(badge, status, font_size=14, bold=True, color=WHITE)

        y += Inches(2.3)


def slide_recommendation(prs):
    """Slide 8: 判定のしくみ."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, WHITE)

    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "判定のしくみ", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    _add_textbox(
        slide, Inches(0.8), Inches(1.6), Inches(11), Inches(0.8),
        "文例での書き換え率に基づいて、4段階の判定を表示",
        font_size=20, color=BLACK
    )

    # Threshold table
    thresholds = [
        ("80%以上", "ほぼいつも言い換えられている", RGBColor(0x2E, 0x7D, 0x32)),
        ("50〜79%", "過半数で言い換えられている", RGBColor(0x55, 0x8B, 0x2F)),
        ("20〜49%", "たまに言い換えられている", RGBColor(0xF5, 0x7F, 0x17)),
        ("20%未満", "大体そのまま使われている", RGBColor(0x78, 0x78, 0x78)),
    ]

    y = Inches(2.6)
    for rate, label, color in thresholds:
        # Rate box
        rate_box = _add_rounded_rect(
            slide, Inches(1.5), y, Inches(2.2), Inches(0.7), color
        )
        _shape_text(rate_box, rate, font_size=18, bold=True, color=WHITE)

        # Arrow
        _add_textbox(
            slide, Inches(3.9), y + Inches(0.05), Inches(0.6), Inches(0.6),
            "→", font_size=24, bold=True, color=color, alignment=PP_ALIGN.CENTER
        )

        # Label
        label_box = _add_rounded_rect(
            slide, Inches(4.6), y, Inches(5.5), Inches(0.7), LIGHT_GREEN
        )
        _shape_text(label_box, label, font_size=18, bold=True, color=color)

        y += Inches(0.95)

    # Explanation
    _, tf = _add_rich_textbox(
        slide, Inches(1.2), Inches(6.0), Inches(10), Inches(0.8)
    )
    p = tf.paragraphs[0]
    _add_run(p, "書き換え率 = ", font_size=15, color=GRAY)
    _add_run(p, "文例で言い換えられた回数 ÷ 文例の総数",
             font_size=15, bold=True, color=GRAY)
    p2 = _new_paragraph(tf)
    _add_run(p2, "※ 判定は参考情報です。最終的な判断は、文脈に応じて担当者が行います。",
             font_size=14, color=GRAY)


def slide_sources(prs):
    """Slide 9: 出典の信頼性."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, WHITE)

    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "出典の信頼性", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    _add_textbox(
        slide, Inches(0.8), Inches(1.6), Inches(11), Inches(0.8),
        "19の行政機関・学術機関の公開資料に基づく",
        font_size=20, color=BLACK
    )

    # Two columns: 行政 and 学術
    # 行政 sources
    admin_box = _add_rounded_rect(
        slide, Inches(0.8), Inches(2.5), Inches(5.8), Inches(4.2), LIGHT_GREEN
    )
    tf = admin_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.space_before = Pt(12)
    _add_run(p, "  行政機関（17件）", font_size=20, bold=True, color=GREEN)

    admin_sources = [
        "出入国在留管理庁・文化庁", "厚生労働省", "自治体国際化協会",
        "川崎市", "横浜市", "札幌市", "福岡市", "大阪市", "大阪府",
        "京都市", "愛知県", "三重県", "鳥取県", "岡山県", "入間市",
    ]
    for src in admin_sources:
        p2 = tf.add_paragraph()
        p2.space_before = Pt(3)
        _add_run(p2, f"    {src}", font_size=13, color=BLACK)

    # 学術 sources
    acad_box = _add_rounded_rect(
        slide, Inches(7), Inches(2.5), Inches(5.5), Inches(4.2), LIGHT_GREEN
    )
    tf2 = acad_box.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    p.space_before = Pt(12)
    _add_run(p, "  学術機関（2件）", font_size=20, bold=True, color=GREEN)

    acad_sources = [
        ("弘前大学", "災害基礎語彙集成"),
        ("愛媛大学", "MATCHAパラレルコーパス"),
        ("奈良先端科学技術大学院大学", "JADESデータセット"),
    ]
    for org, doc in acad_sources:
        p2 = tf2.add_paragraph()
        p2.space_before = Pt(10)
        _add_run(p2, f"    {org}", font_size=15, bold=True, color=BLACK)
        p3 = tf2.add_paragraph()
        p3.space_before = Pt(2)
        _add_run(p3, f"      {doc}", font_size=13, color=GRAY)

    # Bottom note
    _add_textbox(
        slide, Inches(0.8), Inches(6.9), Inches(11), Inches(0.5),
        "複数の出典が同じ書き換えを採用 → 合意度が高い = 信頼性が高い",
        font_size=16, bold=True, color=GREEN, alignment=PP_ALIGN.CENTER
    )


def slide_summary(prs):
    """Slide 10: まとめ."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, WHITE)

    _add_textbox(
        slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.8),
        "まとめ", font_size=36, bold=True, color=GREEN
    )
    _add_rect(slide, Inches(0.8), Inches(1.2), Inches(2), Inches(0.06), GREEN)

    benefits = [
        ("判断が速くなる",
         "前例をすぐに参照できるため、書き換えの検討時間を短縮"),
        ("根拠を示せる",
         "「○○市・△△県でも同じ書き換えを採用」と説明できる"),
        ("一貫性が生まれる",
         "部署を超えて、同じデータに基づいた書き換えが可能に"),
        ("データに基づく判断",
         "感覚ではなく、実際の書き換え率に基づいた意思決定"),
    ]

    y = Inches(1.8)
    for i, (title, desc) in enumerate(benefits):
        # Checkmark circle
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(1.2), y + Inches(0.1), Inches(0.45), Inches(0.45)
        )
        circle.fill.solid()
        circle.fill.fore_color.rgb = GREEN
        circle.line.fill.background()
        _shape_text(circle, "✓", font_size=18, bold=True, color=WHITE)

        _add_textbox(
            slide, Inches(2), y, Inches(9.5), Inches(0.5),
            title, font_size=22, bold=True, color=BLACK
        )
        _add_textbox(
            slide, Inches(2), y + Inches(0.5), Inches(9.5), Inches(0.5),
            desc, font_size=16, color=GRAY
        )
        y += Inches(1.2)

    # Key message box
    msg_box = _add_rounded_rect(
        slide, Inches(1.5), Inches(6.0), Inches(10.3), Inches(0.9), GREEN
    )
    _shape_text(
        msg_box,
        "前例は「正解」ではなく「判断材料」。最終判断は人が行う。",
        font_size=22, bold=True, color=WHITE
    )


def slide_next_steps(prs):
    """Slide 11: 次のステップ."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, GREEN)

    _add_rect(slide, Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.15), DARK_GREEN)

    _add_textbox(
        slide, Inches(0.8), Inches(0.8), Inches(11), Inches(0.8),
        "次のステップ", font_size=36, bold=True, color=WHITE
    )

    steps = [
        ("1. Excelファイルを開く",
         "やさしい日本語_前例リファレンス.xlsx を開くだけ。インストール不要。"),
        ("2. 「検索」タブで語を入力",
         "調べたい語を入力すると、難易度・判定・書き換え例がすぐに表示されます。"),
        ("3. 前例を参考に判断",
         "複数の出典の書き換え例を参考に、文脈に合った書き換えを選択してください。"),
        ("4. フィードバックを共有",
         "使ってみた感想や改善点があれば、ぜひお聞かせください。"),
    ]

    y = Inches(2.0)
    for title, desc in steps:
        step_box = _add_rounded_rect(
            slide, Inches(1.5), y, Inches(10.3), Inches(1.0), DARK_GREEN
        )
        tf = step_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.space_before = Pt(8)
        _add_run(p, f"  {title}", font_size=20, bold=True, color=WHITE)
        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        _add_run(p2, f"    {desc}", font_size=15, color=RGBColor(0xCC, 0xE8, 0xC4))

        y += Inches(1.2)


# ── Main ───────────────────────────────────────────────────────────────

def main():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    slide_title(prs)
    slide_problem(prs)
    slide_solution(prs)
    slide_data_sources(prs)
    slide_data_scale(prs)
    slide_usage_search(prs)
    slide_usage_examples(prs)
    slide_recommendation(prs)
    slide_sources(prs)
    slide_summary(prs)
    slide_next_steps(prs)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT))
    print(f"✓ Saved {OUTPUT}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
