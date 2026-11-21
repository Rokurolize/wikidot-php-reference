#!/usr/bin/env python3
"""Build Wave 2 (Divprefilter, Divalign, Note, Gallery) and Wave 3 (User, Button, Embed, Social, File) batteries and probes."""
import json
import os
from pathlib import Path
from tools import ROOT, load_jsonl, save_jsonl, run_batch

r316_cases = load_jsonl(ROOT / "materials/conformance-r316/middle2-all-cases.jsonl")
r317_cases = load_jsonl(ROOT / "materials/conformance-r317/final-all-cases.jsonl")


def extract_by_prefix(cases, prefix, extra_ids=()):
    out = []
    seen = set()
    for c in cases:
        cid = c["id"]
        if cid.startswith(prefix) or cid in extra_ids:
            if cid not in seen:
                seen.add(cid)
                out.append({"id": cid, "source": c["source"]})
    return out


def write_rule(name, base_cases, extra_cases, probe_specs):
    rdir = ROOT / "refval" / name
    os.makedirs(rdir, exist_ok=True)
    battery = list(base_cases)
    seen = {c["id"] for c in battery}
    for cid, src in extra_cases:
        assert cid not in seen, f"dup {cid}"
        seen.add(cid)
        battery.append({"id": cid, "source": src})
    probes = []
    for pid, src in probe_specs:
        assert not src.endswith("\n") and not src.endswith(" ") and "\r" not in src, f"probe {name}/{pid} unsafe: {src!r}"
        probes.append({"id": pid, "source": src})
        if pid not in seen:
            seen.add(pid)
            battery.append({"id": pid, "source": src})
    save_jsonl(rdir / "battery.jsonl", battery)
    save_jsonl(rdir / "probes.jsonl", probes)
    run_batch(rdir / "battery.jsonl", rdir / "ref-render-before.jsonl", "render")
    print(f"{name:14s}: battery={len(battery)} probes={len(probes)}")


# 6. DIVPREFILTER
dp_base = extract_by_prefix(r316_cases, "dp-", ("sz70-size-crosses-div",))
dp_extra = [
    ("dp-x01", "[[div]]\na\n[[/div]]\n[[div]]\nb\n[[/div]]"),
    ("dp-x02", "[[div]]\na\n[[/div]]\n\n[[div]]\nb\n[[/div]]"),
    ("dp-x03", "[[div]]\na\n[[/div]]   [[div]]\nb\n[[/div]]"),
    ("dp-x04", "[[div]]\na\n[[/div]]\t[[div]]\nb\n[[/div]]"),
    ("dp-x05", "[[div]]\na\n[[/div]]\n[[div class=\"b\"]]\nb\n[[/div]]"),
    ("dp-x06", "[[div]]\na\n[[/div]]\n[[div_]]\nb\n[[/div]]"),
    ("dp-x07", "[[DIV]]\na\n[[/DIV]]\n[[DIV]]\nb\n[[/DIV]]"),
    ("dp-x08", "[[/DIV]]\n[[DIV]]\nx\n[[/div]]"),
    ("dp-x09", "[[div]]\na\n[[/div]] x [[div]]\nb\n[[/div]]"),
    ("dp-x10", "[[div]]\na\n[[/div]]\n[[span]]s[[/span]]"),
    ("dp-x11", "[[div]]\na\n[[/div]]\n[[div]]\nb\n[[/div]]\n[[div]]\nc\n[[/div]]"),
    ("dp-x12", "[[/div]] [[divx]]"),
    ("dp-x13", "[[/div]] [[div"),
    ("dp-x14", "[[div]]\n[[/div]]\n\n[[div]]\n[[/div]]"),
    ("dp-x15", "[[div]]a[[/div]] [[div]]b[[/div]]"),
    ("dp-x16", "[[div]]\na\n[[/div]]\n\n\n[[div]]\nb\n[[/div]]"),
]
dp_probes = [
    ("p01", "[[div]]\na\n[[/div]]\n[[div]]\nb\n[[/div]]"),
    ("p02", "[[div]]\na\n[[/div]]\n\n[[div]]\nb\n[[/div]]"),
    ("p03", "[[div]]\na\n[[/div]]\n\n\n[[div]]\nb\n[[/div]]"),
    ("p04", "[[div]]\na\n[[/div]]   [[div]]\nb\n[[/div]]"),
    ("p05", "[[div]]\na\n[[/div]]\t[[div]]\nb\n[[/div]]"),
    ("p06", "[[div]]\na\n[[/div]]\n[[div class=\"b\"]]\nb\n[[/div]]"),
    ("p07", "[[div]]\na\n[[/div]]\n[[div_]]\nb\n[[/div]]"),
    ("p08", "[[DIV]]\na\n[[/DIV]]\n[[DIV]]\nb\n[[/DIV]]"),
    ("p09", "[[/DIV]]\n[[DIV]]"),
    ("p10", "[[/Div]] [[dIv]]"),
    ("p11", "[[div]]\na\n[[/div]] x [[div]]\nb\n[[/div]]"),
    ("p12", "[[div]]\na\n[[/div]]\n[[span]]s[[/span]]"),
    ("p13", "[[div]]\na\n[[/div]]\n[[div]]\nb\n[[/div]]\n[[div]]\nc\n[[/div]]"),
    ("p14", "[[/div]] [[divx]]"),
    ("p15", "[[/div]] [[div"),
    ("p16", "[[div]]\n[[/div]]\n\n[[div]]\n[[/div]]"),
    ("p17", "[[div]]a[[/div]] [[div]]b[[/div]]"),
    ("p18", "[[size larger]]\n[[div class=\"outer\"]]\nheader\n[[div class=\"links\"]]\nlink\n[[/div]]\n[[div class=\"content\"]]\n[[/size]]\nbody\n[[/div]]\n[[/div]]"),
]
write_rule("divprefilter", dp_base, dp_extra, dp_probes)

