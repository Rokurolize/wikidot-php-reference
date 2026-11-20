#!/usr/bin/env python3
"""Generate battery.jsonl for the R2-notes Bibliography rule.

Every case is a WHOLE DOCUMENT. Sources are kept close to live Wikidot shapes
seen in the ftml corpus pins (test/misc/bibliography*, test/bibliography/*),
plus systematic variations of the matching/joining mechanism under test.
"""
import json

CASES = []


def add(cid, source, note=""):
    CASES.append({"id": cid, "source": source, "_note": note})


# --- canonical forms and citation direction ---------------------------------
add("bib01-canonical-two", (
    "The first pulsar was observed by J. Bell and A. Hewish ((bibcite bell)).\n"
    "Another reference [see ((bibcite guy))].\n\n"
    "[[bibliography]]\n"
    ": bell : Bell, J.; Hewish, A. //Observation of a Rapidly Pulsating Radio Source.// Nature 217, 709, 1968.\n"
    ": guy : Guy, R. K. //Modular Difference Sets.// Springer, 1994.\n"
    "[[/bibliography]]\n"
), "two entries, citations before the block (forward references)")

add("bib02-cite-after", (
    "[[bibliography]]\n"
    ": alpha : Alpha reference.\n"
    ": beta : Beta reference.\n"
    "[[/bibliography]]\n\n"
    "See ((bibcite alpha)) and ((bibcite beta)).\n"
), "citations after the block (backward references)")

add("bib03-cite-both-sides", (
    "Before ((bibcite a)).\n\n"
    "[[bibliography]]\n: a : Entry A.\n[[/bibliography]]\n\n"
    "After ((bibcite a)).\n"
), "same label cited before and after the block")

add("bib04-duplicate-label", (
    "Cite ((bibcite bell)).\n\n"
    "[[bibliography]]\n"
    ": bell : First bell entry.\n"
    ": bell : Second bell entry.\n"
    ": guy : Guy entry.\n"
    "[[/bibliography]]\n"
), "duplicate label: live numbers 1.,2.,2. and cites resolve to last")

add("bib05-empty-block", (
    "Cite ((bibcite bell)).\n\n"
    "[[bibliography]]\n[[/bibliography]]\n"
), "empty body still emits the wrapper and title")

add("bib06-body-only-no-cite", (
    "[[bibliography]]\n"
    ": a : Entry A text.\n"
    ": b : Entry B text.\n"
    "[[/bibliography]]\n"
), "no citations at all")

# --- ordering ---------------------------------------------------------------
add("bib07-alphabetical-order", (
    "((bibcite zeta)) ((bibcite alpha)) ((bibcite mu))\n\n"
    "[[bibliography]]\n"
    ": alpha : Alpha.\n"
    ": mu : Mu.\n"
    ": zeta : Zeta.\n"
    "[[/bibliography]]\n"
), "entries in alphabetical order, cited out of order")

add("bib08-citation-order", (
    "((bibcite c)) ((bibcite a)) ((bibcite b))\n\n"
    "[[bibliography]]\n"
    ": c : See C.\n"
    ": a : See A.\n"
    ": b : See B.\n"
    "[[/bibliography]]\n"
), "definition order is citation order")

add("bib09-definition-order", (
    "[[bibliography]]\n"
    ": z : Zed.\n"
    ": y : Why.\n"
    ": x : Ex.\n"
    "[[/bibliography]]\n\n"
    "((bibcite x)) ((bibcite y)) ((bibcite z))\n"
), "reverse-alphabetical definition order")

# --- multiple blocks --------------------------------------------------------
add("bib10-two-blocks", (
    "Cite ((bibcite a)) and ((bibcite b)).\n\n"
    "[[bibliography]]\n: a : Entry A.\n[[/bibliography]]\n\n"
    "Middle text.\n\n"
    "[[bibliography]]\n: b : Entry B.\n[[/bibliography]]\n"
), "second block stays literal, its label undefined")

