#!/usr/bin/env python3
"""Build the R2-contain Div battery and its live-probe subset.

Sources are LF-only with trailing newlines stripped (Wikidot normalizes them
on save). Run from this directory. Writes battery.jsonl (>=40 cases) and
probe-cases.jsonl (the subset that pins cannot settle on its own).
"""
import json

cases = []


def add(cid, source, tags=None, probe=False):
    rec = {"id": cid, "source": source}
    if tags is not None:
        rec["tags"] = tags
    cases.append((rec, probe))


# --- basic block forms -------------------------------------------------
add("basic", "[[div]]\nhello\n[[/div]]", probe=True)
add("basic-uppercase", "[[DIV]]\nhello\n[[/DIV]]", probe=True)
add("basic-indented", "  [[div]]\nhello\n[[/div]]")
add("basic-trailing-blank", "[[div]]\nhello\n\n[[/div]]")
add("basic-two-paras", "[[div]]\nA\n\nB\n[[/div]]", probe=True)
add("basic-heading", "[[div]]\n+ Head\ntext\n[[/div]]")

# --- attributes: class, id, style, role, type, data-*, unknown, quoting --
add("attr-class", '[[div class="card"]]\nBody\n[[/div]]')
add("attr-id", '[[div id="panel"]]\nBody\n[[/div]]', probe=True)
add("attr-id-prefixed", '[[div id="u-panel"]]\nBody\n[[/div]]', probe=True)
add("attr-id-space", '[[div id=" "]]\nx\n[[/div]]', probe=True)
add("attr-style", '[[div style="color: red"]]\nBody\n[[/div]]')
add("attr-style-two", '[[div style="color: red; background: blue"]]\nBody\n[[/div]]')
add("attr-role-type", '[[div role="note" type="tip"]]\nBody\n[[/div]]')
add("attr-data", '[[div data-foo="one" data-Bar="two"]]\nBody\n[[/div]]')
add("attr-data-empty-suffix", '[[div data-="v"]]\nT\n[[/div]]', probe=True)
add("attr-unknown", '[[div foo="baz" title="tip" lang="en"]]\nBody\n[[/div]]')
add("attr-allowlist", '[[div class="card" id="panel" style="color: red" role="note" type="t" title="tip" lang="en" aria-label="label" data-Foo="one" data-bar="two" foo="baz"]]\nBody\n[[/div]]', probe=True)
add("attr-allowlist-mixed", '[[div CLASS="upper" ID="upper" TYPE="u" DATA-Mixed="three" data-Mixed="four"]]\nBody\n[[/div]]', probe=True)
add("attr-single-quote", "[[div class='foo']]\nhello\n[[/div]]", probe=True)
add("attr-unquoted", "[[div class=foo]]\nhello\n[[/div]]", probe=True)
add("attr-dupe-data", '[[div data-Mixed="three" data-mixed="four"]]\nBody\n[[/div]]')
add("attr-class-space", '[[div class="a  b"]]\nx\n[[/div]]', probe=True)
add("attr-empty-value", '[[div class=""]]\nx\n[[/div]]')
add("attr-style-hidden-display", '[[div style="display:none"]]\nhello\n[[/div]]', probe=True)
add("attr-style-hidden-vis", '[[div style="visibility:hidden"]]\nhello\n[[/div]]', probe=True)
add("attr-style-hidden-mixed", '[[div style="display: none; color: red"]]\nhello\n[[/div]]', probe=True)
add("attr-style-hidden-space", '[[div style="display : none"]]\nhello\n[[/div]]')

# --- empty bodies ------------------------------------------------------
add("empty-plain", "[[div]]\n[[/div]]\nB", probe=True)
add("empty-attr", '[[div class="k"]]\n[[/div]]\nB', probe=True)
add("empty-whitespace", "[[div]]\n   \n[[/div]]\nB")
add("empty-at-eof", "[[div]]\n[[/div]]")

# --- unterminated and stray closers ------------------------------------
add("unterminated", "[[div]]\nhello", probe=True)
add("unterminated-attr", '[[div class="k"]]\nhello')
add("stray", "hello\n[[/div]]", probe=True)
add("stray-only", "[[/div]]")
add("stray-two", "[[/div]]\n[[/div]]\nA")
add("closer-midline", "A [[/div]] B")

