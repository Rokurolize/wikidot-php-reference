#!/usr/bin/env python3
"""Three-way comparison of live captures, reference render, and ftml dumper on the live probe set.

For each probe id pNN the live side comes from captures.json, the reference from
ref-probe-render-<variant>.jsonl (id nlp-pNN), and ftml from ftml-probe-dump.jsonl
(id nlp-pNN). Reports exact HTML and a frame-normalized form that factors out the
inter-block newline and the <br />/<br> spelling surface, plus which side each agrees
with. Writes compare-report.txt in this directory and prints it.
"""
import json, os, re, sys

D = os.path.dirname(os.path.abspath(__file__))
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "before"


def load(path, idkey="id", valkey="output"):
    out = {}
    with open(os.path.join(D, path), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            out[r[idkey]] = r.get(valkey)
    return out


def norm(s):
    s = s.replace("<br />", "<br>")
    s = re.sub(r">\s+<", "><", s)  # drop frame inter-block whitespace entirely
    return s.strip()


def main():
    live = json.load(open(os.path.join(D, "captures.json"), encoding="utf-8"))
    ref = load("ref-probe-render-%s.jsonl" % VARIANT)
    ftml = load("ftml-probe-dump.jsonl", valkey="html")
    lines = ["VARIANT %s" % VARIANT]
    counts = {"all3": 0, "ref_live": 0, "ftml_live": 0, "ref_ftml": 0, "all_disagree": 0}
    for cid in sorted(live):
        lh = live[cid]["html"]
        rh = ref.get("nlp-" + cid)
        fh = ftml.get("nlp-" + cid)
        rmatch, fmatch = (rh == lh), (fh == lh)
        if rmatch and fmatch:
            tag = "all3"
        elif rmatch:
            tag = "ref_live"
        elif fmatch:
            tag = "ftml_live"
        elif rh == fh:
            tag = "ref_ftml"
        else:
            tag = "all_disagree"
        counts[tag] += 1
        lines.append("PROBE %s [%s] valid=%s stable=%s srcmatch=%s" % (
            cid, tag, live[cid]["valid"], live[cid]["stable"], live[cid]["saved_source_matches"]))
        lines.append("  src  =%s" % json.dumps(live[cid]["source"]))
        lines.append("  live =%s" % json.dumps(lh))
        lines.append("  ref  =%s" % json.dumps(rh))
        lines.append("  ftml =%s" % json.dumps(fh))
        lines.append("  nlive=%s" % json.dumps(norm(lh)))
        lines.append("  nref =%s" % json.dumps(norm(rh or "")))
        lines.append("  nftml=%s" % json.dumps(norm(fh or "")))
    lines.append("COUNTS %s" % json.dumps(counts))
    text = "\n".join(lines) + "\n"
    open(os.path.join(D, "compare-report.txt"), "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
