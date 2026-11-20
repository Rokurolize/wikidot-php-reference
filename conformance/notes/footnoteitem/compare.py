#!/usr/bin/env python3
"""Compare the reference (before and after correction) and ftml over the
Footnoteitem battery and live probe set. The footnote-item surface is the
<div class="footnote-footer"> segment rendered by Render/Xhtml/Footnoteitem.php.
"""
import json
import re

FOOTER = re.compile(r'<div class="footnote-footer".*?</div>', re.S)


def load(path, key):
    return {d["id"]: (d.get(key) or "") for d in map(json.loads, open(path, encoding="utf-8"))}


def canon(s):
    s = s.replace("&#39;", "'").replace("<br>", "<br />")
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


def footers(s):
    return FOOTER.findall(s)


def battery_numbers(ref, ft, n):
    ids = list(ref)
    return dict(
        n=n,
        whole_raw=sum(ref[i] == ft.get(i, "") for i in ids),
        whole_canon=sum(canon(ref[i]) == canon(ft.get(i, "")) for i in ids),
        footers_both=sum(1 for i in ids if footers(ref[i]) and footers(ft.get(i, ""))),
        footer_raw=sum(footers(ref[i]) == footers(ft.get(i, "")) for i in ids),
        footer_canon=sum([canon(x) for x in footers(ref[i])] == [canon(x) for x in footers(ft.get(i, ""))] for i in ids),
    )


def main():
    ft = load("ftml-dump.jsonl", "html")
    caps = json.load(open("captures.json", encoding="utf-8"))
    ftp = load("ftml-probe-dump.jsonl", "html")
    valid = [c for c in caps if caps[c].get("valid") and footers(caps[c]["html"])]
    print("Footnoteitem R2 differential compare report")
    print("=" * 66)
    print(f"battery cases: {len(ft)}; live captures: {len(caps)} "
          f"(valid/stable/source-matching: {sum(v['valid'] for v in caps.values())}); "
          f"captures with a footnote footer: {len(valid)}")
    for label, path in (("BEFORE", "ref-render-before.jsonl"), ("AFTER", "ref-render-after.jsonl")):
        ref = load(path, "output")
        m = battery_numbers(ref, ft, len(ref))
        print(f"\n{label} battery vs ftml:")
        print(f"  whole-string raw agreement:            {m['whole_raw']}/{m['n']}")
        print(f"  whole-string canonical agreement:      {m['whole_canon']}/{m['n']}")
        print(f"  cases with footers on both sides:      {m['footers_both']}/{m['n']}")
        print(f"  footer-list raw agreement:             {m['footer_raw']}/{m['n']}")
        print(f"  footer-list entity/newline canonical:  {m['footer_canon']}/{m['n']}")
        refp = load(f"ref-probe-{label.lower()}-render.jsonl", "output") if False else load(
            "ref-probe-render-before.jsonl" if label == "BEFORE" else "ref-probe-render-after.jsonl", "output")
        eq_raw = sum(footers(caps[c]["html"]) == footers(refp[c]) for c in valid)
        live_raw_ft = sum(footers(caps[c]["html"]) == footers(ftp[c]) for c in valid)
        live_ent_ft = sum([x.replace("&#39;", "'") for x in footers(caps[c]["html"])] ==
                          [x.replace("&#39;", "'") for x in footers(ftp[c])] for c in valid)
        print(f"  live==reference footer-list raw:       {eq_raw}/{len(valid)}")
        print(f"  live==ftml footer-list raw:            {live_raw_ft}/{len(valid)}")
        print(f"  live==ftml after &#39;->' canonical:    {live_ent_ft}/{len(valid)}")
    # the two live-settled Footnoteitem questions
    raw_q = ent_q = space = nospace = 0
    for c in valid:
        for x in footers(caps[c]["html"]):
            raw_q += "scrollToReference('" in x
            ent_q += "scrollToReference(&#39;" in x
            m = re.search(r"</a>(\.\s*)</div>", x)
            if m:
                space += m.group(1) == ". "
                nospace += m.group(1) == "."
    print("\nLive-settled Footnoteitem questions:")
    print(f"  Q1 onclick quote: raw ' = {raw_q} footers, &#39; entity = {ent_q} footers")
    print(f"  Q2 empty-body separator: '. ' with trailing space = {space}, '.' without = {nospace}")


if __name__ == "__main__":
    main()
