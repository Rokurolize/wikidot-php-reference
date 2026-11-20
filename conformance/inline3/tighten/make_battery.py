#!/usr/bin/env python3
"""Generate the R2-inline3 Tighten (rule 53) whole-document battery.

Each record is {"id","source"} as consumed by both the shared reference
harness ref-php/harness/batch.php and the one shared ftml dumper at
conformance-refphp/inline3/rust-dump/. Sources are literal Wikitext;
battery-notes.md records intent. Pure trailing-space shapes are marked
"dumper-only" in the notes: Wikidot normalizes trailing whitespace on save,
so a saved-page probe cannot settle them and they are compared only on the
reference/dumper sides. All other shapes are eligible for live probing.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# (id, source, intent, dumper_only)
CASES = [
    # --- newlines in plain text / soft breaks / consecutive blank lines ---
    ("tighten01", "one line only", "plain text, no newline", False),
    ("tighten02", "a\nb", "single soft break", False),
    ("tighten03", "a\nb\nc", "two soft breaks", False),
    ("tighten04", "a\n\nb", "one blank line (paragraph break)", False),
    ("tighten05", "a\n\n\nb", "two blank lines (three newlines)", False),
    ("tighten06", "a\n\n\n\nb", "three blank lines (four newlines)", False),
    ("tighten07", "a\n\n\n\n\n\nb", "six consecutive newlines", False),
    ("tighten08", "\nleading newline", "newline at very start of source (save-normalized)", True),
    ("tighten09", "\n\nleading blank line", "two newlines at very start (save-normalized)", True),
    ("tighten10", "trailing newline\n", "single trailing newline (save-normalized)", True),
    ("tighten11", "trailing blank line\n\n", "two trailing newlines (save-normalized)", True),
    ("tighten12", "\n", "source is a single newline (save-normalized)", True),
    ("tighten13", "\n\n\n", "source is three newlines (save-normalized)", True),
    ("tighten14", "a\n b", "newline then a leading space on next line", False),
    ("tighten15", "a \nb", "space before a soft break (pure trailing space at line end)", True),
    ("tighten16", "a \n b", "space on both sides of a soft break (pre-break space save-normalized)", True),
    ("tighten17", "a  \n\n b", "two spaces before a paragraph break", True),
    ("tighten18", "a  b", "two spaces inside a line", False),
    ("tighten19", "a   b", "three spaces inside a line", False),
    ("tighten20", "  leading spaces", "leading spaces at start (save-normalized)", True),
    ("tighten21", "trailing spaces  ", "pure trailing spaces at end", True),
    ("tighten22", "a\t\tb", "interior tab run", False),
    ("tighten23", "a \t b", "mixed space/tab run", False),

    # --- line breaks at element edges (each sibling inline marker) ---
    ("tighten24", "a\n**bold**", "newline immediately before strong", False),
    ("tighten25", "**bold**\na", "newline immediately after strong", False),
    ("tighten26", "a\n//em//", "newline before emphasis", False),
    ("tighten27", "//em//\na", "newline after emphasis", False),
    ("tighten28", "a\n##red|x##", "newline before color span", False),
    ("tighten29", "##red|x##\na", "newline after color span", False),
    ("tighten30", "a\n__u__", "newline before underline", False),
    ("tighten31", "__u__\na", "newline after underline", False),
    ("tighten32", "a\n--s--", "newline before strike", False),
    ("tighten33", "--s--\na", "newline after strike", False),
    ("tighten34", "a\n{{tt}}", "newline before monospace", False),
    ("tighten35", "{{tt}}\na", "newline after monospace", False),
    ("tighten36", "a\n^^sup^^", "newline before superscript", False),
    ("tighten37", "^^sup^^\na", "newline after superscript", False),
    ("tighten38", "a\n,,sub,,", "newline before subscript", False),
    ("tighten39", ",,sub,,\na", "newline after subscript", False),

    # --- leading/trailing whitespace around spans (inherited Colortext residual) ---
    ("tighten40", "##red| A##", "leading space inside color span", False),
    ("tighten41", "##red|A ##", "trailing space inside color span (probed in follow-up campaign)", False),
    ("tighten42", "##red| A ##", "both edges inside color span (probed in follow-up campaign)", False),
    ("tighten43", "x ##red| A## y", "leading-space color span embedded in text", False),
    ("tighten44", "x ##red|A ## y", "trailing-space color span embedded in text", False),
    ("tighten45", "[[#x| A ]]", "leading/trailing space in anchor label", False),
    ("tighten46", "** A **", "spaces just inside strong markers", False),
    ("tighten47", "// A //", "spaces just inside emphasis markers", False),
    ("tighten48", "__ A __", "spaces just inside underline markers", False),
    ("tighten49", "-- A --", "spaces just inside strike markers", False),
    ("tighten50", "A ##red|B## C", "color span with clean surrounding spaces", False),

    # --- underline empty-pair trailing-space shapes (inherited Underline residual) ---
    ("tighten51", "Empty ____", "empty underline pair at end of line (p02 shape; probed in follow-up)", False),
    ("tighten52", "x ____ y", "empty pair between spaces (ftml collapses to x y)", False),
    ("tighten53", "____ x", "empty pair before space and text", False),
    ("tighten54", "x____", "empty pair directly after text", False),
    ("tighten55", "a ____ b ____ c", "two empty pairs with spaces", False),
    ("tighten56", "Empty ____\nnext", "empty pair at line end followed by soft break", False),

    # --- seams with each earlier rule's settled output ---
    ("tighten57", "para one\n\npara two", "paragraph seam", False),
    ("tighten58", "* item one\n* item two", "native list lines", False),
    ("tighten59", "+++ heading\nafter", "heading then soft break", False),
    ("tighten60", "[[code]]a\nb[[/code]]", "newline inside code block", False),
    ("tighten61", "{{{a\nb}}}", "newline inside raw block", False),
    ("tighten62", "> quoted one\n> quoted two", "blockquote lines", False),
    ("tighten63", "|| head ||\n|| cell ||", "table rows", False),
    ("tighten64", "a -- b\nc", "typography dash then soft break", False),
    ("tighten65", "...\nnext", "typography ellipsis then soft break", False),
    ("tighten66", "a\\\\b\nc", "explicit line break then soft break", False),
    ("tighten67", "##red|A\nB##", "color pair crossing a soft break", False),
    ("tighten68", "**A\nB**", "strong pair crossing a soft break", False),
    ("tighten69", "a\n\n[[div]]x[[/div]]\n\nb", "div block with blank-line seams", False),
    ("tighten70", "a  \n\nb  \n\nc", "blank-line seams with trailing spaces", True),
]


def main():
    with open(os.path.join(HERE, "battery.jsonl"), "w", encoding="utf-8") as f:
        for cid, src, _intent, _dump_only in CASES:
            f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "battery-notes.md"), "w", encoding="utf-8") as f:
        f.write("# R2-inline3 Tighten battery notes\n\n")
        f.write("dumper-only cases are shapes that live cannot settle because Wikidot "
                "normalizes leading/trailing whitespace and blank lines on save; they are "
                "compared only between the reference and the ftml dumper.\n\n")
        for cid, src, intent, dump_only in CASES:
            shown = src.replace("\\", "\\\\").replace("\n", "\\n")
            tag = " [DUMPER-ONLY]" if dump_only else ""
            f.write(f"- {cid}{tag}: {intent} | source: `{shown}`\n")
    with open(os.path.join(HERE, "probe-cases.jsonl"), "w", encoding="utf-8") as f:
        for cid, src, _intent, dump_only in CASES:
            if not dump_only:
                f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} battery cases, "
          f"{sum(1 for _,_,_,d in CASES if not d)} probe-eligible cases")


if __name__ == "__main__":
    main()
