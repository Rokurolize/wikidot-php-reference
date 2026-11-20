#!/usr/bin/env python3
"""Compare the R2 Image reference renders (before and after correction) against the shared ftml dumper and, when present, against live saved-page captures.

Two normalizations are reported. The frame normalization factors out only
frame-level or serving-layer surface that no Image rule owns: the https host
of the file-serving base (wikipedia-style wjfiles/wdfiles, which is deployment
specific), the current-page name in local--files/ paths (the harness gives the
reference an empty page name and the dumper uses "some-page"), XHTML '/>' against
HTML '>' self-closing, collapsed blank lines and leading indentation. The shape
normalization additionally sorts the attributes inside each <img> and <a> tag,
because live probes p09, p10, p11, p16 and p17 show that the reference's
attribute order is live truth and the dumper's canonical order is a candidate
ftml divergence (IMG-F1, IMG-F2, IMG-F3 in SECTION.md); sorting lets the rest of
the tag shape be compared without silently accepting either order. Byte-identical
counts are reported separately. Run from this directory with python3 compare.py,
which writes compare-report.txt.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_jsonl(path):
    out = {}
    with open(ROOT / path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rec = json.loads(line)
                out[rec["id"]] = rec
    return out


def _sort_tag_attrs(match):
    tag = match.group(1)
    rest = match.group(2)
    # Split on whitespace but keep quoted values intact.
    parts = re.findall(r'[^\s"\']+(?:"[^"]*"|\'[^\']*\')?|[^\s]+', rest.strip())
    parts = [p for p in parts if p]
    parts.sort(key=lambda p: p.split("=", 1)[0].lower())
    return "<" + tag + (" " + " ".join(parts) if parts else "") + ">"


def shape(text, sort_attrs=False):
    if not isinstance(text, str):
        return ""
    text = text.replace("\r\n", "\n").replace("<br />", "<br>").replace(" />", ">")
    text = re.sub(r"https://[a-z0-9.\-]+\.(?:wjfiles|wdfiles)\.com", "", text)
    text = text.replace("local--files/some-page/", "local--files/")
    text = text.replace("local--resized-images/some-page/", "local--resized-images/")
    text = re.sub(r"(local--(?:files|resized-images))/+", r"\1/", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = "\n".join(line.lstrip(" ") for line in text.split("\n"))
    if sort_attrs:
        text = re.sub(r"<(img|a)\b([^>]*)>", _sort_tag_attrs, text)
    return text.strip("\n")


def compare_battery(report):
    before = load_jsonl("ref-render-before.jsonl")
    final = load_jsonl("ref-render-final.jsonl")
    ftml = load_jsonl("ftml-dump.jsonl")
    report.append("BATTERY (whole-document cases)")
    report.append("cases=%d" % len(before))
    for label, ref in (("before", before), ("final", final)):
        byte = sum(1 for c in ref if ref[c].get("output") == ftml.get(c, {}).get("html"))
        frame = sum(1 for c in ref if shape(ref[c].get("output", "")) == shape(ftml.get(c, {}).get("html", "")))
        tagged = sum(1 for c in ref if shape(ref[c].get("output", ""), True) == shape(ftml.get(c, {}).get("html", ""), True))
        report.append("%s: byte_identical=%d/%d frame_normalized=%d/%d shape_normalized=%d/%d" %
                      (label, byte, len(ref), frame, len(ref), tagged, len(ref)))
    diffs = [c for c in sorted(final)
             if shape(final[c].get("output", ""), True) != shape(ftml.get(c, {}).get("html", ""), True)]
    report.append("final shape disagreements: %s" % ", ".join(diffs))
    for cid in diffs:
        report.append("=== %s\n  ref: %r\n  ftml: %r" %
                      (cid, shape(final[cid].get("output", ""), True)[:400],
                       shape(ftml.get(cid, {}).get("html", ""), True)[:400]))
    return final


def probe_records():
    """Probe cases and the live capture dict, merging both capture batches."""
    cases = {}
    for path in ("probes/probe-map.json", "probes/probe-map2.json"):
        p = ROOT / path
        if p.exists():
            m = json.load(open(p, encoding="utf-8"))
            for cid, rec in m.items():
                cases[cid] = {"id": cid, "source": rec["source"]}
    caps = {}
    for path in ("probes/captures.json", "probes/captures2.json"):
        p = ROOT / path
        if p.exists():
            caps.update(json.load(open(p, encoding="utf-8")))
    return cases, caps


def run_driver_over_probes(report, mode):
    """Run the reference and dumper over probe sources; returns records by id."""
    import subprocess
    cases, caps = probe_records()
    lines = "".join(json.dumps(rec) + "\n" for rec in cases.values())
    ref_root = ROOT.parents[2] / "ref-php" / "harness" / "batch.php"
    dump = ROOT.parent / "rust-dump" / "target" / "release" / "r2para-rust-dump"
    ref_out = subprocess.run(["/usr/bin/php", str(ref_root), mode], input=lines,
                             text=True, capture_output=True, check=True).stdout
    dump_out = subprocess.run([str(dump)], input=lines,
                              text=True, capture_output=True, check=True).stdout
    ref = {r["id"]: r for r in (json.loads(x) for x in ref_out.splitlines() if x.strip())}
    ft = {r["id"]: r for r in (json.loads(x) for x in dump_out.splitlines() if x.strip())}
    return cases, caps, ref, ft


def compare_probes(report):
    cases, caps, ref, ftml = run_driver_over_probes(report, "render")
    valid = {cid: cap for cid, cap in caps.items()
             if cap.get("valid") and cap.get("stable") and cap.get("saved_source_matches")}
    report.append("")
    report.append("LIVE PROBES")
    report.append("probes=%d valid=%d stable=%d source_matches=%d" %
                  (len(caps), sum(1 for c in caps.values() if c.get("valid")),
                   sum(1 for c in caps.values() if c.get("stable")),
                   sum(1 for c in caps.values() if c.get("saved_source_matches"))))
    report.append("Live uses .wdfiles.com and a per-page filename in local--files; both are served-layer and removed by shape().")
    report.append("A trailing sentinel paragraph `<p>x</p>` is part of every probe source; it is kept in the comparison.")

    def live_shape(text, fullname):
        # The live page's own fullname is the file-serving page-name slot;
        # the reference harness gives it an empty name and the dumper uses
        # "some-page", both removed above. Live also inserts one frame newline
        # between adjacent block tags that the pins and both local drivers
        # omit, so remove only that newline (the R2-TABLE frame finding).
        text = shape(text.replace(fullname, "PAGE"), True)
        text = text.replace("local--files/PAGE/", "local--files/")
        text = re.sub(r"(local--(?:files|resized-images))/PAGE/+", r"\1/", text)
        text = re.sub(r">\n<", "><", text)
        text = re.sub(r"\n(?=<p\b)", "", text)
        return text

    before_path = ROOT / "probes" / "ref-probe-render-before.jsonl"
    before = load_jsonl("probes/ref-probe-render-before.jsonl") if before_path.exists() else {}
    before_ok = sum(1 for cid in valid if live_shape(before.get(cid, {}).get("output", ""), valid[cid]["fullname"]) == live_shape(valid[cid].get("html", ""), valid[cid]["fullname"]))
    ref_ok = sum(1 for cid in valid if live_shape(ref.get(cid, {}).get("output", ""), valid[cid]["fullname"]) == live_shape(valid[cid].get("html", ""), valid[cid]["fullname"]))
    ft_ok = sum(1 for cid in valid if live_shape(ftml.get(cid, {}).get("html", ""), valid[cid]["fullname"]) == live_shape(valid[cid].get("html", ""), valid[cid]["fullname"]))
    report.append("before reference vs live (shape): match=%d/%d" % (before_ok, len(valid)))
    report.append("final reference vs live (shape): match=%d/%d" % (ref_ok, len(valid)))
    report.append("ftml dumper vs live (shape): match=%d/%d" % (ft_ok, len(valid)))
    for cid in sorted(valid):
        fullname = valid[cid]["fullname"]
        live = live_shape(valid[cid].get("html", ""), fullname)
        r = live_shape(ref.get(cid, {}).get("output", ""), fullname)
        f = live_shape(ftml.get(cid, {}).get("html", ""), fullname)
        status = "MATCH" if r == live else "DIFF"
        fstatus = "MATCH" if f == live else "DIFF"
        report.append("=== %s ref=%s ftml=%s\n  ref:  %r\n  ftml: %r\n  live: %r" %
                      (cid, status, fstatus, r[:360], f[:360], live[:360]))
    return ref, ftml, valid


def main():
    report = []
    compare_battery(report)
    compare_probes(report)
    out = "\n".join(report) + "\n"
    (ROOT / "compare-report.txt").write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
