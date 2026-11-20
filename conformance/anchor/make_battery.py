#!/usr/bin/env python3
import json
from pathlib import Path

cases = [
    # Family 1: Named anchors [[# ...]]
    ("a01", "[[# strawberry]]"),
    ("a02", "[[# _lemon-lime.2%20]]"),
    ("a03", "[[#durian]]"),
    ("a04", "[[# ]]"),
    ("a05", "[[#  a]]"),
    ("a06", "[[#  a  ]]"),
    ("a07", "[[# apple banana]]"),
    ("a08", "[[# apple banana]]]"),
    ("a09", "[[# symbol$%_foo]]"),
    ("a10", "[[# name]]]"),
    ("a11", "[[[# a]]]\n[[[# a | L]]]"),
    ("a12", "[[# top]]\n[[a href=\"#top\"]]jump[[/a]]"),

    # Family 2: Basic [[a]]...[[/a]] and href classes
    ("a13", "[[a]]Test[[/a]]"),
    ("a14", "[[a]][[/a]]"),
    ("a15", "[[a href=\"some-page\"]]click[[/a]]"),
    ("a16", "[[a href=\"*some-page\"]]click[[/a]]"),
    ("a17", "[[a href=\"https://example.com\"]]click[[/a]]"),
    ("a18", "[[a href=\"*https://example.com\"]]click[[/a]]"),
    ("a19", "[[a href=\"*https://example.com\" target=\"_self\"]]click[[/a]]"),
    ("a20", "[[a href=\"#something\"]]click[[/a]]"),
    ("a21", "[[a href=\"*#something\"]]click[[/a]]"),
    ("a22", "[[a href=\"/local/path\"]]click[[/a]]"),
    ("a23", "[[a href=\"*/local/path\"]]click[[/a]]"),
    ("a24", "[[a href=\"mailto:user@example.com\"]]mail[[/a]]"),
    ("a25", "[[a href=\"ftp://files.example.com/pub\"]]ftp[[/a]]"),
    ("a26", "[[a href=\"javascript:alert(1)\"]]xss[[/a]]"),
    ("a27", "[[a href=\"JAVASCRIPT:alert(1)\"]]xss2[[/a]]"),
    ("a28", "[[a href=\"data:text/html,<b>x</b>\"]]data[[/a]]"),
    ("a29", "[[a href=\"HTTP://X/Y\"]]upper-http[[/a]]"),
    ("a30", "[[a href=\" http://x\"]]lead-sp[[/a]]\n[[a href=\"http://x \"]]trail-sp[[/a]]"),

    # Family 3: href encoding and special values
    ("a31", "[[a href=\"http://example.com/a b\"]]sp1[[/a]]\n[[a href=\"/a b\"]]sp2[[/a]]\n[[a href=\"#a b\"]]sp3[[/a]]"),
    ("a32", "[[a href=\"https://example.com/a b/日本語\"]]enc[[/a]]"),
    ("a33", "[[a href=\"a::b\"]]c1[[/a]]\n[[a href=\"a - b\"]]c2[[/a]]\n[[a href=\":\"]]c3[[/a]]\n[[a href=\"abc=\"]]c4[[/a]]"),
    ("a34", "[[a href=\"@@a@@\"]]r1[[/a]]\n[[a class=\"@@a@@\" href=\"/x\"]]r2[[/a]]\n[[a href=\"/x@@a@@\"]]r3[[/a]]"),
    ("a35", "[[a href=\"*https://example.com\"]]star-ext[[/a]]\n[[a href=\"*some-page\"]]star-slug[[/a]]\n[[a href=\"*https://example.com\" target=\"_self\"]]star-override[[/a]]"),

    # Family 4: Attribute allowlist, ordering, isolation, and normalization
    ("a36", "[[a href=\"/x\" id=\"i\" class=\"c\" style=\"s\" role=\"r\" type=\"t\" data-x=\"d\" target=\"_blank\"]]y[[/a]]"),
    ("a37", "[[a href=\"/x\" style=\"s\" class=\"c\" id=\"i\"]]y[[/a]]"),
    ("a38", "[[a href=\"/x\" data-z=\"1\" data-a=\"2\" data-m=\"3\"]]y[[/a]]"),
    ("a39", "[[a href=\"/x\" data-X=\"1\"]]y1[[/a]]\n[[a href=\"/x\" DATA-X=\"1\"]]y2[[/a]]\n[[a href=\"/x\" data-=\"1\"]]y3[[/a]]"),
    ("a40", "[[a href=\"/x\" name=\"n\" title=\"t\" rel=\"r\" onclick=\"o\" foo=\"f\" lang=\"en\" dir=\"ltr\" align=\"left\" tabindex=\"2\" aria-label=\"a\"]]y[[/a]]"),
    ("a41", "[[a href=\"/x\" CLASS=\"c\" HREF=\"/u\"]]y[[/a]]"),
    ("a42", "[[a data-x=\"\" id=\"i\"]]y1[[/a]]\n[[a href=\"/x\" class=\"a  b\"]]y2[[/a]]\n[[a href=\"/x\" class=\"c\" class=\"\"]]y3[[/a]]\n[[a href=\"/x\" href=\"/u\"]]y4[[/a]]"),
    ("a43", "[[A HREF=\"/x\" href=\"/y\"]]UPPER[[/A]]"),
    ("a44", "[[a href=\"/x\" class='single' id=unquoted style = \"spaced\"]]quote-forms[[/a]]"),

    # Family 5: Boundary spaces, nesting, malformed & literal shapes
    ("a45", "[[a]] one [[/a]]\nx[[a]] one [[/a]]y\n[[a]]one[[/a]][[a]] two[[/a]]\n[[a]]one [[/a]][[a]]two[[/a]]"),
    ("a46", "[[a href=\"/1\"]]x[[a href=\"/2\"]]y[[/a]]z[[/a]]\n[[a href=\"/1\"]][[/a]] [[a href=\"/2\"]]y[[/a]]"),
    ("a47", "a[[a ]] b[[/a]]c"),
    ("a48", "[[anchor href=\"/x\"]]txt[[/anchor]]\n[[*a href=\"/x\"]]txt[[/a]]\n[[a href=\"/x\"]]txt[[/anchor]]"),
    ("a49", "[[a href=\"http://example.com\"]]unterminated\n[[div]]\ninside\n[[/div]]"),
    ("a50", "[[a href=\"/x\"]]txt[[/a]]]\n[[# name]]]"),
    ("a51", "[[a href=\"/x\"]]\nline1\nline2\n[[/a]]"),
    ("a52", "[[a href=\"/x\"]]line1\n\nline2[[/a]]"),

    # Family 6: Scored [[a_]] and R2 cross-rule sightings
    ("a53", "[[a_]]X[[/a]]"),
    ("a54", "[[a_ href=\"https://example.com\"]]^^label^^[[/a]]"),
    ("a55", "PRE\n[[a_ href=\"https://example.com\"]]x[[/a]]\nPOST"),
    ("a56", "PRE\n\n[[a_ href=\"/x\"]]mid[[/a]]\n\nPOST"),
    ("a57", "[[a_ href=\"some-page\"]]\nline1\nline2\n[[/a]]"),
    ("a58", "[[a href=\"http://x/a--b\"]]label[[/a]]\nx"),
    ("a59", "[[a href=\"https://example.com\"]]^^label^^[[/a]]\nx"),
    ("a60", "[[a href=\"http://x\"]]__label__[[/a]]"),
]

out_path = Path(__file__).resolve().parent / "battery.jsonl"
with out_path.open("w", encoding="utf-8") as f:
    for cid, src in cases:
        f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
print(f"Wrote {len(cases)} cases to {out_path}")
