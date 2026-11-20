#!/usr/bin/env python3
"""Generate the R2 Code differential battery as JSONL ({"id","source"} per line).

The battery covers the shapes named in BRIEF-R2-CODE.md step 2. Sources are
literal wikitext; \r and \n in the Python strings become real CR/LF bytes in
the JSONL (json.dumps escapes them on the wire and the harness decodes them).
"""
import json

cases = []


def add(cid, source):
    cases.append({"id": cid, "source": source})


# --- basic blocks -----------------------------------------------------------
add("basic-line", "BEFORE\n[[code]]\nalpha\nbeta\n[[/code]]\nAFTER")
add("basic-inline", "[[code]]alpha[[/code]]")
add("basic-no-trailing-nl", "x\n[[code]]\nalpha\n[[/code]]")
add("basic-leading-text", "pre [[code]]x[[/code]]\npost")
add("basic-two-blocks", "[[code]]a[[/code]]\n[[code]]b[[/code]]")
add("basic-in-paragraph", "para before [[code]]mid[[/code]] para after")

# --- empty and whitespace-only bodies --------------------------------------
add("empty", "[[code]][[/code]]")
add("empty-lines", "[[code]]\n[[/code]]")
add("empty-two-lines", "[[code]]\n\n[[/code]]")
add("ws-body-spaces", "[[code]]   [[/code]]")
add("ws-body-tabs", "[[code]]\t\t[[/code]]")
add("ws-body-blank-lines", "[[code]]\n \n \n[[/code]]")

# --- tabs and blank-line runs inside the body -------------------------------
add("body-tab", "[[code]]\n\tx\t\n[[/code]]")
add("body-tab-middle", "[[code]]\na\tb\n[[/code]]")
add("body-blank-run", "[[code]]\na\n\n\n\nb\n[[/code]]")
add("body-leading-blanks", "[[code]]\n\n\nx\n[[/code]]")
add("body-trailing-blanks", "[[code]]\nx\n\n\n[[/code]]")
add("body-spaces-line", "[[code]]\nx\n   \ny\n[[/code]]")
add("body-mid-trailing-spaces", "[[code]]\nx \ny \n[[/code]]")
add("body-leading-space-first", "[[code]]  indented\nnext\n[[/code]]")
add("body-nbsp", "[[code]]\n\u00a0x\u00a0\n[[/code]]")
add("body-ideographic", "[[code]]\n\u3000x\u3000\n[[/code]]")

# --- nested openers / stray closers / unterminated --------------------------
add("nested-openers", "[[code]]\n[[code]]\ninner\n[[/code]]\nouter\n[[/code]]")
add("nested-one-line", "[[code]]a[[code]]b[[/code]]c[[/code]]")
add("stray-closer", "[[/code]]")
add("stray-closer-after-text", "before\n[[/code]]\nafter")
add("stray-closer-before", "[[/code]]\n[[code]]x[[/code]]")
add("unterminated", "[[code]]\nnever closed")
add("unterminated-inline", "[[code]]abc")
add("unterminated-then-other", "[[code]]\nx\n[[div]]y[[/div]]")
add("closer-suffixed", "[[code]]a[[/code]] x")
add("closer-trailing-space", "[[code]]a[[/code]] \nNEXT")
add("closer-suffix-newline", "[[code]]\na\n[[/code]]\nNEXT")

# --- argument forms ---------------------------------------------------------
add("arg-type-python", "[[code type=\"python\"]]\nimport antigravity\n[[/code]]")
add("arg-type-PYTHON", "[[code type=\"PYTHON\"]]\nimport antigravity\n[[/code]]")
add("arg-type-css-inline", "[[code type=\"css\"]]a { display: none; }[[/code]]")
add("arg-type-unknown", "[[code type=\"apache\"]]\nSELECT 1;\n[[/code]]")
add("arg-type-empty", "[[code type=\"\"]]x[[/code]]")
add("arg-name", "[[code name=\"Sample Heading\"]]\nbody\n[[/code]]")
add("arg-type-name", "[[code name=\"a\" type=\"java\"]]\nclass A {}\n[[/code]]")
add("arg-unknown", "[[code foo=\"bar\"]]\nbody\n[[/code]]")
add("arg-unquoted", "[[code type=css]]x[[/code]]")
add("arg-half-quote-1", "[[code type=\"css]]x[[/code]]")
add("arg-half-quote-2", "[[code type=css\"]]x[[/code]]")
add("arg-spaced-name", "[[ code ]]\nNESTED\n[[code]]\n[[/code]]")
add("arg-tab-after", "[[code\ttype=\"css\"]]x[[/code]]")
add("arg-multi-space", "[[code   type=\"css\"]]x[[/code]]")
add("arg-two-attrs", "[[code type=\"python\" name=\"n\"]]x[[/code]]")
add("arg-newline-after", "[[code\ntype=\"css\"]]x[[/code]]")

# --- literal body content ---------------------------------------------------
add("body-wikitext", "[[code]]\n[[div]]\nnot a div\n[[/div]]\n**not bold**\n[[/code]]")
add("body-brackets", "[[code]]\n[[foo]] [[bar baz]] [[]] [[/code]]\n[[/code]]")
add("body-quotes", "[[code]]\n\"double\" 'single' &amp; & < >\n[[/code]]")
add("body-html", "[[code]]\n<b>bold</b> <script>alert(1)</script>\n[[/code]]")
add("body-entities", "[[code]]\n&amp; &lt; &gt; &quot;\n[[/code]]")
add("body-code-closer-literal", "[[code]]\n[[/code]] literal\n[[/code]]")

# --- line placement / multiple blocks --------------------------------------
add("line-start-opener", "[[code]]x[[/code]]")
add("mid-paragraph", "alpha [[code]]beta[[/code]] gamma")
add("after-heading", "= H =\n[[code]]x[[/code]]")
add("three-blocks", "[[code]]a[[/code]]\n[[code]]b[[/code]]\n[[code]]c[[/code]]")
add("block-then-paragraph", "[[code]]x[[/code]]\nparagraph after")

# --- CRLF -------------------------------------------------------------------
add("crlf-basic", "[[code]]\r\nalpha\r\nbeta\r\n[[/code]]\r\n")
add("crlf-empty", "[[code]]\r\n[[/code]]\r\n")
add("crlf-nested", "[[code]]\r\n[[code]]x[[/code]]\r\n[[/code]]")
add("crlf-args", "[[code type=\"python\"]]\r\nx=1\r\n[[/code]]")
add("lone-cr-body", "[[code]]\ra\rb\r[[/code]]")

# --- mixed frame interactions -----------------------------------------------
add("frame-tab-newlines", "[[code]]\nline1\t\n\n\nline2\n[[/code]]")
add("frame-ueue", "[[code]]\n\u00fc\u00fc\n[[/code]]")
add("frame-quoted", ">> [[code]]\n>> QUOTED_LITERAL\n>> [[/code]]")

with open("/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh/conformance-refphp/code/battery.jsonl", "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
print(len(cases), "cases")