# 7. DIVALIGN
da_base = extract_by_prefix(r316_cases, "da-")
da_extra = [
    ("da-x01", "[[=]]\np1\n\np2\n[[/=]]"),
    ("da-x02", "[[=]]\n* a\n* b\n[[/=]]"),
    ("da-x03", "[[=]]\n|| a || b ||\n[[/=]]"),
    ("da-x04", "[[=]]\n[[div]]\nin\n[[/div]]\n[[/=]]"),
    ("da-x05", "[[= class=\"x\"]]\nbody\n[[/=]]"),
    ("da-x06", "[[===]]\nbody\n[[/===]]"),
    ("da-x07", "[[=]] \nbody\n[[/=]]"),
    ("da-x08", "[[=]]\nbody\n [[/=]]"),
    ("da-x09", "[[=]]\nbody\n[[/=]]\n[[>]]\nright\n[[/>]]"),
    ("da-x10", "[[<]]\n[[>]]\n[[==]]\ndeep\n[[/==]]\n[[/>]]\n[[/<]]"),
    ("da-x11", "[[=]]\n= inline center\n[[/=]]"),
    ("da-x12", "[[=]]\n[[note]]\nin note\n[[/note]]\n[[/=]]"),
    ("da-x13", "[[div]]\n[[=]]\nin div\n[[/=]]\n[[/div]]"),
    ("da-x14", "[[=]]\n+ Heading\n[[/=]]"),
    ("da-x15", "[[=]]\n> quoted\n[[/=]]"),
]
da_probes = [
    ("p01", "[[=]]\ncentered\n[[/=]]"),
    ("p02", "[[<]]\nleft\n[[/<]]"),
    ("p03", "[[>]]\nright\n[[/>]]"),
    ("p04", "[[==]]\njustified\n[[/==]]"),
    ("p05", "[[==]]\nx\n[[/=]]\n\n[[=]]\nx\n[[/==]]"),
    ("p06", "[[=]]\n[[/=]]"),
    ("p07", "[[=]]\n\n[[/=]]"),
    ("p08", "x\n[[=]]\nbody\n[[/=]]\ny"),
    ("p09", "[[=]]\nbody\n[[/=]] tail"),
    ("p10", " [[=]]\nbody\n[[/=]]\n\nx[[=]]\nbody\n[[/=]]"),
    ("p11", "[[=]] body\n[[/=]]\n\n[[=]]\nbody[[/=]]"),
    ("p12", "[[=]]\n[[<]]\ninner\n[[/<]]\n[[/=]]"),
    ("p13", "[[=]]\n[[=]]\ninner\n[[/=]]\n[[/=]]"),
    ("p14", "[[=]]\n[[=]]\nx\n[[/=]]\ny\n[[/=]]"),
    ("p15", "[[=]]\n[[=]]\n[[/=]]"),
    ("p16", "[[=]]\n[[/=]] extra\n[[/=]]"),
    ("p17", "[[=]]\np1\n\np2\n[[/=]]"),
    ("p18", "[[=]]\n* a\n* b\n\n----\n[[/=]]"),
    ("p19", "[[= class=\"x\"]]\nbody\n[[/=]]\n\n[[=]] \nbody\n[[/=]]"),
    ("p20", "[[=]]\n**bold** body\n[[/=]]"),
]
write_rule("divalign", da_base, da_extra, da_probes)