add("bib11-first-empty-second-full", (
    "[[bibliography]]\n[[/bibliography]]\n\n"
    "[[bibliography]]\n: a : Entry A.\n[[/bibliography]]\n"
), "first empty block consumes the single match")

add("bib12-three-blocks", (
    "[[bibliography]]\n: a : A.\n[[/bibliography]]\n"
    "[[bibliography]]\n: b : B.\n[[/bibliography]]\n"
    "[[bibliography]]\n: c : C.\n[[/bibliography]]\n"
), "only first of three forms")

# --- title options ----------------------------------------------------------
add("bib13-title-double-quoted", (
    "[[bibliography title=\"Works Cited\"]]\n: a : Entry A.\n[[/bibliography]]\n"
), "title option with double quotes")

add("bib14-title-single-quoted", (
    "[[bibliography title='Works']]\n: a : Entry A.\n[[/bibliography]]\n"
), "title option with single quotes")

add("bib15-title-empty", (
    "[[bibliography title=\"\"]]\n: a : Entry A.\n[[/bibliography]]\n"
), "explicit empty title suppresses the title div")

add("bib16-title-special-chars", (
    "[[bibliography title=\"<Works & Sources>\"]]\n: a : A & B\n[[/bibliography]]\n"
), "title HTML-escaped in the render")

add("bib17-hide-yes", (
    "[[bibliography hide=\"yes\"]]\n: key : value\n[[/bibliography]]\n"
), "live ignores hide; default title still shown")

add("bib18-hide-short-t", (
    "[[bibliography hide=\"t\"]]\n: k : V\n[[/bibliography]]\n"
), "live ignores hide=t")

add("bib19-unknown-args", (
    "[[bibliography class=\"probe\" stray v7arg=\"one\"]]\n: a : Entry A.\n[[/bibliography]]\n"
), "unknown arguments ignored for title")

add("bib20-title-and-hide", (
    "[[bibliography title=\"Works\" hide=\"true\"]]\n: a : A\n[[/bibliography]]\n"
), "title wins, hide ignored")

# --- unterminated / malformed matching --------------------------------------
add("bib21-unterminated", (
    "Before.\n\n"
    "[[bibliography]]\n"
    ": a : Entry A.\n"
), "no closer: opener and deflist stay literal")

add("bib22-unterminated-empty", (
    "[[bibliography]]\n"
), "bare opener stays literal")

add("bib23-name-case-uppercase", (
    "[[BIBLIOGRAPHY]]\n: a : A\n[[/BIBLIOGRAPHY]]\n"
), "uppercase name does not form; deflist parses")

add("bib24-name-case-title", (
    "[[Bibliography]]\n: a : A\n[[/Bibliography]]\n"
), "mixed-case name does not form")

add("bib25-closer-uppercase", (
    "[[bibliography]]\n: a : A\n[[/BIBLIOGRAPHY]]\n"
), "opener lower, closer uppercase: no match")

add("bib26-opener-leading-space", (
    "[[ bibliography]]\n: a : A\n[[/bibliography]]\n"
), "leading space inside opener brackets: no match")

add("bib27-opener-extra-close", (
    "[[bibliography]]]\n: a : A\n[[/bibliography]]\n"
), "extra ] in opener head: no match")

add("bib28-closer-trailing-spaces", (
    "[[bibliography]]\n: a : A\n[[/bibliography]]   \n\nafter\n"
), "trailing spaces after closer are allowed")

add("bib29-closer-trailing-tab", (
    "[[bibliography]]\n: a : A\n[[/bibliography]]\t\nafter\n"
), "trailing tab after closer: live accepts, fossil regex uses [ ]*")

add("bib30-closer-trailing-text", (
    "start-[[bibliography]]\n: a : A\n[[/bibliography]]-middle\n"
), "text before opener and after closer: neither forms")

