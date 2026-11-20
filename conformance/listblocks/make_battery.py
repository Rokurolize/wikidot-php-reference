#!/usr/bin/env python3
import json
from pathlib import Path

cases = [
    # Family 1: Basic [[ul]] and [[ol]] with [[li]]...[[/li]]
    ("lb01", "[[ul]]\n[[li]]Apple[[/li]]\n[[li]]Banana[[/li]]\n[[/ul]]"),
    ("lb02", "[[ol]]\n[[li]]First[[/li]]\n[[li]]Second[[/li]]\n[[/ol]]"),
    ("lb03", "[[ul]]\n[[li]]Apple[[/li]]\n[[li]]Banana[[/li]]\n[[/ul]]\n[[ol]]\n[[li]]First[[/li]]\n[[li]]Second[[/li]]\n[[/ol]]"),
    ("lb04", "[[ul]][[li]]Inline[[/li]][[li]]list[[/li]][[/ul]]"),
    ("lb05", "[[ol]][[li]]One[[/li]][[li]]Two[[/li]][[/ol]]"),
    ("lb06", "[[ul]]\n[[li]] Indented [[/li]]\n[[li]]   spaced   [[/li]]\n[[/ul]]"),
    ("lb07", "[[UL]]\n[[LI]]Case[[/LI]]\n[[/UL]]"),
    ("lb08", "[[ul]]\n[[li]]\nALPHA\n[[/li]]\n[[li]]\nBETA\n[[/li]]\n[[/ul]]"),
    ("lb09", "[[ul]]\n[[li]]line1\nline2[[/li]]\n[[/ul]]"),
    ("lb10", "[[ul]]\n[[li]]u[[/li]]\n[[/ul]]\n[[ul]]\n[[li]]u[[/li]]\n[[/ul]]"),

    # Family 2: Nesting [[ul]] / [[ol]] / [[li]]
    ("lb11", "[[ul]]\n[[li]] Indented [[/li]]\n[[ol]]\n[[li]] and [[/li]]\n[[li]] nested [[/li]]\n[[/ol]]\n[[li]] list [[/li]]\n[[/ul]]"),
    ("lb12", "[[ol]]\n[[ul]]\n[[li]]-[[/li]]\n[[/ul]]\n[[/ol]]"),
    ("lb13", "[[ul]]\n[[ul]]\n[[li]]deep[[/li]]\n[[/ul]]\n[[/ul]]"),
    ("lb14", "[[ul]]\n[[li]]outer\n[[ol]]\n[[li]]inner[[/li]]\n[[/ol]]\n[[/li]]\n[[/ul]]"),
    ("lb15", "[[ol]]\n[[li]]1\n[[ul]]\n[[li]]a[[/li]]\n[[li]]b[[/li]]\n[[/ul]]\n[[/li]]\n[[li]]2[[/li]]\n[[/ol]]"),
    ("lb16", "[[ul]]\n[[li]]L1[[/li]]\n[[ul]]\n[[li]]L2[[/li]]\n[[ol]]\n[[li]]L3[[/li]]\n[[/ol]]\n[[/ul]]\n[[/ul]]"),

    # Family 3: Attributes on [[ul]], [[ol]], [[li]]
    ("lb17", "[[ul id=\"my-list\" class=\"a\" style=\"color: red;\" role=\"list\" type=\"disc\" data-x=\"1\" title=\"ignored\" hidden=\"yes\"]]\n[[li id=\"item-1\" class=\"b\" style=\"color: blue;\" data-Y=\"2\" value=\"9\"]]One[[/li]]\n[[/ul]]"),
    ("lb18", "[[ol id=\"num-list\" class=\"n\" style=\"color: green;\" type=\"A\" start=\"5\" reversed=\"reversed\"]]\n[[li]]Item[[/li]]\n[[/ol]]"),
    ("lb19", "[[ul class=\"c\" id=\"i\" style=\"s\"]]\n[[li style=\"ls\" id=\"li\" class=\"lc\"]]ordered-attrs[[/li]]\n[[/ul]]"),
    ("lb20", "[[ul data-z=\"1\" data-a=\"2\" DATA-UPPER=\"3\" data-Mixed=\"4\"]]\n[[li data-k=\"v\" CLASS=\"upper\"]]data-attrs[[/li]]\n[[/ul]]"),
    ("lb21", "[[ul id=\"\" class=\"\" data-empty=\"\"]]\n[[li id=\"u-already\" class=\"a  b\"]]norm[[/li]]\n[[/ul]]"),

    # Family 4: Interaction with line-led lists (* and #)
    ("lb22", "[[ul]]\n* one\n* two\n[[/ul]]"),
    ("lb23", "[[ol]]\n* one\n* two\n[[/ol]]"),
    ("lb24", "[[ul]]\n* one\n* two\n[[/ul]]\n[[ol]]\n* bullet\n# num\n[[/ol]]"),
    ("lb25", "[[ul]]\n* a\n* b\n# c\n# d\n[[/ul]]"),
    ("lb26", "[[ul]]\n[[li]]\n* one\n* two\n[[/li]]\n[[/ul]]"),
    ("lb27", "[[ul]]\n[[li]]header\n* sub1\n* sub2\n[[/li]]\n[[/ul]]"),
    ("lb28", "* line1\n* line2\n\n[[ul]]\n[[li]]block1[[/li]]\n[[li]]block2[[/li]]\n[[/ul]]"),

    # Family 5: Interaction with simple and advanced tables (R2-TABLE sightings y03, y04, y09 + [[li]] variants)
    ("lb29", "||[[ul]]\n* one\n* two\n[[/ul]] ||\n|| after ||\nx"),
    ("lb30", "||[[ol]]\n* one\n* two\n[[/ol]] ||\n|| after ||\nx"),
    ("lb31", "[[table]][[row]][[cell]][[ul]]\n* one\n* two\n[[/ul]][[/cell]][[/row]][[/table]]\nx"),
    ("lb32", "||[[ul]]\n[[li]]one[[/li]]\n[[li]]two[[/li]]\n[[/ul]] ||\n|| after ||\nx"),
    ("lb33", "[[table]][[row]][[cell]][[ul]]\n[[li]]one[[/li]]\n[[li]]two[[/li]]\n[[/ul]][[/cell]][[/row]][[/table]]\nx"),

    # Family 6: Interaction with containers and inline formatting (R2-CONTAIN, R2-INLINE3 sup38, tighten69)
    ("lb34", "[[div]]\n[[ul]]\n[[li]]in-div[[/li]]\n[[/ul]]\n[[/div]]"),
    ("lb35", "[[note]]\n[[ul]]\n[[li]]u[[/li]]\n[[/ul]]\n[[/note]]"),
    ("lb36", "[[collapsible]]\n[[ul]]\n[[li]]u[[/li]]\n[[/ul]]\n[[/collapsible]]"),
    ("lb37", "[[ul]]\n[[li]]**bold** //italic// __under__ ^^sup^^[[/li]]\n[[li]][[[some-page|link]]] and [[a href=\"/x\"]]anchor[[/a]][[/li]]\n[[/ul]]"),
    ("lb38", "^^a\n* list\nb^^\nx"),
    ("lb39", "^^a\n[[ul]]\n[[li]]list[[/li]]\n[[/ul]]\nb^^\nx"),
    ("lb40", "^^a\n* list\nb^^\nx\n^^a\n[[ul]]\n[[li]]list[[/li]]\n[[/ul]]\nb^^\nx"),
    ("lb41", "a\n\n[[div]]x[[/div]]\n\nb"),

    # Family 7: Empty, degraded, scored, and malformed forms
    ("lb42", "[[ul]][[/ul]]\n[[ol]][[/ol]]\n[[ul]][[li]][[/li]][[/ul]]\nx"),
    ("lb43", "[[ul]]\nFoo\n[[/ul]]\n[[li]]\nBaz\n[[/li]]"),
    ("lb44", "[[ol]]\nBar\n[[/ol]]"),
    ("lb45", "[[ul_]]\n[[li]]Alpha[[/li]]\n[[li]]Beta[[/li]]\n[[/ul]]\n[[ol_]]\n[[li]]One[[/li]]\n[[/ol]]"),
    ("lb46", "[[ul_]]\n[[li_]]\nAlpha\n[[/li]]\n[[li_]]\nBeta\n[[/li]]\n[[/ul]]"),
    ("lb47", "[[ul ]]\n[[li]]a[[/li]]\n[[/ul]]\n[[ul]]\n[[li ]]b[[/li]]\n[[/ul]]\n[[ul]]\n[[li]]c[[/li ]]\n[[/ul ]]"),
    ("lb48", "[[ul]]\n[[li]]ab\n[[/ul]]"),
    ("lb49", "[[ul]]\n[[li]]unterminated"),
    ("lb50", "[[ul]]\n[[li]]fused[[/li]]]\n[[/ul]]]"),
]

out_path = Path(__file__).resolve().parent / "battery.jsonl"
with out_path.open("w", encoding="utf-8") as f:
    for cid, src in cases:
        f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
print(f"Wrote {len(cases)} cases to {out_path}")