# 8. NOTE
nt_base = extract_by_prefix(r316_cases, "nt-", ("lb35",))
nt_extra = [
    ("nt-x01", "[[note]]\np1\n\np2\n[[/note]]"),
    ("nt-x02", "[[note class=\"x\"]]\nbody\n[[/note]]"),
    ("nt-x03", "[[note_]]\nbody\n[[/note]]"),
    ("nt-x04", "[[note]] \nbody\n[[/note]]"),
    ("nt-x05", "[[note]]\nbody\n[[/note ]]"),
    ("nt-x06", "x\n[[note]]\nbody\n[[/note]]\ny"),
    ("nt-x07", "x\n\n[[note]]\nbody\n[[/note]]\n\ny"),
    ("nt-x08", "[[note]]\n|| a || b ||\n[[/note]]"),
    ("nt-x09", "[[note]]\n> quote\n[[/note]]"),
    ("nt-x10", "[[note]]\n+ Head\n[[/note]]"),
    ("nt-x11", "[[div]]\n[[note]]\nbody\n[[/note]]\n[[/div]]"),
    ("nt-x12", "[[note]]\n[[=]]\ncentered\n[[/=]]\n[[/note]]"),
    ("nt-x13", "[[note]]\nline1\nline2\n[[/note]]"),
    ("nt-x14", "[[note]]\n\nline1\n[[/note]]"),
    ("nt-x15", "[[note]]\nline1\n\n[[/note]]"),
    ("nt-x16", "[[note]]\n* a\n* b\n[[/note]]"),
    ("nt-x17", "[[note]]\nbody1\n[[/note]]\n\n[[note]]\nbody2\n[[/note]]"),
    ("nt-x18", "[[note]]\n[[collapsible]]\nin\n[[/collapsible]]\n[[/note]]"),
    ("nt-x19", "[[note]]\na _\nb\n[[/note]]"),
]
nt_probes = [
    ("p01", "[[note]]\nbody\n[[/note]]"),
    ("p02", "x\n[[note]]\nbody\n[[/note]]\ny"),
    ("p03", "x\n\n[[note]]\nbody\n[[/note]]\n\ny"),
    ("p04", "[[note]]\n[[/note]]"),
    ("p05", "[[note]]\n\n[[/note]]"),
    ("p06", "[[note]]\nline1\nline2\n[[/note]]"),
    ("p07", "[[note]]\np1\n\np2\n[[/note]]"),
    ("p08", "[[note]] body\n[[/note]]"),
    ("p09", "[[note]]\nbody[[/note]]"),
    ("p10", "[[NOTE]]\nbody\n[[/NOTE]]"),
    ("p11", "[[Note]]\nbody\n[[/note]]\n\n[[note]]\nbody\n[[/NOTE]]"),
    ("p12", "[[note]]\n[[note]]\ninner\n[[/note]]\n[[/note]]"),
    ("p13", "a [[note]]\nb\n[[/note]] c"),
    ("p14", "[[note]]\na[[/note]]b[[/note]]"),
    ("p15", "[[note]]\nbody\n[[/note]]\n[[note]]\nc\n[[/note]]"),
    ("p16", "[[note class=\"x\"]]\nbody\n[[/note]]\n\n[[note_]]\nbody\n[[/note]]"),
    ("p17", "[[note]] \nbody\n[[/note]]\n\n[[note]]\nbody\n[[/note ]]"),
    ("p18", "[[note]]\n* a\n* b\n[[/note]]"),
    ("p19", "[[note]]\n**bold** and ----\n[[/note]]"),
    ("p20", "[[note]]\n[[div]]\nx\n[[/div]]\n[[/note]]"),
]
write_rule("note", nt_base, nt_extra, nt_probes)

