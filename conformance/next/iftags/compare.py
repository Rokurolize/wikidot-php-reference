#!/usr/bin/env python3
"""Three-way view for the R2-next Iftags differential.

Reads the battery and probe JSONL inputs, the before/after reference renders,
the shared ftml dumper outputs and the frozen live captures, then reports
agreements and disagreements on two surfaces. `strict` compares the raw
render strings after only JSON unescaping; `canon` additionally normalizes
frame-level surface owned by later rules (<br /> vs <br>, whitespace runs,
inter-block spaces, stray space before '>' and the odate/iframe/date/math
serving-layer wrappers) so that gate ownership is compared rather than glue.
The script is read-only and prints flowing single-line prose.
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent


def load(name):
    return [json.loads(line) for line in (HERE / name).open(encoding="utf-8") if line.strip()]


def by_id(rows, key="output"):
    return {row["id"]: row.get(key) for row in rows}


def unescape(text):
    if text is None:
        return None
    return text.replace("\\/", "/")


def canon(text):
    if text is None:
        return None
    text = unescape(text)
    text = text.replace("<br />", "<br>")
    text = re.sub(r"\s+/>", "/>", text)
    text = re.sub(r"\s+>", ">", text)
    text = re.sub(r"</p>\s+<", "</p><", text)
    text = re.sub(r"</div>\s+<", "</div><", text)
    text = re.sub(r"\s+", " ", text).strip()
    # serving-layer wrappers owned by later rules are masked to their payload
    text = re.sub(r'<span class="odate[^"]*">([^<]*)</span>', r"\1", text)
    text = re.sub(r'<div class="math-equation"[^>]*>(.*?)</div>', r"\1", text)
    text = re.sub(r'<span class="equation-number">[^<]*</span>', "", text)
    text = re.sub(r'<div class="error-block">.*?</div>', "ERRORBLOCK", text)
    return text


def has_keep(text):
    return "KEEP" in (text or "")


def main():
    battery = load("battery.jsonl")
    rb = by_id(load("ref-render-before.jsonl"))
    ra = by_id(load("ref-render-after.jsonl"))
    ftml = {r["id"]: r["html"] for r in load("ftml-dump.jsonl")}
    strict_same_before = sum(1 for c in battery if unescape(rb[c["id"]]) == ftml[c["id"]])
    strict_same_after = sum(1 for c in battery if unescape(ra[c["id"]]) == ftml[c["id"]])
    canon_same_before = sum(1 for c in battery if canon(rb[c["id"]]) == canon(ftml[c["id"]]))
    canon_same_after = sum(1 for c in battery if canon(ra[c["id"]]) == canon(ftml[c["id"]]))
    changed = [c["id"] for c in battery if rb[c["id"]] != ra[c["id"]]]
    substantive = [c["id"] for c in battery if canon(ra[c["id"]]) != canon(ftml[c["id"]])]
    print(f"BATTERY cases={len(battery)} strict_agreement_before={strict_same_before} strict_agreement_after={strict_same_after}")
    print(f"BATTERY canon_agreement_before={canon_same_before} canon_agreement_after={canon_same_after} corrected_outputs={len(changed)} corrected_ids={changed}")
    print(f"BATTERY canon_disagreements_after={len(substantive)} ids={substantive}")
    for cid in substantive:
        print(f"  {cid}: ref={canon(ra[cid])!r} ftml={canon(ftml[cid])!r}")
    probes = load("probe-cases.jsonl")
    prb = by_id(load("ref-probe-render-before.jsonl"))
    pra = by_id(load("ref-probe-render-after.jsonl"))
    pftml = {r["id"]: r["html"] for r in load("ftml-probe-dump.jsonl")}
    caps = {k: v for k, v in json.load((HERE / "captures.json").open(encoding="utf-8")).items()}
    live = {k: v["html"] for k, v in caps.items()}
    valid = [k for k in live if caps[k].get("valid")]
    tally = {"all3": [], "ref_live": [], "ftml_live": [], "none": []}
    for cid in valid:
        r, f, l = canon(pra[cid]), canon(pftml[cid]), canon(live[cid])
        er, ef = r == l, f == l
        if er and ef:
            tally["all3"].append(cid)
        elif er:
            tally["ref_live"].append(cid)
        elif ef:
            tally["ftml_live"].append(cid)
        else:
            tally["none"].append(cid)
    print(f"PROBES total={len(probes)} valid={len(valid)} all3={len(tally['all3'])} ref+live={len(tally['ref_live'])} ftml+live={len(tally['ftml_live'])} none={len(tally['none'])}")
    for group, ids in tally.items():
        print(f"  {group}: {ids}")
    print("PROBE GATE POLARITIES (KEEP present or absent)")
    for cid in valid:
        print(f"  {cid}: ref={has_keep(pra[cid])} ftml={has_keep(pftml[cid])} live={has_keep(live[cid])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
