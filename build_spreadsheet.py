#!/usr/bin/env python3
"""Build the やさしい日本語 precedent reference spreadsheet.

Tab order: 検索 → 文例 → 出典一覧 → 全データ → 使い方  (+ hidden _合意データ)
All user-facing headers in Japanese.
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import xlsxwriter

DATA = Path("data")


def strip_furigana(text: str) -> str:
    """Remove furigana in parentheses from text.

    Matches both half-width (ひらがな) and full-width （ひらがな） patterns.
    """
    s = re.sub(r'（[ぁ-ゖー]+）', '', text)
    s = re.sub(r'\([ぁ-ゖー]+\)', '', s)
    return s


def _jlpt_easier(a, b):
    """Return the easier (higher N number) of two JLPT levels."""
    return a if int(a[1:]) > int(b[1:]) else b


def load_jlpt_levels():
    """Load JLPT vocabulary from multiple sources.

    Sources:
      - jamsinclair/open-anki-jlpt-decks (n1.csv–n5.csv, MIT)
      - elzup/jlpt-word-list (elzup_all.csv, MIT)
      - Bluskyo/JLPT_Vocabulary (bluskyo_all.csv)

    For words appearing in multiple levels, uses the easiest (highest N number).
    """
    jlpt_dir = DATA / "jlpt"
    levels = {}  # expression → level string (e.g. "N3")

    def _add(expr, level):
        if expr in levels:
            levels[expr] = _jlpt_easier(levels[expr], level)
        else:
            levels[expr] = level

    # 1. jamsinclair per-level CSVs (process hardest first so easiest wins)
    for n in range(1, 6):
        csv_path = jlpt_dir / f"n{n}.csv"
        if not csv_path.exists():
            continue
        with open(csv_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                expr = row.get("expression", "").strip()
                if expr:
                    _add(expr, f"N{n}")

    # 2. elzup combined CSV (tags like "JLPT_1 JLPT")
    elzup_path = jlpt_dir / "elzup_all.csv"
    if elzup_path.exists():
        with open(elzup_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                expr = row.get("expression", "").strip()
                tags = row.get("tags", "")
                if expr:
                    for t in tags.split():
                        if t.startswith("JLPT_") and t != "JLPT":
                            suffix = t.split("_")[1]
                            # Handle both "JLPT_1" and "JLPT_N4" formats
                            if suffix.startswith("N"):
                                _add(expr, suffix)
                            else:
                                _add(expr, "N" + suffix)

    # 3. Bluskyo combined CSV (Word, JLPTLevel columns)
    bluskyo_path = jlpt_dir / "bluskyo_all.csv"
    if bluskyo_path.exists():
        with open(bluskyo_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                word = row.get("Word", "").strip()
                level = row.get("JLPTLevel", "").strip()
                if word and level:
                    _add(word, level)

    # 4. coolmule0 per-level CSVs (kanji + kana columns)
    for n in range(1, 6):
        csv_path = jlpt_dir / f"coolmule0_n{n}.csv"
        if not csv_path.exists():
            continue
        with open(csv_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                for col in ("kanji", "kana"):
                    expr = row.get(col, "").strip()
                    if expr:
                        _add(expr, f"N{n}")

    # 5. wordfreq frequency-based approximation (lowest priority — only fills gaps)
    wordfreq_path = jlpt_dir / "wordfreq_ja.csv"
    if wordfreq_path.exists():
        with open(wordfreq_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                expr = row.get("expression", "").strip()
                level = row.get("level", "").strip()
                if expr and level and expr not in levels:
                    levels[expr] = level

    print(f"Loaded {len(levels)} JLPT vocabulary entries")
    return levels


def load_source_short_names():
    """Load source_id → short_name mapping from sources.csv."""
    mapping = {}
    with open(DATA / "sources.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            mapping[row["source_id"]] = row.get("source_short_name", "")
    return mapping


def load_all_entries():
    """Load all per-source JSON files, sorted by source_id.

    Strips furigana from yasashii fields and deduplicates entries
    that become identical after stripping.
    """
    short_names = load_source_short_names()

    all_entries = []
    for jf in sorted(DATA.glob("*.json")):
        with open(jf, "r", encoding="utf-8") as f:
            all_entries.extend(json.load(f))

    # Strip furigana and remove spaces from yasashii, attach short_name
    for e in all_entries:
        y = strip_furigana(e["yasashii"])
        # Remove half-width and full-width spaces (分かち書き)
        y = y.replace(" ", "").replace("\u3000", "")
        e["yasashii"] = y
        e["source_short_name"] = short_names.get(e.get("source_id", ""), "")

    # Deduplicate: entries identical on (source_id, original, yasashii, entry_type)
    seen = set()
    deduped = []
    for e in all_entries:
        key = (e["source_id"], e["original"], e["yasashii"], e["entry_type"])
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    removed = len(all_entries) - len(deduped)
    if removed:
        print(f"Removed {removed} duplicate entries after furigana stripping")

    return deduped


def build_consensus_data(entries):
    """Build consensus rows from term entries.

    Returns list of (original_normalized, yasashii, source_count, source_list, notes_combined)
    sorted by source_count DESC then original ASC.
    """
    term_entries = [e for e in entries if e["entry_type"] == "term"]

    # Group: (original_normalized, yasashii) -> {sources, notes, retain}
    pivot = defaultdict(lambda: {"sources": set(), "notes": set(), "retain": False})
    for e in term_entries:
        key = (e["original_normalized"], e["yasashii"])
        bucket = pivot[key]
        bucket["sources"].add(e["source_short_name"])
        note = e.get("notes", "")
        if note:
            bucket["notes"].add(note)
        if e.get("retain_original"):
            bucket["retain"] = True

    rows = []
    for (orig, yasa), bucket in pivot.items():
        source_count = len(bucket["sources"])
        source_list = "、".join(sorted(bucket["sources"]))
        # Deduplicate notes, cap at 3, join with ；
        unique_notes = sorted(bucket["notes"])[:3]
        notes_combined = "；".join(unique_notes)
        if bucket["retain"]:
            if notes_combined:
                notes_combined += "　※原語を残す"
            else:
                notes_combined = "※原語を残す"
        rows.append((orig, yasa, source_count, source_list, notes_combined))

    rows.sort(key=lambda r: (-r[2], r[0]))
    return rows


def main():
    entries = load_all_entries()
    print(f"Loaded {len(entries)} entries")

    out_path = DATA / "やさしい日本語_前例リファレンス.xlsx"
    wb = xlsxwriter.Workbook(str(out_path))

    # --- Shared formats ---
    BODY_SIZE = 12
    HEADER_SIZE = 13
    BORDER_COLOR = "#BFBFBF"

    def _header(bg):
        return wb.add_format({
            "bold": True, "font_color": "white", "bg_color": bg,
            "font_size": HEADER_SIZE, "align": "center", "valign": "vcenter",
            "text_wrap": True, "border": 1, "border_color": "#808080",
        })

    header_fmt_green = _header("#3B7A28")
    header_fmt_gold = _header("#A67A00")
    header_fmt_blue = _header("#1F4E8C")
    header_fmt_teal = _header("#1A6298")
    header_fmt_purple = _header("#5E3B7E")

    # --- Cell formats with borders for data tables ---
    def _cell(extra=None):
        d = {
            "text_wrap": True, "valign": "top", "font_size": BODY_SIZE,
            "border": 1, "border_color": BORDER_COLOR,
        }
        if extra:
            d.update(extra)
        return wb.add_format(d)

    cell_fmt = _cell()
    cell_center_fmt = _cell({"align": "center"})
    cell_alt_fmt = _cell({"bg_color": "#EDF5EB"})
    cell_alt_center_fmt = _cell({"align": "center", "bg_color": "#EDF5EB"})
    cell_url_fmt = _cell({"font_color": "#0563C1", "underline": True})
    cell_alt_url_fmt = _cell({"font_color": "#0563C1", "underline": True, "bg_color": "#EDF5EB"})

    # Borderless versions for dynamic-array / non-table areas
    wrap_fmt = wb.add_format({"text_wrap": True, "valign": "top", "font_size": BODY_SIZE})
    center_fmt = wb.add_format({"align": "center", "valign": "top", "font_size": BODY_SIZE})

    # Search input formats
    label_fmt = wb.add_format({"bold": True, "font_size": 14})
    search_fmt = wb.add_format({
        "font_size": 16, "bg_color": "#FFF2CC",
        "border": 2, "border_color": "#BF8F00",
    })
    hint_fmt = wb.add_format({"font_size": 10, "font_color": "#666666"})
    count_fmt = wb.add_format({"font_size": BODY_SIZE, "font_color": "#333333"})
    url_fmt = wb.add_format({
        "font_color": "#0563C1", "underline": True, "valign": "top", "font_size": BODY_SIZE,
    })

    # --- Load JLPT data ---
    jlpt_levels = load_jlpt_levels()

    # --- Pre-compute consensus data ---
    consensus_rows = build_consensus_data(entries)
    print(f"Consensus rows: {len(consensus_rows)}")

    # ==================== Hidden: _合意データ ====================
    ws_hidden = wb.add_worksheet("_合意データ")
    print("Building '_合意データ' hidden sheet...")

    hidden_headers = ["original_normalized", "yasashii", "source_count", "source_list", "notes_combined"]
    for col, h in enumerate(hidden_headers):
        ws_hidden.write(0, col, h)

    for i, (orig, yasa, count, sources_str, notes) in enumerate(consensus_rows, 1):
        ws_hidden.write(i, 0, orig)
        ws_hidden.write(i, 1, yasa)
        ws_hidden.write(i, 2, count)
        ws_hidden.write(i, 3, sources_str)
        ws_hidden.write(i, 4, notes)

    # ==================== _JLPT ====================
    ws_jlpt = wb.add_worksheet("_JLPT")
    print("Building '_JLPT' hidden sheet...")

    jlpt_sorted = sorted(jlpt_levels.items())
    ws_jlpt.write(0, 0, "word")
    ws_jlpt.write(0, 1, "level")
    for i, (word, level) in enumerate(jlpt_sorted, 1):
        ws_jlpt.write(i, 0, word)
        ws_jlpt.write(i, 1, level)
    jlpt_row_count = len(jlpt_sorted) + 1  # 1-indexed last row
    # ==================== 1. 検索 TAB (term consensus search) ====================
    ws_lookup = wb.add_worksheet("検索")
    print("Building '検索' tab...")

    ws_lookup.activate()
    ws_lookup.set_selection("B1")

    ws_lookup.write(0, 0, "検索語を入力：", label_fmt)
    ws_lookup.merge_range("B1:D1", "", search_fmt)
    ws_lookup.write(1, 0, "↑ 検索したい語を入力してください（例：避難、届出、津波）", hint_fmt)

    # Column widths
    result_headers = ["原文", "やさしい日本語", "出典数", "出典", "備考"]
    result_widths = [36, 60, 12, 34, 30]
    for col, w in enumerate(result_widths):
        ws_lookup.set_column(col, col, w, wrap_fmt)

    # FILTER formulas referencing _合意データ
    clr = len(consensus_rows) + 1  # 1-indexed last row in hidden sheet
    lr = len(entries) + 1
    link_fmt = wb.add_format({"font_size": BODY_SIZE, "font_color": "#0563C1", "underline": True})

    # ── Stats box (rows 3–8) ──
    STATS_BG = "#F5F5F5"
    STATS_BORDER = "#999999"

    def _stats(extra=None):
        d = {
            "font_size": BODY_SIZE, "valign": "vcenter",
            "bg_color": STATS_BG, "border": 1, "border_color": STATS_BORDER,
        }
        if extra:
            d.update(extra)
        return wb.add_format(d)

    stats_header_fmt = _stats({
        "bold": True, "font_color": "white", "bg_color": "#3B7A28",
        "font_size": HEADER_SIZE,
    })
    stats_label_fmt = _stats({"font_color": "#333333", "indent": 1})
    stats_value_fmt = _stats({"bold": True, "font_color": "#1A1A1A"})
    stats_sub_label_fmt = _stats({"font_color": "#555555", "indent": 3})
    stats_sub_value_fmt = _stats({"font_color": "#333333"})
    stats_link_fmt = _stats({"font_color": "#0563C1", "underline": True})
    stats_blank_fmt = _stats()

    # Helper: fill remaining stats columns with blank bg
    def _fill_stats_row(row, start_col=2):
        for c in range(start_col, 5):
            ws_lookup.write_blank(row, c, None, stats_blank_fmt)

    # Shared sub-expressions for sentence stats
    bunrei_total = (
        f"SUMPRODUCT(ISNUMBER(SEARCH($B$1,'全データ'!$G$2:$G${lr}))*"
        f"('全データ'!$F$2:$F${lr}=\"sentence\")*1)"
    )
    bunrei_yasashiku = (
        f"SUMPRODUCT(ISNUMBER(SEARCH($B$1,'全データ'!$G$2:$G${lr}))*"
        f"ISERROR(SEARCH($B$1,'全データ'!$I$2:$I${lr}))*"
        f"('全データ'!$F$2:$F${lr}=\"sentence\")*1)"
    )
    pct_expr = f"{bunrei_yasashiku}/{bunrei_total}"

    # ── Row 3: section header ──
    ws_lookup.write(3, 0, "検索サマリー", stats_header_fmt)
    for c in range(1, 5):
        ws_lookup.write_blank(3, c, None, stats_header_fmt)

    # ── Row 4: 難易度 ──
    ws_lookup.write(4, 0, "難易度", stats_label_fmt)
    difficulty_formula = (
        f'=IF($B$1="","",IFERROR('
        f'SWITCH(INDEX(\'_JLPT\'!$B$2:$B${jlpt_row_count},'
        f'MATCH($B$1,\'_JLPT\'!$A$2:$A${jlpt_row_count},0)),'
        f'"N5","やさしい（N5）","N4","ふつう（N4）","N3","やや難しい（N3）",'
        f'"N2","難しい（N2）","N1","とても難しい（N1）"),'
        f'"該当なし"))'
    )
    ws_lookup.write_formula(4, 1, difficulty_formula, stats_value_fmt)
    _fill_stats_row(4)

    # ── Row 5: 判定 (recommendation — most actionable, show early) ──
    ws_lookup.write(5, 0, "判定", stats_label_fmt)
    rec_formula = (
        f'=IF($B$1="","",IFERROR('
        f'IF({pct_expr}>=0.8,"ほぼいつも言い換えられている",'
        f'IF({pct_expr}>=0.5,"過半数で言い換えられている",'
        f'IF({pct_expr}>=0.2,"たまに言い換えられている",'
        f'"大体そのまま使われている"))),"ー"))'
    )
    ws_lookup.write_formula(5, 1, rec_formula, stats_value_fmt)
    # Explanation in col C-D
    rec_hint_fmt = _stats({"font_color": "#888888", "font_size": 10})
    ws_lookup.merge_range(5, 2, 5, 4, "", rec_hint_fmt)
    ws_lookup.write(5, 2, "← 文例での言い換え率に基づく", rec_hint_fmt)

    # ── Row 6: 言い換え率 ──
    ws_lookup.write(6, 0, "言い換え率", stats_label_fmt)
    pct_formula = (
        f'=IF($B$1="","",IFERROR(TEXT({pct_expr},"0%"),"ー"))'
    )
    ws_lookup.write_formula(6, 1, pct_formula, stats_value_fmt)
    _fill_stats_row(6)

    # ── Row 7: spacer/divider ──
    stats_divider_fmt = _stats({"top": 2, "top_color": "#CCCCCC", "bg_color": STATS_BG})
    for c in range(5):
        ws_lookup.write_blank(7, c, None, stats_divider_fmt)

    # ── Row 8: 用語ヒット ──
    ws_lookup.write(8, 0, "用語ヒット", stats_label_fmt)
    count_consensus_formula = (
        f'=IF($B$1="","",IFERROR(SUMPRODUCT(ISNUMBER(SEARCH($B$1,'
        f"'_合意データ'!$A$2:$A${clr}))*1)"
        f'&" 件",""))'
    )
    ws_lookup.write_formula(8, 1, count_consensus_formula, stats_value_fmt)
    _fill_stats_row(8)

    # ── Row 9: 文例ヒット + link ──
    ws_lookup.write(9, 0, "文例ヒット", stats_label_fmt)
    count_bunrei_total_formula = (
        f'=IF($B$1="","",IFERROR({bunrei_total}&" 件",""))'
    )
    ws_lookup.write_formula(9, 1, count_bunrei_total_formula, stats_value_fmt)
    ws_lookup.write_url(9, 2, "internal:'文例'!A1", stats_link_fmt, "→ 文例タブへ")
    for c in range(3, 5):
        ws_lookup.write_blank(9, c, None, stats_blank_fmt)

    # ── Row 10: やさしくされた (indented) ──
    ws_lookup.write(10, 0, "やさしくされた", stats_sub_label_fmt)
    ws_lookup.write_formula(
        10, 1,
        f'=IF($B$1="","",IFERROR({bunrei_yasashiku}&" 件",""))',
        stats_sub_value_fmt,
    )
    _fill_stats_row(10)

    # ── Row 11: そのまま (indented) ──
    ws_lookup.write(11, 0, "そのまま", stats_sub_label_fmt)
    ws_lookup.write_formula(
        11, 1,
        f'=IF($B$1="","",IFERROR(({bunrei_total}-{bunrei_yasashiku})&" 件",""))',
        stats_sub_value_fmt,
    )
    _fill_stats_row(11)

    # ── Conditional formatting: difficulty (row 4) ──
    diff_range = [4, 0, 4, 4]
    diff_labels = [
        ("とても難しい", "#F8D7DA", "#842029"),
        ("やや難しい",   "#FFF3CD", "#664D03"),
        ("難しい",       "#FCE4D6", "#984C0C"),
        ("ふつう",       "#D1E7DD", "#0F5132"),
        ("やさしい",     "#CFE2FF", "#084298"),
    ]
    for label, bg, fc in diff_labels:
        fmt = wb.add_format({
            "bg_color": bg, "font_color": fc, "valign": "vcenter", "bold": True,
            "font_size": BODY_SIZE, "border": 1, "border_color": STATS_BORDER,
        })
        ws_lookup.conditional_format(*diff_range, {
            "type": "text",
            "criteria": "containing",
            "value": label,
            "format": fmt,
        })

    # ── Conditional formatting: 判定 (row 5) ──
    rec_range = [5, 0, 5, 1]
    rec_labels = [
        ("ほぼいつも言い換えられている", "#F8D7DA", "#842029"),
        ("過半数で言い換えられている",   "#FFF3CD", "#664D03"),
        ("たまに言い換えられている",     "#D1E7DD", "#0F5132"),
        ("大体そのまま使われている",     "#CFE2FF", "#084298"),
    ]
    for label, bg, fc in rec_labels:
        fmt = wb.add_format({
            "bg_color": bg, "font_color": fc, "valign": "vcenter", "bold": True,
            "font_size": BODY_SIZE, "border": 1, "border_color": STATS_BORDER,
        })
        ws_lookup.conditional_format(*rec_range, {
            "type": "text",
            "criteria": "containing",
            "value": label,
            "format": fmt,
        })

    # ── Result table (row 13: headers, row 14+: data) ──
    RESULT_HEADER_ROW = 13
    RESULT_DATA_ROW = RESULT_HEADER_ROW + 1

    for col, h in enumerate(result_headers):
        ws_lookup.write(RESULT_HEADER_ROW, col, h, header_fmt_green)

    ws_lookup.freeze_panes(RESULT_DATA_ROW, 0)

    cond_consensus = (
        f'ISNUMBER(SEARCH(検索!$B$1,\'_合意データ\'!$A$2:$A${clr}))'
    )

    hidden_cols = ["A", "B", "C", "D", "E"]
    exact_match = f'EXACT(検索!$B$1,FILTER(\'_合意データ\'!$A$2:$A${clr},{cond_consensus}))'
    for col_idx, data_col in enumerate(hidden_cols):
        empty_msg = '"検索語を入力してください"' if col_idx == 0 else '""'
        no_results_msg = '""'
        formula = (
            f'=IF(検索!$B$1="",{empty_msg},IFERROR(SORTBY('
            f'FILTER(\'_合意データ\'!${data_col}$2:${data_col}${clr},{cond_consensus}),'
            f'{exact_match},-1,'
            f'FILTER(\'_合意データ\'!$C$2:$C${clr},{cond_consensus}),-1,'
            f'FILTER(\'_合意データ\'!$A$2:$A${clr},{cond_consensus}),1'
            f'),{no_results_msg}))'
        )
        ws_lookup.write_dynamic_array_formula(
            RESULT_DATA_ROW, col_idx, RESULT_DATA_ROW, col_idx, formula
        )

    # Pre-format result rows with bordered cells
    for row in range(RESULT_DATA_ROW + 1, RESULT_DATA_ROW + 1 + len(consensus_rows)):
        for col in range(len(hidden_cols)):
            ws_lookup.write_blank(row, col, None, cell_fmt)

    # Conditional formatting: source-count tiers (strong enough to read)
    source_count_range_full = [
        RESULT_DATA_ROW, 0, RESULT_DATA_ROW + len(consensus_rows), 4
    ]
    source_count_tiers = [
        (5, None, "#D1E7DD", "#1A1A1A"),   # light green bg, black text
        (4, 4,    "#DFF0D8", "#1A1A1A"),   # softer green bg
        (3, 3,    "#EAF4E7", "#1A1A1A"),   # pale green bg
        (2, 2,    "#F2F8F0", "#333333"),   # very pale green bg
    ]
    cr = RESULT_DATA_ROW + 1  # 1-indexed row for first data cell
    for min_val, max_val, bg, fc in source_count_tiers:
        fmt = wb.add_format({
            "bg_color": bg, "font_color": fc,
            "border": 1, "border_color": BORDER_COLOR,
            "text_wrap": True, "valign": "top", "font_size": BODY_SIZE,
        })
        if max_val is None:
            ws_lookup.conditional_format(*source_count_range_full, {
                "type": "formula",
                "criteria": f'=$C{cr}>={min_val}',
                "format": fmt,
            })
        else:
            ws_lookup.conditional_format(*source_count_range_full, {
                "type": "formula",
                "criteria": f'=AND($C{cr}>={min_val},$C{cr}<={max_val})',
                "format": fmt,
            })

    # ==================== 2. 文例 TAB (sentence examples) ====================
    ws_bunrei = wb.add_worksheet("文例")
    print("Building '文例' tab...")

    ws_bunrei.write_url(0, 0, "internal:'検索'!B1", link_fmt, "← 検索タブに戻る")
    ws_bunrei.write(0, 1, "検索語を含む文レベルの書き換え例", hint_fmt)

    # Result count formula in row 1
    bunrei_total_b = (
        f"SUMPRODUCT(ISNUMBER(SEARCH(検索!$B$1,'全データ'!$G$2:$G${lr}))*"
        f"('全データ'!$F$2:$F${lr}=\"sentence\")*1)"
    )
    bunrei_yasashiku_b = (
        f"SUMPRODUCT(ISNUMBER(SEARCH(検索!$B$1,'全データ'!$G$2:$G${lr}))*"
        f"ISERROR(SEARCH(検索!$B$1,'全データ'!$I$2:$I${lr}))*"
        f"('全データ'!$F$2:$F${lr}=\"sentence\")*1)"
    )
    bunrei_count_formula = (
        f'=IFERROR("文例: "&{bunrei_total_b}'
        f'&" 件（やさしくされた: "&{bunrei_yasashiku_b}'
        f'&" 件 / そのまま: "&({bunrei_total_b}-{bunrei_yasashiku_b})'
        f'&" 件）","")'
    )
    ws_bunrei.write_formula(1, 0, bunrei_count_formula, count_fmt)

    bunrei_headers = ["原文", "やさしい日本語", "出典", "変換"]
    bunrei_widths = [48, 72, 20, 20]

    for col, (h, w) in enumerate(zip(bunrei_headers, bunrei_widths)):
        ws_bunrei.write(2, col, h, header_fmt_purple)
        ws_bunrei.set_column(col, col, w, cell_fmt)

    ws_bunrei.freeze_panes(3, 0)

    # Pre-format result rows with bordered cells
    max_bunrei = sum(1 for e in entries if e["entry_type"] == "sentence")
    for row in range(3, 3 + max_bunrei):
        for col in range(len(bunrei_headers)):
            ws_bunrei.write_blank(row, col, None, cell_fmt)

    # HSTACK formula without LET (LET fails silently in Excel for Mac).
    # All 4 columns spill from one formula to guarantee alignment.
    cond_bunrei = (
        f"ISNUMBER(SEARCH(検索!$B$1,'全データ'!$G$2:$G${lr}))"
        f"*('全データ'!$F$2:$F${lr}=\"sentence\")"
    )
    f_orig = f"FILTER('全データ'!$G$2:$G${lr},{cond_bunrei})"
    f_yasa = f"FILTER('全データ'!$I$2:$I${lr},{cond_bunrei})"
    f_src = f"FILTER('全データ'!$B$2:$B${lr},{cond_bunrei})"

    bunrei_formula = (
        f'=IF(検索!$B$1="",{{"← 検索タブで語を入力してください","","",""}},IFERROR(SORTBY('
        f'HSTACK({f_orig},{f_yasa},{f_src},'
        f'IF(ISNUMBER(SEARCH(検索!$B$1,{f_yasa})),"そのまま","やさしくされた")),'
        f'ISERROR(SEARCH(検索!$B$1,{f_yasa})),-1,'
        f'EXACT(検索!$B$1,{f_orig}),-1,'
        f'{f_src},1'
        f'),{{"","","",""}}))'
    )
    ws_bunrei.write_dynamic_array_formula(3, 0, 3, 3, bunrei_formula)

    # Conditional formatting on 変換 column
    henkan_range = [3, 3, 3 + max_bunrei, 3]
    henkan_yasashiku_fmt = wb.add_format({
        "bg_color": "#FCE4D6", "font_color": "#984C0C",
        "border": 1, "border_color": BORDER_COLOR,
        "text_wrap": True, "valign": "top", "font_size": BODY_SIZE,
    })
    henkan_sonomama_fmt = wb.add_format({
        "bg_color": "#D1E7DD", "font_color": "#0F5132",
        "border": 1, "border_color": BORDER_COLOR,
        "text_wrap": True, "valign": "top", "font_size": BODY_SIZE,
    })
    ws_bunrei.conditional_format(*henkan_range, {
        "type": "text", "criteria": "containing",
        "value": "やさしくされた", "format": henkan_yasashiku_fmt,
    })
    ws_bunrei.conditional_format(*henkan_range, {
        "type": "text", "criteria": "containing",
        "value": "そのまま", "format": henkan_sonomama_fmt,
    })

    # ==================== 3. 出典一覧 TAB (sources) ====================
    ws_sources = wb.add_worksheet("出典一覧")
    print("Building '出典一覧' tab...")

    # Reordered: 略称, 件数, 出典（組織）, 出典（文書）, 分類, 語彙基準, 概要, 特徴・注意点, URL, 発行年
    source_headers = ["略称", "件数", "出典（組織）", "出典（文書）", "分類", "語彙基準", "概要", "特徴・注意点", "URL", "発行年"]
    source_widths = [20, 10, 30, 44, 12, 18, 48, 48, 12, 10]

    for col, (h, w) in enumerate(zip(source_headers, source_widths)):
        ws_sources.write(0, col, h, header_fmt_teal)
        ws_sources.set_column(col, col, w)

    # Load sources.csv
    sources_csv = DATA / "sources.csv"
    source_rows = []
    with open(sources_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sid = row["source_id"]
            count = sum(1 for e in entries if e.get("source_id") == sid)
            source_rows.append((
                row.get("source_short_name", ""),
                count,
                row["source_org"],
                row["source_document"],
                row.get("source_category", ""),
                row.get("source_vocab_standard", ""),
                row.get("source_description", ""),
                row.get("source_notes", ""),
                row.get("source_url", ""),
                row.get("source_date", ""),
            ))

    for i, (short, count, org, doc, cat, vocab, desc, notes, url, date) in enumerate(source_rows, 1):
        if i % 2 == 0:
            fmt, cfmt, ufmt = cell_alt_fmt, cell_alt_center_fmt, cell_alt_url_fmt
        else:
            fmt, cfmt, ufmt = cell_fmt, cell_center_fmt, cell_url_fmt
        ws_sources.write(i, 0, short, fmt)
        ws_sources.write(i, 1, count, cfmt)
        ws_sources.write(i, 2, org, fmt)
        ws_sources.write(i, 3, doc, fmt)
        ws_sources.write(i, 4, cat, cfmt)
        ws_sources.write(i, 5, vocab, fmt)
        ws_sources.write(i, 6, desc, fmt)
        ws_sources.write(i, 7, notes, fmt)
        if url:
            ws_sources.write_url(i, 8, url, ufmt, string="リンク")
        else:
            ws_sources.write(i, 8, "", fmt)
        ws_sources.write(i, 9, date, cfmt)

    ws_sources.freeze_panes(1, 2)
    ws_sources.autofilter(0, 0, len(source_rows), len(source_headers) - 1)

    # ==================== 5. 全データ TAB (raw data) ====================
    ws_data = wb.add_worksheet("全データ")
    print("Building '全データ' tab...")

    # Internal keys for data lookup
    data_keys = [
        "source_org", "source_short_name", "source_document", "source_date", "domain",
        "entry_type", "original", "original_normalized", "yasashii",
        "notes", "retain_original", "is_negative_example",
    ]
    # Japanese display headers
    data_headers_jp = [
        "組織", "略称", "文書名", "発行年", "分野",
        "種別", "原文", "原文（正規化）", "やさしい日本語",
        "備考", "原語保持", "非推奨例",
    ]
    data_widths = [20, 20, 34, 10, 12, 11, 36, 26, 48, 24, 14, 14]

    for col, (h, w) in enumerate(zip(data_headers_jp, data_widths)):
        ws_data.write(0, col, h, header_fmt_blue)
        ws_data.set_column(col, col, w)

    for i, entry in enumerate(entries, 1):
        fmt = cell_alt_fmt if i % 2 == 0 else cell_fmt
        for col, key in enumerate(data_keys):
            val = entry.get(key, "")
            if isinstance(val, bool):
                val = "○" if val else ""
            elif isinstance(val, str):
                val = val.replace("\n", "／")
            ws_data.write(i, col, val, fmt)

    ws_data.freeze_panes(1, 0)
    ws_data.autofilter(0, 0, len(entries), len(data_keys) - 1)

    # ==================== 使い方 TAB ====================
    ws_help = wb.add_worksheet("使い方")
    print("Building '使い方' tab...")

    ws_help.hide_gridlines(2)
    ws_help.set_column(0, 0, 4)   # left margin
    ws_help.set_column(1, 1, 80)  # content

    help_title_fmt = wb.add_format({
        "bold": True, "font_size": 18, "font_color": "#1A1A1A",
        "bottom": 2, "bottom_color": "#3B7A28",
    })
    help_h2_fmt = wb.add_format({
        "bold": True, "font_size": 14, "font_color": "#3B7A28",
    })
    help_body_fmt = wb.add_format({
        "font_size": 12, "text_wrap": True, "valign": "top",
    })
    help_step_fmt = wb.add_format({
        "font_size": 12, "text_wrap": True, "valign": "top",
        "bold": True,
    })
    help_note_fmt = wb.add_format({
        "font_size": 11, "font_color": "#555555", "text_wrap": True,
        "valign": "top", "italic": True,
    })

    r = 1  # start row (row 0 = margin)
    ws_help.write(r, 1, "やさしい日本語 前例リファレンス — 使い方", help_title_fmt)
    r += 2

    ws_help.write(r, 1, "このシートについて", help_h2_fmt); r += 1
    ws_help.write(r, 1,
        "市役所の文書をやさしい日本語に書き換えるとき、過去の書き換え例を検索できるツールです。"
        "複数の公的機関の資料から集めた用語・文例データをもとに、言い換えの参考情報を表示します。",
        help_body_fmt)
    r += 2

    ws_help.write(r, 1, "基本の使い方", help_h2_fmt); r += 1
    steps = [
        ("① 検索タブで語を入力", "「検索」タブの黄色い欄に、調べたい語（例：避難、届出、津波）を入力します。"),
        ("② サマリーを確認", "難易度・判定・言い換え率が表示されます。判定は文例での実際の言い換え率に基づきます。"),
        ("③ 用語の結果を確認", "下の表に、過去の書き換え例が出典数の多い順に表示されます。出典数が多いほど信頼性が高い例です。"),
        ("④ 文例を確認", "「文例」タブに切り替えると、その語を含む文レベルの書き換え例が表示されます。"
         "「変換」列で、語がやさしくされたか（やさしくされた）、そのまま残されたか（そのまま）がわかります。"),
    ]
    for title, desc in steps:
        ws_help.write(r, 1, title, help_step_fmt); r += 1
        ws_help.write(r, 1, desc, help_body_fmt); r += 2

    ws_help.write(r, 1, "タブの説明", help_h2_fmt); r += 1
    tabs = [
        ("検索", "メインの検索画面。語を入力すると、用語の書き換え例とサマリーが表示されます。"),
        ("文例", "検索語を含む文レベルの書き換え例。実際の文書でどう言い換えられたかを確認できます。"),
        ("出典一覧", "データの出典元一覧。各資料の組織・文書名・URLなどを確認できます。"),
        ("全データ", "全エントリの生データ。フィルタで自由に絞り込めます。"),
    ]
    for tab, desc in tabs:
        ws_help.write(r, 1, f"「{tab}」— {desc}", help_body_fmt); r += 1
    r += 1

    ws_help.write(r, 1, "補足", help_h2_fmt); r += 1
    ws_help.write(r, 1,
        "難易度はJLPTの語彙レベル（N5〜N1）に基づいています。N5がやさしく、N1が最も難しい語です。"
        "「該当なし」と出た場合は、JLPTリストに含まれない語です。",
        help_note_fmt)
    r += 1
    ws_help.write(r, 1,
        f"収録データ: 用語 {len(consensus_rows):,} 件 / 文例 {max_bunrei:,} 件 / "
        f"出典 {len(source_rows)} 件 / JLPT語彙 {len(jlpt_levels):,} 語",
        help_note_fmt)

    # ==================== Print settings ====================
    for ws in [ws_lookup, ws_bunrei, ws_sources, ws_data, ws_help]:
        ws.set_landscape()
        ws.fit_to_pages(1, 0)

    # ==================== DONE ====================
    wb.close()
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