# 9. GALLERY
ga_base = extract_by_prefix(r316_cases, "ga-")
ga_extra = [
    ("ga-x01", "[[gallery size=\"small\"]]"),
    ("ga-x02", "[[gallery size=\"medium\"]]\n: a.png\n[[/gallery]]"),
    ("ga-x03", "[[gallery size=\"thumbnail\"]]\n: a.png\n[[/gallery]]"),
    ("ga-x04", "[[gallery size=\"square\"]]\n: a.png\n[[/gallery]]"),
    ("ga-x05", "[[gallery size=\"original\"]]\n: a.png\n[[/gallery]]"),
    ("ga-x06", "[[gallery size=\"large\"]]\n: a.png\n[[/gallery]]"),
    ("ga-x07", "[[gallery size=\"mini\"]]\n: a.png\n[[/gallery]]"),
    ("ga-x08", "[[gallery]]\n: other-page/a.png\n[[/gallery]]"),
    ("ga-x09", "[[gallery]]\n: /other-page/a.png\n[[/gallery]]"),
    ("ga-x10", "[[gallery]]\n: https://example.com/a.png\n[[/gallery]]"),
    ("ga-x11", "[[gallery]]\n: *https://example.com/a.png\n[[/gallery]]"),
    ("ga-x12", "[[gallery]]\n: a.png link=\"https://example.com\"\n[[/gallery]]"),
    ("ga-x13", "[[gallery]]\n: a.png link=\"*https://example.com\"\n[[/gallery]]"),
    ("ga-x14", "[[gallery]]\n: a.png link=\"some-page\"\n[[/gallery]]"),
    ("ga-x15", "[[gallery]]\n: a.png alt=\"My Alt\" title=\"My Title\"\n[[/gallery]]"),
    ("ga-x16", "[[gallery order=\"name desc\" style=\"color:red\"]]\n: a.png\n[[/gallery]]"),
    ("ga-x17", "[[gallery]]\n: a.png\n: https://example.com/b.png\n[[/gallery]]"),
    ("ga-x18", "[[gallery]]\n: a.png \"quoted caption\"\n[[/gallery]]"),
    ("ga-x19", "[[gallery size=\"small\"]]\n: a.png\n: b.png\n[[/gallery]]"),
    ("ga-x20", "[[gallery]]\n: http://example.com/a.png link=\"http://example.org\"\n[[/gallery]]"),
]
ga_probes = [
    ("p01", "[[gallery]]"),
    ("p02", "[[gallery size=\"small\"]]"),
    ("p03", "[[gallery]]\n: a.png\n[[/gallery]]"),
    ("p04", "[[gallery]]\n: a.png\n: b.png\n[[/gallery]]"),
    ("p05", "[[gallery size=\"small\"]]\n: a.png\n[[/gallery]]"),
    ("p06", "[[gallery size=\"medium\"]]\n: a.png\n[[/gallery]]"),
    ("p07", "[[gallery size=\"square\"]]\n: a.png\n[[/gallery]]"),
    ("p08", "[[gallery size=\"original\"]]\n: a.png\n[[/gallery]]"),
    ("p09", "[[gallery size=\"large\"]]\n: a.png\n[[/gallery]]"),
    ("p10", "[[gallery size=\"\"]]\n: a.png\n[[/gallery]]"),
    ("p11", "[[gallery size=\"0\"]]\n: a.png\n[[/gallery]]"),
    ("p12", "[[gallery]]\n: other-page/a.png\n[[/gallery]]"),
    ("p13", "[[gallery]]\n: /other-page/a.png\n[[/gallery]]"),
    ("p14", "[[gallery]]\n: https://example.com/a.png\n[[/gallery]]"),
    ("p15", "[[gallery]]\n: *https://example.com/a.png\n[[/gallery]]"),
    ("p16", "[[gallery]]\n: a.png link=\"https://example.com\"\n[[/gallery]]"),
    ("p17", "[[gallery]]\n: a.png link=\"*https://example.com\"\n[[/gallery]]"),
    ("p18", "[[gallery]]\n: a.png link=\"some-page\"\n[[/gallery]]"),
    ("p19", "[[gallery]]\n: a.png alt=\"My Alt\" title=\"My Title\"\n[[/gallery]]"),
    ("p20", "[[gallery]]\nnot a source\n[[/gallery]]"),
    ("p21", "[[gallery]]\n: a.png"),
    ("p22", "[[GALLERY]]\n: a.png\n[[/GALLERY]]"),
    ("p23", "[[gallery\nsize=\"small\"]]\n: a.png\n[[/gallery]]"),
    ("p24", "x [[gallery]]\n: a.png\n[[/gallery]]"),
]
write_rule("gallery", ga_base, ga_extra, ga_probes)