# --- closer discipline -------------------------------------------------
add("closer-first", "[[div]]\nA\n[[/div]]\nB\n[[/div]]", probe=True)
add("closer-multi", "[[div]]\nA\n[[/div]]\nB\n[[/div]]\nC\n[[/div]]")
add("closer-same-line", "[[div]]\nA[[/div]]B\n[[/div]]")
add("closer-upper", "[[div]]\nA\n[[/DIV]]")

# --- inline content inside the block container -------------------------
add("inline-bold", "[[div]]\n**bold** and //ital//\n[[/div]]")
add("inline-span", "[[div]]\n[[span]]egg[[/span]]\n[[/div]]", probe=True)
add("inline-link", "[[div]]\n[http://example.com link]\n[[/div]]")
add("inline-code", "[[div]]\n{{code}}\n[[/div]]")
add("crossed-span", "[[div]]A1[[span]]B2[[/div]]C3[[/span]]D4", probe=True)
add("inline-content-scored", "[[div_]]\n**bold** [[span]]egg[[/span]]\n[[/div]]")

# --- nested divs -------------------------------------------------------
add("nested", "[[div]]\nA\n[[div]]\nB\n[[/div]]\nC\n[[/div]]", probe=True)
add("nested-deep", "[[div]]\n1\n[[div]]\n2\n[[div]]\n3\n[[/div]]\n2b\n[[/div]]\n1b\n[[/div]]")
add("nested-attr", '[[div class="outer"]]\nA\n[[div class="inner"]]\nB\n[[/div]]\n[[/div]]')
add("nested-scored", "[[div_]]\n1\n[[div_]]\n2\n[[/div]]\n3\n[[/div]]", probe=True)
add("nested-mixed", "[[div]]\nA\n[[div_]]\nB\n[[/div]]\nC\n[[/div]]")

# --- div inside collapsible / tabview ----------------------------------
add("div-in-collapsible", "[[collapsible]]\n[[div]]\nA\n[[/div]]\n[[/collapsible]]", probe=True)
add("div-in-tabview", "[[tabview]]\n[[tab T]]\n[[div]]\nA\n[[/div]]\n[[/tab]]\n[[/tabview]]", probe=True)
add("scored-in-collapsible", "[[collapsible]]\n[[div_]]\nA\n[[/div]]\n[[/collapsible]]")
add("nested-in-tab", "[[tabview]]\n[[tab T]]\n[[div]]\nA\n[[div]]\nB\n[[/div]]\n[[/div]]\n[[/tab]]\n[[/tabview]]")

# --- malformed forms ---------------------------------------------------
add("malformed-division", "[[division]]\nA\n[[/division]]", probe=True)
add("malformed-divx", "[[divx]]\nA\n[[/divx]]")
add("malformed-open-bracket", "[[div\nA\n[[/div]]")
add("malformed-close-bracket", "[[div]]\nA\n[[/div]]]")
add("malformed-extra-bracket", "[[[div]]]\nA\n[[[/div]]]")
add("malformed-star", "[[div*]]\nA\n[[/div]]")
add("malformed-empty-args", "[[div ]]\nA\n[[/div]]")

# --- standalone [[div_]] opener (N1 residual) --------------------------
add("score-basic", "[[div_]]\nhello\n[[/div]]", probe=True)
add("score-attr", '[[div_ class="strip"]]\nhello\n[[/div]]', probe=True)
add("score-attrs-full", '[[div_ class="strip" title="tip" role="note" data-x="y"]]\nBody\n[[/div]]', probe=True)
add("score-attrs-id", '[[div_ id="q" role="note" data-z="1"]]\nx\n[[/div]]', probe=True)
add("score-empty", "[[div_]]\n[[/div]]\nB", probe=True)
add("score-attr-empty", '[[div_ class="k"]]\n[[/div]]\nB', probe=True)
add("score-inline", "[[div_]]Banana[[/div]]", probe=True)
add("score-two-lines", "[[div_]]\napple\nbanana\n[[/div]]", probe=True)
add("score-unterminated", "[[div_]]\nhello")
add("score-stray", "[[div_]]\nhello\n[[/div]]\n[[/div]]")
add("score-uppercase", "[[DIV_]]\nhello\n[[/DIV]]")
add("score-style-hidden", '[[div_ style="display:none"]]\nhello\n[[/div]]')

with open("battery.jsonl", "w") as f:
    for rec, _ in cases:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

probe_cases = [rec for rec, p in cases if p]
with open("probe-cases.jsonl", "w") as f:
    for rec in probe_cases:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"battery: {len(cases)} cases; probe subset: {len(probe_cases)} cases")