add("bib31-nested-bibliography", (
    "[[bibliography]]\n[[bibliography]]\nnested\n[[/bibliography]]\n[[/bibliography]]\n"
), "nested opener is literal inside the joined body")

add("bib32-overlap-bold-closer", (
    "[[bibliography]]\nouter [[bold]]inner\n[[/bibliography]][[/bold]]\n"
), "closer not at EOL: whole thing literal")

# --- body joining and nested markup -----------------------------------------
add("bib33-inline-strong-em", (
    "((bibcite k))\n\n[[bibliography]]\n: k : aa **bold** and //italic// text\n[[/bibliography]]\n"
), "unanchored inline markup forms in the joined body")

add("bib34-inline-size-span", (
    "((bibcite k1)) ((bibcite k2))\n\n[[bibliography]]\n"
    ": k1 : aa [[size 150%]]bb[[/size]] cc\n"
    ": k2 : aa [[span]]bb[[/span]] cc\n"
    "[[/bibliography]]\n"
), "size/span are AfterJoinUnanchored")

add("bib35-line-anchored-list", (
    "[[bibliography]]\n: a : A\n* item one\n* item two\n[[/bibliography]]\n"
), "list lines cannot form in the joined body; become residual")

add("bib36-line-anchored-heading", (
    "[[bibliography]]\n: a : A\n+ Heading\n[[/bibliography]]\n"
), "heading line cannot form in joined body")

add("bib37-bibcite-in-value", (
    "[[bibliography]]\n: alpha : ((bibcite alpha)) self\n[[/bibliography]]\n((bibcite alpha))\n"
), "self citation inside the joined value (Bibcite runs after join)")

add("bib38-definition-separators", (
    "((bibcite a)) ((bibcite b)) ((bibcite c)) ((bibcite d)) ((bibcite e)) ((bibcite g)) ((bibcite h)) ((bibcite i))\n\n"
    "[[bibliography]]\n"
    ": a: Alpha.\n: b :Bravo.\n: c:  Charlie.\n: d :\tDelta.\n: i  : India.\n: e :\n\n: g: Golf.\n: h :Hotel.\n"
    "[[/bibliography]]\n"
), "separator spacing and tabs around the label colon")

add("bib39-label-charset", (
    "((bibcite smith2020)) ((bibcite smith-2020)) ((bibcite alpha_2)) ((bibcite 2b))\n\n"
    "[[bibliography]]\n"
    ": smith2020 : Smith 2020.\n"
    ": smith-2020 : Never registered.\n"
    ": alpha_2 : Never registered.\n"
    ": 2b : Or not to be.\n"
    "[[/bibliography]]\n"
), "label charset: only [a-z0-9]+ registers")

add("bib40-tab-prefix-label", (
    "((bibcite alpha)) ((bibcite bell))\n\n[[bibliography]]\n"
    ": alpha : Alpha text.\n"
    ":\tbell : Bell text.\n"
    "[[/bibliography]]\n"
), "tab immediately after first colon")

add("bib41-next-line-value", (
    "((bibcite a)) ((bibcite b)) ((bibcite c)) ((bibcite d))\n\n"
    "[[bibliography]]\n"
    ": a:\nValue on next line.\n"
    ": b:\n"
    ": c : See text.\n"
    ": d:\n+ Not a heading.\n"
    "[[/bibliography]]\n"
), "value starting on the following line after join")

add("bib42-invalid-line-residual", (
    "((bibcite alpha)) ((bibcite omega))\n\n"
    "[[bibliography]]\n"
    ": bad-first : Bad first.\n"
    ": alpha : Alpha text.\n"
    ": bad-label : **bold** bad.\n"
    ": omega : Omega text.\n"
    "trailing prose\n"
    "[[/bibliography]]\n"
), "non-definition line becomes residual inside the wrapper")