# 10. USER
us_base = extract_by_prefix(r317_cases, "us-")
us_extra = [
    ("us-x01", "[[user michal-frackowiak]]"),
    ("us-x02", "[[*user michal-frackowiak]]"),
    ("us-x03", "[[user Michal Frackowiak]]"),
    ("us-x04", "[[*user Michal Frackowiak]]"),
    ("us-x05", "[[user nonexistent-refval-xyz-99999]]"),
    ("us-x06", "[[*user nonexistent-refval-xyz-99999]]"),
    ("us-x07", "[[USER michal-frackowiak]]"),
    ("us-x08", "[[*User michal-frackowiak]]"),
    ("us-x09", "[[user nonexistent-refval-xyz-99999 ]]"),
    ("us-x10", "[[user  michal-frackowiak]]"),
    ("us-x11", "[[user <b>xss</b>]]"),
    ("us-x12", "[[user a\"b&c]]"),
    ("us-x13", "[[user wikidot]]"),
    ("us-x14", "[[*user wikidot]]"),
    ("us-x15", "pre [[user michal-frackowiak]] post"),
    ("us-x16", "[[div]]\n[[user michal-frackowiak]]\n[[/div]]"),
    ("us-x17", "[[note]]\n[[user michal-frackowiak]]\n[[/note]]"),
    ("us-x18", "[[user a\nb]]"),
    ("us-x19", "[[user\tmichal-frackowiak]]"),
    ("us-x20", "[[user a]]]"),
]
us_probes = [
    ("p01", "[[user michal-frackowiak]]"),
    ("p02", "[[*user michal-frackowiak]]"),
    ("p03", "[[user Michal Frackowiak]]"),
    ("p04", "[[*user Michal Frackowiak]]"),
    ("p05", "[[user nonexistent-refval-xyz-99999]]"),
    ("p06", "[[*user nonexistent-refval-xyz-99999]]"),
    ("p07", "[[USER michal-frackowiak]]"),
    ("p08", "[[*User michal-frackowiak]]"),
    ("p09", "[[user  michal-frackowiak]]"),
    ("p10", "[[user michal-frackowiak ]]"),
    ("p11", "[[user]]\n[[user ]]\n[[*user]]\n[[**user michal-frackowiak]]"),
    ("p12", "[[user\tmichal-frackowiak]]"),
    ("p13", "[[user a\nb]]"),
    ("p14", "[[user a]b]]\n[[user a]]]"),
    ("p15", "[[user <b>xss</b>]]"),
    ("p16", "[[user a\"b&c]]"),
    ("p17", "[[user wikidot]]\n[[*user wikidot]]"),
    ("p18", "pre [[user michal-frackowiak]] post"),
    ("p19", "[[user café]]"),
    ("p20", "[[code]][[user michal-frackowiak]][[/code]]"),
]
write_rule("user", us_base, us_extra, us_probes)

