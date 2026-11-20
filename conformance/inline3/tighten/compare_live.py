#!/usr/bin/env python3
"""Compare live saved-page captures against the reference render and ftml dump
for the R2-inline3 Tighten battery.

Two comparisons are made per case.

  ws-sensitive: the live content HTML is compared to the reference/ftml output
    after (a) stripping the reference harness's two trailing newlines and
    inter-block padding, (b) canonicalising <br /> to <br>, and (c) decoding
    numeric character entities. In-text whitespace runs are deliberately NOT
    collapsed here: keeping them is what lets this section rule on the two
    inherited whitespace residuals.

  probe-norm: the campaign-standard wikidot_probe.norm() for both sides. It
    does collapse in-text whitespace and decode entities, so it reports the
    coarse three-way agreement used by the other sections.

Usage: compare_live.py CAPTURES.json [REF_RENDER.jsonl ...]
Writes compare-live.txt in this directory.
"""
import importlib.machinery
import importlib.util
import json
import os
import re
import sys

D = os.path.dirname(os.path.abspath(__file__))

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def load_jsonl(path, key):
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            rows[r["id"]] = r.get(key)
    return rows


def decode_entities(s):
    s = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), s or "")
    return re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), s)


def ws_sensitive(s):
    """Frame-normalize but keep in-text whitespace; decode numeric entities."""
    s = (s or "").replace("<br />", "<br>")
    s = re.sub(r">\s+<", ">\n<", s)
    return decode_entities(s).strip()


def main():
    captures_path = sys.argv[1]
    ref_paths = sys.argv[2:] or [os.path.join(D, "ref-render-after.jsonl")]
    captures = json.load(open(captures_path, encoding="utf-8"))
    dump = load_jsonl(os.path.join(D, "ftml-dump.jsonl"), "html")
    lines = []
    tally = {}
    for ref_path in ref_paths:
        label = os.path.basename(ref_path)
        ref = load_jsonl(ref_path, "output")
        counts = dict(total=0, valid=0, lref_ws=0, lftm_ws=0, lref_norm=0, lftm_norm=0)
        for cid in sorted(captures, key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
            cap = captures[cid]
            live = cap.get("html")
            r, f = ref.get(cid), dump.get(cid)
            counts["total"] += 1
            if cap.get("valid"):
                counts["valid"] += 1
            lr_ws = ws_sensitive(live) == ws_sensitive(r)
            lf_ws = ws_sensitive(live) == ws_sensitive(f)
            lr_n = probe.norm(live) == probe.norm(r)
            lf_n = probe.norm(live) == probe.norm(f)
            counts["lref_ws"] += lr_ws
            counts["lftm_ws"] += lf_ws
            counts["lref_norm"] += lr_n
            counts["lftm_norm"] += lf_n
            lines.append(
                f"{label} {cid} | valid={cap.get('valid')} stable={cap.get('stable')} "
                f"srcmatch={cap.get('saved_source_matches')} | "
                f"ws(live==ref)={lr_ws} ws(live==ftml)={lf_ws} | "
                f"norm(live==ref)={lr_n} norm(live==ftml)={lf_n}"
            )
            if not (lr_ws and lf_ws):
                lines.append(f"  LIVE: {json.dumps(live, ensure_ascii=False)[:300]}")
                lines.append(f"  REF : {json.dumps(r, ensure_ascii=False)[:300]}")
                lines.append(f"  FTML: {json.dumps(f, ensure_ascii=False)[:300]}")
        tally[label] = counts
        lines.append(f"SUMMARY {label}: {counts}")
        lines.append("")
    text = "\n".join(lines) + "\n"
    with open(os.path.join(D, "compare-live.txt"), "w", encoding="utf-8") as fh:
        fh.write(text)
    for k, v in tally.items():
        print(f"SUMMARY {k}: {v}")
    print(f"wrote {len(lines)} lines to compare-live.txt")


if __name__ == "__main__":
    main()
