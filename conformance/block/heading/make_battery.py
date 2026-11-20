#!/usr/bin/env python3
# Generate the Heading differential battery. One case per line of battery.jsonl,
# each {"id","source"}; sources are literal wikitext with \n line breaks.
import json

cases = []

def add(cid, source):
    cases.append({"id": cid, "source": source})

# All six + line prefixes, single heading per document.
add("h01-plus1", "+ Level one")
add("h02-plus2", "++ Level two")
add("h03-plus3", "+++ Level three")
add("h04-plus4", "++++ Level four")
add("h05-plus5", "+++++ Level five")
add("h06-plus6", "++++++ Level six")

# Level skips, repeats, descents and blank-line separations.
add("h07-skips", "+ One\n+++ Three\n++++++ Six")
add("h08-repeats", "++ A\n++ B\n++ C")
add("h09-descent", "++++++ Six\n++++ Five\n+++ Three\n++ Two\n+ One")
add("h10-mixed-blanks", "+ A\n\n++ B\n\n\n+++ C")

# Heading text carrying inline markup and links.
add("h11-em", "+ My //header//")
add("h12-bold", "++ Bold **text** here")
add("h13-underline", "+++ Under __line__")
add("h14-raw", "++++ Inline @@raw@@ here")
add("h15-size", "+++++ [[size 20%]]this one has an inline block in it[[/size]]")
add("h16-external-link", "+ See [[http://example.com|the site]]")
add("h17-internal-link", "++ See [[page-name]]")
add("h18-anchor", "+++ [[a name=\"x\"]]anchor[[/a]]")
add("h19-entities", "+ A & B < C > D \"quote\" 'apos'")
add("h20-leading-double-space", "+  double space after prefix")

# Repeated heading text, anchor-id sequencing and TOC placement.
add("h21-same-text", "+ Same\n+ Same\n+ Same")
add("h22-same-diff-level", "+ Same\n++ Same\n+++ Same")
add("h23-seven-headings", "+ a\n+ b\n+ c\n+ d\n+ e\n+ f\n+ g")
add("h24-interleaved", "+ A\npara\n++ B\npara\n+ C")
add("h25-toc-before", "[[toc]]\n\n+ A\n++ B\n+++ C")
add("h26-toc-after", "+ A\n++ B\n\n[[toc]]")
add("h27-two-tocs", "[[toc]]\n+ A\n[[toc]]\n++ B")

# The no-toc *-suffixed heading form.
add("h28-notoc1", "+* no toc one")
add("h29-notoc2", "++* no toc two")
add("h30-notoc6", "++++++* no toc six")
add("h31-notoc-mixed", "+ A\n+* B\n++ C\n++* D\n+++ E")
add("h32-notoc-with-toc", "[[toc]]\n+ A\n++* skip\n++ B")
add("h33-notoc-repeat", "+* Same\n++* Same")

# Malformed forms and near-misses.
add("h34-nospace", "+No space")
add("h35-seven", "+++++++ seven")
add("h36-eight", "++++++++ eight")
add("h37-leading-space", " + Leading space")
add("h38-tab", "+\tTab after plus")
add("h39-only-plus", "+")
add("h40-plus-space-only", "+ ")
add("h41-trailing-spaces", "+ trailing  ")
add("h42-plus-in-para", "text + plus in middle")
add("h43-plus-after-para", "para\n+ Heading\nmore")
add("h53-notoc-seven", "+++++++* seven notoc")
add("h55-double-plus-space", "++  two spaces after prefix")

# Adjacent-block shapes and barriers.
add("h44-adjacent-div", "[[div]]\ninside\n[[/div]]\n+ After div")
add("h45-heading-then-div", "+ Head\n[[div]]\nd\n[[/div]]")
add("h46-quote", "> quote\n+ Head")
add("h47-list", "* list\n+ Head")
add("h48-barrier-div", "[[div]]\n+ Head[[/div]] tail\n\n++ J")
add("h49-comment-line", "[!--x--]+ Head\n[!--a--][!--b--]++ Sub")
add("h50-raw-shield", "@@+ not a heading@@\n+ real heading")
add("h51-unicode", "+ Héading 中文 🎉")
add("h52-empty-body", "++    ")
add("h54-toc-raw-pin", "[[toc]]\n\n[[div]]\n+ Head[[/div]] tail\n\n++ J")

with open("battery.jsonl", "w", encoding="utf-8") as fh:
    for case in cases:
        fh.write(json.dumps(case, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cases")
