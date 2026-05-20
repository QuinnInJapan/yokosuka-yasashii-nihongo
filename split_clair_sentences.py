#!/usr/bin/env python3
"""Interactive CLI tool to split CLAIR multi-paragraph entries into individual sentence pairs."""

import json
import os
import re
import sys

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "21_clair.json")
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), ".split_progress.json")

# ANSI escape codes
DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RESET = "\033[0m"


def strip_furigana(text):
    """Remove furigana in parentheses for cleaner display."""
    s = re.sub(r'（[ぁ-ゖー]+）', '', text)
    s = re.sub(r'\([ぁ-ゖー]+\)', '', s)
    return s


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"completed_indices": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


def is_multi_paragraph(entry):
    orig_lines = [l for l in entry["original"].split("\n") if l.strip()]
    yasa_lines = [l for l in entry["yasashii"].split("\n") if l.strip()]
    return len(orig_lines) > 1 or len(yasa_lines) > 1


def split_entry(entry):
    """Interactive alignment of a multi-paragraph entry. Returns list of new entries."""
    orig_lines = [l for l in entry["original"].split("\n") if l.strip()]
    yasa_lines = [l for l in entry["yasashii"].split("\n") if l.strip()]

    # Overview: show all lines side by side
    max_i = max(len(orig_lines), len(yasa_lines))
    print(f"\n{BOLD}{'─' * 80}{RESET}")
    print(f"{BOLD}  Original ({len(orig_lines)})                          Yasashii ({len(yasa_lines)}){RESET}")
    print(f"{BOLD}{'─' * 80}{RESET}")
    for i in range(max_i):
        o = orig_lines[i] if i < len(orig_lines) else ""
        y = strip_furigana(yasa_lines[i]) if i < len(yasa_lines) else ""
        # Truncate for overview so columns stay readable
        o_disp = (o[:36] + "…") if len(o) > 37 else o
        y_disp = (y[:36] + "…") if len(y) > 37 else y
        print(f"  {DIM}{i}{RESET} {CYAN}{o_disp:<38}{RESET}{DIM}│{RESET} {GREEN}{y_disp}{RESET}")
    print(f"{BOLD}{'─' * 80}{RESET}\n")

    pairs = []
    oi = 0  # orig cursor
    yi = 0  # yasa cursor

    while oi < len(orig_lines) or yi < len(yasa_lines):
        if oi >= len(orig_lines) and yi >= len(yasa_lines):
            break

        # Show already-accepted pairs as dim context
        if pairs:
            print(f"  {DIM}Paired so far:{RESET}")
            for pi, (po, py) in enumerate(pairs):
                print(f"    {DIM}{pi+1}. {po[:50]}{RESET}")
                print(f"    {DIM}   → {strip_furigana(py)[:50]}{RESET}")
            print()

        # Current pair
        o_text = orig_lines[oi] if oi < len(orig_lines) else None
        y_text = yasa_lines[yi] if yi < len(yasa_lines) else None

        print(f"  {BOLD}{CYAN}原文{RESET}  {CYAN}{o_text or '(end)'}{RESET}")
        print(f"  {BOLD}{GREEN}やさ{RESET}  {GREEN}{strip_furigana(y_text) if y_text else '(end)'}{RESET}")

        # Peek at next lines for context
        if oi + 1 < len(orig_lines):
            print(f"  {DIM}next 原文: {orig_lines[oi+1][:60]}{RESET}")
        if yi + 1 < len(yasa_lines):
            print(f"  {DIM}next やさ: {strip_furigana(yasa_lines[yi+1])[:60]}{RESET}")

        # Build available actions
        parts = []
        if o_text and y_text:
            parts.append(f"{BOLD}y{RESET}=pair")
        if o_text:
            parts.append(f"{BOLD}s{RESET}=skip原文")
        if y_text:
            parts.append(f"{BOLD}S{RESET}=skipやさ")
        if o_text and oi + 1 < len(orig_lines):
            parts.append(f"{BOLD}m{RESET}=merge原文↓")
        if y_text and yi + 1 < len(yasa_lines):
            parts.append(f"{BOLD}M{RESET}=mergeやさ↓")
        parts.append(f"{BOLD}k{RESET}=keep whole")
        parts.append(f"{BOLD}d{RESET}=delete")

        choice = input(f"\n  {YELLOW}>{RESET} {' '.join(parts)}: ").strip()

        if choice == "d":
            return []

        elif choice == "y" and o_text and y_text:
            pairs.append((orig_lines[oi], yasa_lines[yi]))
            oi += 1
            yi += 1
            print(f"  {DIM}  paired ✓{RESET}\n")

        elif choice == "s" and o_text:
            oi += 1
            print(f"  {DIM}  skipped orig →{RESET}\n")

        elif choice == "S" and y_text:
            yi += 1
            print(f"  {DIM}  skipped yasa →{RESET}\n")

        elif choice == "m" and o_text and oi + 1 < len(orig_lines):
            orig_lines[oi] = orig_lines[oi] + orig_lines[oi + 1]
            del orig_lines[oi + 1]
            print(f"  {DIM}  merged orig lines ↓{RESET}\n")

        elif choice == "M" and y_text and yi + 1 < len(yasa_lines):
            yasa_lines[yi] = yasa_lines[yi] + yasa_lines[yi + 1]
            del yasa_lines[yi + 1]
            print(f"  {DIM}  merged yasa lines ↓{RESET}\n")

        elif choice == "k":
            return [entry]

        else:
            print(f"  {MAGENTA}Invalid action. Try again.{RESET}\n")

    if not pairs:
        return [entry]

    # Build new entries from pairs
    result = []
    template = {k: v for k, v in entry.items()
                if k not in ("original", "original_normalized", "yasashii")}
    for orig, yasa in pairs:
        new_entry = dict(template)
        new_entry["original"] = orig
        new_entry["original_normalized"] = orig
        new_entry["yasashii"] = yasa
        result.append(new_entry)

    print(f"\n  {BOLD}→ Split into {len(result)} entries{RESET}")
    return result


