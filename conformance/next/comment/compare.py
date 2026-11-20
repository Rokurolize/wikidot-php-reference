#!/usr/bin/env python3
"""Side-by-side report for the R2-next Comment differential.

Reads the local battery, the before/after reference renders, the ftml dumper
outputs and the frozen live captures, then prints counts and the cases in
each disagreement class. Two normalizations are used: a mild one for live
probe grouping (newline padding, <br /> vs <br>, typography entities,
whitespace runs) and a structural one that drops whitespace entirely so only
Comment-owned text differences count as substantive. The script never edits
any input file and makes no claim about rules it does not own.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def by_id(rows, key="output"):
    return {row["id"]: row.get(key, "") for row in rows}


def mild(html):
    if html is None:
        return ""
    text = str(html)
    text = text.replace("<br />", "<br>").replace("&#8212;", "\u2014")
    text = text.replace("&#32;", " ").replace("&#39;", "'")
    text = text.replace("&quot;", '"').replace("&amp;", "&")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def structural(html):
    return re.sub(r"\s+", "", mild(html))


def main():
    battery = load("battery.jsonl")
    before = by_id(load("ref-render-before.jsonl"))
    after = by_id(load("ref-render-after.jsonl"))
    ftml = by_id(load("ftml-dump.jsonl"), "html")
    probes = load("probe-cases.jsonl")
    p_before = by_id(load("ref-probe-render-before.jsonl"))
    p_after = by_id(load("ref-probe-render-after.jsonl"))
    p_ftml = by_id(load("ftml-probe-dump.jsonl"), "html")
    with open(os.path.join(HERE, "captures.json"), encoding="utf-8") as fh:
        live = json.load(fh)

    raw_changed = [row["id"] for row in battery if before[row["id"]] != after[row["id"]]]
    exact, substantive = [], []
    for row in battery:
        cid = row["id"]
        if structural(after[cid]) == structural(ftml[cid]):
            exact.append(cid)
        else:
            substantive.append(cid)

    valid = [cid for cid in p_after if live.get(cid, {}).get("valid")]
    classes = {"all3": [], "ref_live": [], "ftml_live": [], "all_disagree": []}
    for cid in valid:
        r, f, l = mild(p_after[cid]), mild(p_ftml[cid]), mild(live[cid]["html"])
        if r == f == l:
            classes["all3"].append(cid)
        elif r == l and f != l:
            classes["ref_live"].append(cid)
        elif f == l and r != l:
            classes["ftml_live"].append(cid)
        else:
            classes["all_disagree"].append(cid)

    print("battery cases:", len(battery), "probes:", len(probes), "valid captures:", len(valid))
    print("raw render changes:", len(raw_changed), raw_changed)
    print("battery after: structurally equal to ftml", len(exact), "substantive", len(substantive))
    print("battery substantive:", substantive)
    for name, ids in classes.items():
        print("probes", name, len(ids), ids)
    print("probe raw changes:", [cid for cid in valid if p_before[cid] != p_after[cid]])
    for cid in substantive:
        print("\nSUB", cid)
        print(" REF    ", repr(before[cid]), "->", repr(after[cid]))
        print(" FTML   ", repr(ftml[cid]))
    for cid in classes["all_disagree"]:
        print("\nPROBE", cid)
        print(" REF   ", repr(p_after[cid]))
        print(" FTML  ", repr(p_ftml[cid]))
        print(" LIVE  ", repr(live[cid]["html"]))


if __name__ == "__main__":
    main()