add("bib43-label-only-crossing", (
    "((bibcite alpha)) ((bibcite bell)) ((bibcite omega))\n\n"
    "[[bibliography]]\n"
    ": alpha : Alpha text.\n"
    ": bell\n"
    ": omega : Omega text.\n"
    ": solo\n"
    "[[/bibliography]]\n"
), "label-only lines crossing into the next definition")

add("bib44-whitespace-body", (
    "[[bibliography]]\n   \n\t\n[[/bibliography]]\n"
), "whitespace-only body")

# --- adjacency with the footnote family and other block constructs ----------
add("bib45-footnote-then-bibliography", (
    "A claim[[footnote]]with a note[[/footnote]].\n\n"
    "[[bibliography]]\n: a : A\n[[/bibliography]]\n"
), "footnote before the bibliography in one document")

add("bib46-bibliography-then-footnote", (
    "[[bibliography]]\n: a : A\n[[/bibliography]]\n\n"
    "A claim[[footnote]]with a note[[/footnote]].\n"
), "footnote after the bibliography in one document")

add("bib47-bibliography-inside-footnote", (
    "[[footnote]]\n[[bibliography]]\n: a : A\n[[/bibliography]]\n[[/footnote]]\nafter\n"
), "bibliography does not form inside a footnote body")

add("bib48-footnote-opened-in-bib-body", (
    "[[bibliography]]\n: a : A\n[[footnote]]\n: b : B\n[[/bibliography]]\n[[/footnote]]\nafter\n"
), "footnote opened inside bibliography body keeps tail inside")

add("bib49-bibliography-inside-list", (
    "[[ul]]\n[[li]]\n[[bibliography]]\n: a : A\n[[/bibliography]]\n[[/li]]\n[[/ul]]\nafter\n"
), "bibliography forms inside a list item")

add("bib50-item-inside-table", (
    "[[bibliography]]\n: a : A\n"
    "[[table]]\n[[row]]\n[[cell]]\n: b : B\n[[/cell]]\n[[/row]]\n[[/table]]\n"
    ": c : C\n[[/bibliography]]\nafter\n"
), "Bibitem ran before join so nested cell definition becomes an entry")

add("bib51-iftags-kept", (
    "[[iftags -zzz]]\n[[bibliography]]\n: a : A\n[[/bibliography]]\n[[/iftags]]\nafter\n"
), "iftags gate keeps the bibliography")

add("bib52-iftags-closer-inside", (
    "[[bibliography]]\n: key : a[[iftags -zzz]]b\n[[/bibliography]]\nc[[/iftags]]d\n"
), "iftags gate crosses the bibliography closer")

add("bib53-tabview-residue", (
    "[[bibliography]]\n: key : Value\n"
    "[[tabview]]\n[[tab One]]\nBody one\n[[/tab]]\n[[/tabview]]\n[[/bibliography]]\n"
), "tabview is line-anchored and cannot form in the joined body")

add("bib54-trailing-paragraph", (
    "[[bibliography]]\n: key1 : Some reference\n\n"
    "after para\n[[/bibliography]]\n"
), "trailing paragraph inside the body becomes residual")

add("bib55-dashes-typography", (
    "((bibcite key1))\n\n[[bibliography]]\n: key1 : aa -- bb --- cc ... dd\n[[/bibliography]]\n"
), "typography pass runs after join, unanchored")

add("bib56-no-bibliography", (
    "Just a plain document with ((bibcite ghost)) and no bibliography block.\n"
), "control: undefined cite with no block at all")

# emit (drop the private note key from the actual battery)
out = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh-r2notes/conformance-refphp/notes/bibliography/battery.jsonl"
notes = [{"id": c["id"], "note": c["_note"]} for c in CASES]
with open(out, "w", encoding="utf-8") as fh:
    for case in CASES:
        case.pop("_note")
        fh.write(json.dumps(case, ensure_ascii=False) + "\n")

with open(out + ".notes.json", "w", encoding="utf-8") as fh:
    json.dump(notes, fh, indent=1, ensure_ascii=False)

print(f"wrote {len(CASES)} cases")