# 11. BUTTON
bt_base = extract_by_prefix(r317_cases, "bt-")
bt_extra = [
    ("bt-x01", "[[button edit-append]]"),
    ("bt-x02", "[[button edit-sections]]"),
    ("bt-x03", "[[button history]]"),
    ("bt-x04", "[[button print]]"),
    ("bt-x05", "[[button files]]"),
    ("bt-x06", "[[button tags]]"),
    ("bt-x07", "[[button source]]"),
    ("bt-x08", "[[button talk]]"),
    ("bt-x09", "[[button backlinks]]"),
    ("bt-x10", "[[button set-tags]]"),
    ("bt-x11", "[[button set-tags text=\"Tag It\" tags=\"+a -b\"]]"),
    ("bt-x12", "[[button rename]]"),
    ("bt-x13", "[[button delete]]"),
    ("bt-x14", "[[button parent]]"),
    ("bt-x15", "[[button lock]]"),
    ("bt-x16", "[[button edit-meta]]"),
    ("bt-x17", "[[button watchers]]"),
    ("bt-x18", "[[button edit_append]]"),
    ("bt-x19", "[[button edit_sections]]"),
    ("bt-x20", "[[button edit text=\"a<b>c&d'e\"]]"),
    ("bt-x21", "[[button edit class=\"c1 c2\" style=\"color:red\"]]"),
    ("bt-x22", "[[button unknown-type]]"),
]
bt_probes = [
    ("p01", "[[button edit]]"),
    ("p02", "[[button edit-append]]\n[[button edit-sections]]"),
    ("p03", "[[button history]]\n[[button print]]\n[[button files]]"),
    ("p04", "[[button tags]]\n[[button source]]\n[[button talk]]\n[[button backlinks]]"),
    ("p05", "[[button edit_append]]\n[[button edit_sections]]"),
    ("p06", "[[button set-tags]]\n[[button set-tags text=\"Tag It\" tags=\"+a -b\"]]"),
    ("p07", "[[button rename]]\n[[button delete]]\n[[button parent]]\n[[button lock]]"),
    ("p08", "[[button edit-meta]]\n[[button watchers]]\n[[button unknown-type]]"),
    ("p09", "[[button edit text=\"Edit Page\"]]"),
    ("p10", "[[button edit text=\"Edit\" class=\"my-btn\" style=\"color: red;\"]]"),
    ("p11", "[[button edit id=\"x\" data-foo=\"bar\" title=\"t\"]]"),
    ("p12", "[[button edit text=\"\"]]"),
    ("p13", "[[button edit text=\"a<b>c&d'e\"]]"),
    ("p14", "[[BUTTON edit]]\n[[button EDIT]]\n[[button Edit_Sections]]"),
    ("p15", "[[button edit ]]"),
    ("p16", "[[button edit  ]]"),
    ("p17", "[[button edit x]]"),
    ("p18", "[[button edit text='single']]"),
    ("p19", "[[button edit\ntext=\"newline\"]]"),
    ("p20", "[[button edit\ttext=\"tab\"]]"),
    ("p21", "[[button]]\n[[button ]]"),
    ("p22", "[[button edit text=\"a\" text=\"b\"]]"),
]
write_rule("button", bt_base, bt_extra, bt_probes)