def main():
    entries = load_data()
    progress = load_progress()
    completed = set(progress["completed_indices"])

    # Find multi-paragraph entries with their original indices
    multi_indices = []
    for i, entry in enumerate(entries):
        if is_multi_paragraph(entry):
            multi_indices.append(i)

    pending = [i for i in multi_indices if i not in completed]
    print(f"Total entries: {len(entries)}")
    print(f"Multi-paragraph entries: {len(multi_indices)}")
    print(f"Already completed: {len(completed)}")
    print(f"Remaining: {len(pending)}")

    if not pending:
        print("All multi-paragraph entries have been processed!")
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
        return

    for count, idx in enumerate(pending, 1):
        print(f"\n{BOLD}{MAGENTA}{'━' * 80}")
        print(f"  Entry {count}/{len(pending)}")
        print(f"{'━' * 80}{RESET}")

        entry = entries[idx]
        new_entries = split_entry(entry)

        # Replace the entry in the list
        entries[idx:idx + 1] = new_entries

        # If we inserted extra entries, adjust all subsequent indices
        offset = len(new_entries) - 1
        if offset != 0:
            # Update pending indices that come after this one
            for j in range(count, len(pending)):
                pending[j] += offset
            # Update completed indices that come after this one
            new_completed = set()
            for c in completed:
                if c > idx:
                    new_completed.add(c + offset)
                else:
                    new_completed.add(c)
            completed = new_completed

        completed.add(idx)

        # Save after each entry
        save_data(entries)
        save_progress({"completed_indices": sorted(completed)})
        print(f"  [saved]")

    print(f"\nDone! All {len(multi_indices)} multi-paragraph entries processed.")
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)


if __name__ == "__main__":
    main()