# 12. EMBED
eb_base = extract_by_prefix(r317_cases, "eb-")
eb_extra = [
    ("eb-x01", "[[embed]]\n<iframe src=\"http://example.com\" width=\"400\" height=\"300\"></iframe>\n[[/embed]]"),
    ("eb-x02", "[[embed]]\n<iframe src=\"https://example.com\" width=\"400\" height=\"300\"></iframe>\n[[/embed]]"),
    ("eb-x03", "[[embed]]\n<iframe src=\"http://example.com\" onclick=\"alert(1)\"></iframe>\n[[/embed]]"),
    ("eb-x04", "[[embedvideo]]\n<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/dQw4w9WgXcQ\" frameborder=\"0\"></iframe>\n[[/embedvideo]]"),
    ("eb-x05", "[[embedaudio]]\n<iframe width=\"100\" height=\"100\" src=\"https://w.soundcloud.com/player/?url=https://api.soundcloud.com/tracks/1\"></iframe>\n[[/embedaudio]]"),
    ("eb-x06", "[[embed]]<iframe src=\"http://example.com\"></iframe>[[/embed]]"),
    ("eb-x07", "[[embed]]<iframe src=\"http://example.com\" data-x=\"1\"></iframe>[[/embed]]"),
    ("eb-x08", "[[embed]]<iframe src=\"http://example.com\">fallback</iframe>[[/embed]]"),
    ("eb-x09", "[[embed]]<a href=\"http://example.com\">hi</a>[[/embed]]"),
    ("eb-x10", "[[embed]]<div class=\"x\">hi</div>[[/embed]]"),
    ("eb-x11", "[[embed]]\n<script type=\"text/javascript\" src=\"https://static.wikidot.com/common--misc/reflection.js\"></script>\n[[/embed]]"),
    ("eb-x12", "[[embed]]\n<iframe src=\"http://wikimapia.org/s/123\"></iframe>\n[[/embed]]"),
    ("eb-x13", "[[embed]]<iframe src=\"javascript:alert(1)\"></iframe>[[/embed]]"),
    ("eb-x14", "[[embed]]\n<object width=\"425\" height=\"344\"><param name=\"movie\" value=\"http://www.youtube.com/v/abc\"></param><embed src=\"http://www.youtube.com/v/abc\" type=\"application/x-shockwave-flash\" width=\"425\" height=\"344\"></embed></object>\n[[/embed]]"),
    ("eb-x15", "[[embed]]hello world[[/embed]]"),
    ("eb-x16", "[[embedvideo]]hello world[[/embedvideo]]"),
    ("eb-x17", "[[embedaudio]]hello world[[/embedaudio]]"),
    ("eb-x18", "[[embed]]<iframe src=\"http://example.com\" width=\"200\" height=\"100\" allow=\"fullscreen\"></iframe>[[/embed]]"),
    ("eb-x19", "pre [[embed]]hello[[/embed]] post"),
    ("eb-x20", "[[div]]\n[[embed]]hello[[/embed]]\n[[/div]]"),
]
eb_probes = [
    ("p01", "[[embed]]body[[/embed]]"),
    ("p02", "[[embedvideo]]body[[/embedvideo]]"),
    ("p03", "[[embedaudio]]body[[/embedaudio]]"),
    ("p04", "[[embedvideo]]body[[/embed]]"),
    ("p05", "[[embed]]body[[/embedvideo]]"),
    ("p06", "[[EMBED]]x[[/EMBED]]\n[[EmbedVideo]]x[[/EmbedAudio]]"),
    ("p07", "[[embed]][[/embed]]\n[[embed]] [[/embed]]"),
    ("p08", "[[embed]]unclosed"),
    ("p09", "[[embed]]a[[/embed]]b[[/embed]]"),
    ("p10", "[[embed]][[embed]]x[[/embed]]"),
    ("p11", "[[embed ]]x[[/embed]]\n[[embed]]x[[/embed ]]"),
    ("p12", "[[embed]]\n<iframe src=\"http://example.com\" width=\"400\" height=\"300\"></iframe>\n[[/embed]]"),
    ("p13", "[[embed]]\n<iframe src=\"https://example.com\" width=\"400\" height=\"300\"></iframe>\n[[/embed]]"),
    ("p14", "[[embed]]\n<iframe src=\"http://example.com\" onclick=\"alert(1)\"></iframe>\n[[/embed]]"),
    ("p15", "[[embedvideo]]\n<iframe width=\"560\" height=\"315\" src=\"https://www.youtube.com/embed/dQw4w9WgXcQ\" frameborder=\"0\"></iframe>\n[[/embedvideo]]"),
    ("p16", "[[embed]]<iframe src=\"http://example.com\">fallback</iframe>[[/embed]]"),
    ("p17", "[[embed]]<iframe src=\"javascript:alert(1)\"></iframe>[[/embed]]"),
    ("p18", "[[embed]]<a href=\"http://example.com\">hi</a>[[/embed]]"),
    ("p19", "[[embed]]**bold**[[/embed]]"),
    ("p20", "pre [[embed]]hello[[/embed]] post"),
]
write_rule("embed", eb_base, eb_extra, eb_probes)

# 13. SOCIAL
so_base = extract_by_prefix(r317_cases, "so-")
so_extra = [
    ("so-x01", "[[social facebook]]"),
    ("so-x02", "[[social reddit]]"),
    ("so-x03", "[[social twitter]]"),
    ("so-x04", "[[social digg, reddit]]"),
    ("so-x05", "[[social facebook, twitter, reddit]]"),
    ("so-x06", "[[social facebook,twitter]]"),
    ("so-x07", "[[social del.icio.us]]"),
    ("so-x08", "[[social unknownsite]]"),
    ("so-x09", "[[SOCIAL]]"),
    ("so-x10", "[[SOCIAL facebook]]"),
    ("so-x11", "[[social Facebook]]"),
    ("so-x12", "[[social   facebook  ]]"),
    ("so-x13", "[[social]]\n[[social facebook]]"),
    ("so-x14", "pre [[social]] post"),
    ("so-x15", "[[div]]\n[[social]]\n[[/div]]"),
    ("so-x16", "[[note]]\n[[social]]\n[[/note]]"),
    ("so-x17", "[[social]]\n\n[[social]]"),
    ("so-x18", "[[social blinkbits, digg, fark]]"),
]
so_probes = [
    ("p01", "[[social]]"),
    ("p02", "[[social digg]]"),
    ("p03", "[[social facebook]]"),
    ("p04", "[[social reddit]]"),
    ("p05", "[[social twitter]]"),
    ("p06", "[[social digg, reddit]]"),
    ("p07", "[[social digg reddit]]"),
    ("p08", "[[social facebook, twitter, reddit]]"),
    ("p09", "[[social unknownsite]]"),
    ("p10", "[[SOCIAL]]"),
    ("p11", "[[SOCIAL facebook]]"),
    ("p12", "[[social Facebook]]"),
    ("p13", "[[social ]]"),
    ("p14", "[[social  ]]"),
    ("p15", "[[social  facebook]]"),
    ("p16", "[[social facebook ]]"),
    ("p17", "[[social\tfacebook]]"),
    ("p18", "[[social\nfacebook]]"),
    ("p19", "pre [[social]] post"),
    ("p20", "[[social a]b]]\n[[social a]]]"),
]
write_rule("social", so_base, so_extra, so_probes)

# 14. FILE
fi_base = extract_by_prefix(r317_cases, "fi-")
fi_extra = [
    ("fi-x01", "[[file other-page/a.txt]]"),
    ("fi-x02", "[[file other-page/a.txt|Label]]"),
    ("fi-x03", "[[file /other-page/a.txt]]"),
    ("fi-x04", "[[file /other-page/a.txt|Label]]"),
    ("fi-x05", "[[file a/b/c.txt]]"),
    ("fi-x06", "[[file a.txt|**bold**]]"),
    ("fi-x07", "[[file a.txt|//italic//]]"),
    ("fi-x08", "[[file a\"b.txt|c<d>e]]"),
    ("fi-x09", "[[file a&b.txt|x&y]]"),
    ("fi-x10", "[[file]]"),
    ("fi-x11", "[[file a.txt]]"),
    ("fi-x12", "[[file :other-page/a.txt]]"),
    ("fi-x13", "[[file :site:page/a.txt]]"),
    ("fi-x14", "[[file cat:page/a.txt]]"),
    ("fi-x15", "[[file cat:page/a.txt|Cat File]]"),
    ("fi-x16", "[[file https://example.com/a.txt]]"),
    ("fi-x17", "[[*file a.txt]]"),
    ("fi-x18", "[[file a.txt|Label with \"quotes\"]]"),
    ("fi-x19", "[[file my file.txt|My File]]"),
    ("fi-x20", "[[file a.txt|Label]] tail"),
]
fi_probes = [
    ("p01", "[[file a.txt]]"),
    ("p02", "[[file a.txt|Label]]"),
    ("p03", "[[file other-page/a.txt]]"),
    ("p04", "[[file other-page/a.txt|Label]]"),
    ("p05", "[[file /other-page/a.txt]]"),
    ("p06", "[[file cat:page/a.txt|Cat File]]"),
    ("p07", "[[file :site:page/a.txt]]"),
    ("p08", "[[file a.txt|]]"),
    ("p09", "[[file a.txt| ]]"),
    ("p10", "[[file a.txt | Label ]]"),
    ("p11", "[[file  a.txt  ]]"),
    ("p12", "[[file |x]]\n[[file |]]"),
    ("p13", "[[file a|b|c]]"),
    ("p14", "[[FILE a.txt]]\n[[File a.txt|Label]]"),
    ("p15", "[[file my file.txt|My File]]\n[[file café.txt]]"),
    ("p16", "[[file a.txt|**bold**]]"),
    ("p17", "[[file a\"b.txt|c<d>e]]"),
    ("p18", "[[file a\nb.txt]]\n[[file a.txt|x\ny]]"),
    ("p19", "[[file ]]\n[[file]]\n[[*file a.txt]]"),
    ("p20", "[[file\ta.txt]]\n[[file a]]]\n[[file a]b]]"),
]
write_rule("file", fi_base, fi_extra, fi_probes)
