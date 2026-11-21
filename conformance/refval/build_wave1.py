#!/usr/bin/env python3
"""Build Wave 1 batteries and probe sets for Horiz, Break, Center, Separator, Clearfloat."""
import json
import os
from pathlib import Path
from tools import ROOT, load_jsonl, save_jsonl, run_batch

r315_cases = load_jsonl(ROOT / "materials/conformance-r315/middle-all-cases.jsonl")
r315_prov = json.load(open(ROOT / "materials/conformance-r315/corpus-provenance.json", encoding="utf-8"))


def extract_r315(prefix, rule_name):
    out = []
    seen = set()
    for c in r315_cases:
        cid = c["id"]
        if cid.startswith(prefix) or (r315_prov.get(cid, {}).get("kind") == "canonical" and rule_name in r315_prov[cid].get("detail", "")):
            if cid not in seen:
                seen.add(cid)
                out.append({"id": cid, "source": c["source"]})
    return out


def write_rule(name, base_cases, extra_cases, probe_specs):
    """probe_specs: list of (probe_id, source) — all probe_ids also included in battery if not already present."""
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
        # Ensure probe sources have no trailing newline or lone CR that Wikidot save strips/normalizes
        assert not src.endswith("\n") and not src.endswith(" ") and "\r" not in src, f"probe {name}/{pid} has unsafe end/CR: {src!r}"
        probes.append({"id": pid, "source": src})
        if pid not in seen:
            seen.add(pid)
            battery.append({"id": pid, "source": src})
    save_jsonl(rdir / "battery.jsonl", battery)
    save_jsonl(rdir / "probes.jsonl", probes)
    run_batch(rdir / "battery.jsonl", rdir / "ref-render-before.jsonl", "render")
    print(f"{name:12s}: battery={len(battery)} probes={len(probes)}")


# 1. HORIZ
hz_base = extract_r315("hz-", "Horiz")
hz_extra = [
    ("hz-x01", "[[div]]\n----\n[[/div]]"),
    ("hz-x02", "[[note]]\n----\n[[/note]]"),
    ("hz-x03", "[[=]]\n----\n[[/=]]"),
    ("hz-x04", "[[collapsible]]\n----\n[[/collapsible]]"),
    ("hz-x05", "x\n————\n––––\ny"),
    ("hz-x06", "[[toc]]----\n\n+ A"),
    ("hz-x07", "[[tabview]]\n[[tab T]]\n----\n[[/tab]]\n[[/tabview]]"),
    ("hz-x08", "[[span]]----[[/span]]\n[[a href=\"/x\"]]\n----\n[[/a]]"),
]
hz_probes = [
    ("p01", "----"),
    ("p02", "x\n----\ny"),
    ("p03", "x\n-----\n----------\ny"),
    ("p04", "x\n---\n--\n-\ny"),
    ("p05", "x\n---- \ny"),
    ("p06", "x\n----\t\ny"),
    ("p07", "x\n ----\ny"),
    ("p08", "x\n----x\nx----\na ---- b\n- - - -\ny"),
    ("p09", "----\n----"),
    ("p10", "----\n\n----"),
    ("p11", "* one\n----\n* two"),
    ("p12", "|| a || b ||\n----\n|| c || d ||"),
    ("p13", "+ Head\n----\nx"),
    ("p14", "> quote\n----\nx"),
    ("p15", "[[div]]\n----\n[[/div]]"),
    ("p16", "[[code]]\n----\n[[/code]]\n@@\n----\n@@\nx"),
    ("p17", "**a\n----\nb**\nx"),
    ("p18", "x\n————\n––––\ny"),
]
write_rule("horiz", hz_base, hz_extra, hz_probes)

# 2. BREAK
br_base = extract_r315("br-", "Break")
br_extra = [
    ("br-x01", "a _\nb"),
    ("br-x02", "a _"),
    ("br-x03", "a _ \nb"),
    ("br-x04", "a\t_\nb"),
    ("br-x05", "a _ _\nb"),
    ("br-x06", "a  _\nb"),
    ("br-x07", "a _\n _\n _\nb"),
    ("br-x08", "a _\n\nb"),
    ("br-x09", "a__\n_\na _x\nb"),
    ("br-x10", " _\nb"),
    ("br-x11", "[[div]]\na _\nb\n[[/div]]"),
    ("br-x12", "[[note]]\na _\nb\n[[/note]]"),
    ("br-x13", "[[=]]\na _\nb\n[[/=]]"),
    ("br-x14", "[[a href=\"/x\"]]a _\nb[[/a]]"),
    ("br-x15", "[[span]]a _\nb[[/span]]"),
    ("br-x16", "**a _\nb**"),
]
br_probes = [
    ("p01", "a _\nb"),
    ("p02", "a _"),
    ("p03", "a _ \nb"),
    ("p04", "a\t_\nb"),
    ("p05", "a _ _\nb"),
    ("p06", "a  _\nb"),
    ("p07", "a _\n _\n _\nb"),
    ("p08", "a _\n\nb"),
    ("p09", "a__\n_\na _x\nb"),
    ("p10", " _\nb"),
    ("p11", "* mango _\nmelon _\npineapple\n* pear"),
    ("p12", "|| Apple _\nBanana || Cherry_ || _Pineapple _\n _\n _\nMelon ||"),
    ("p13", "+ head _\nx"),
    ("p14", "> a _\n> b"),
    ("p15", "**a _\nb**\n[[span]]c _\nd[[/span]]"),
    ("p16", "[[div]]\na _\nb\n[[/div]]"),
    ("p17", "a _\n----\nb"),
    ("p18", "x\n= a _\nb\ny"),
]
write_rule("break", br_base, br_extra, br_probes)

# 3. CENTER
ce_base = extract_r315("ce-", "Center")
ce_extra = [
    ("ce-x01", "= hello"),
    ("ce-x02", "= hello\ny"),
    ("ce-x03", "x\n= hello"),
    ("ce-x04", "x\n= a\n= b\ny"),
    ("ce-x05", "x\n= a\n= b\n= c\ny"),
    ("ce-x06", "x\n= \ny"),
]
ce_probes = [
    ("p01", "= hello"),
    ("p02", "= hello\ny"),
    ("p03", "x\n= hello"),
    ("p04", "x\n= hello\ny"),
    ("p05", "x\n= hello =\ny"),
    ("p06", "x\n= a = b\ny"),
    ("p07", "x\n= \ny"),
    ("p08", "x\n=  padded\ny"),
    ("p09", "x\n = hello\n== hello\n=hello\nx= hello\ny"),
    ("p10", "x\n= a\n= b\ny"),
    ("p11", "x\n= a\n= b\n= c\ny"),
    ("p12", "x\n= a\n\n= b\ny"),
    ("p13", "x\n= **bold** //italic// http://example.com\ny"),
    ("p14", "[[div]]\n= centered\n[[/div]]"),
    ("p15", "> quote\n= a\nx"),
    ("p16", "* item\n= a\nx"),
    ("p17", "[[code]]\n= a\n[[/code]]\nx"),
    ("p18", "x\n= a _\nb\ny"),
]
write_rule("center", ce_base, ce_extra, ce_probes)

# 4. SEPARATOR
sep_base = extract_r315("sep-", "Separator")
sep_extra = [
    ("sep-x01", "x\n====\ny"),
    ("sep-x02", "x\n=====\n==========\ny"),
    ("sep-x03", "x\n===\n==\n=\ny"),
    ("sep-x04", "x\n==== \ny"),
    ("sep-x05", "x\n ====\ny"),
    ("sep-x06", "x\n====x\nx====\na ==== b\n= = = =\ny"),
    ("sep-x07", "x\n= ====\ny"),
    ("sep-x08", "= ===="),
    ("sep-x09", "x\n==== =\ny"),
    ("sep-x10", "====\n===="),
    ("sep-x11", "====\n\n===="),
    ("sep-x12", "----\n====\nx"),
    ("sep-x13", "[[div]]\n====\n[[/div]]"),
    ("sep-x14", "[[note]]\n====\n[[/note]]"),
    ("sep-x15", "[[=]]\n====\n[[/=]]"),
    ("sep-x16", "[[collapsible]]\n====\n[[/collapsible]]"),
    ("sep-x17", "* item\n====\n* item2"),
    ("sep-x18", "|| a ||\n====\n|| b ||"),
    ("sep-x19", "> quote\n====\nx"),
    ("sep-x20", "a _\n====\nb"),
    ("sep-x21", "[[toc]]====\n\n+ H"),
]
sep_probes = [
    ("p01", "===="),
    ("p02", "x\n====\ny"),
    ("p03", "x\n=====\n==========\ny"),
    ("p04", "x\n===\n==\n=\ny"),
    ("p05", "x\n==== \ny"),
    ("p06", "x\n ====\ny"),
    ("p07", "x\n====x\nx====\na ==== b\n= = = =\ny"),
    ("p08", "x\n= ====\ny"),
    ("p09", "= ===="),
    ("p10", "x\n==== =\ny"),
    ("p11", "====\n===="),
    ("p12", "====\n\n===="),
    ("p13", "----\n====\nx"),
    ("p14", "[[div]]\n====\n[[/div]]"),
    ("p15", "* item\n====\n* item2"),
    ("p16", "|| a ||\n====\n|| b ||"),
    ("p17", "[[code]]\n====\n[[/code]]\n@@\n====\n@@\nx"),
    ("p18", "a _\n====\nb"),
]
write_rule("separator", sep_base, sep_extra, sep_probes)

# 5. CLEARFLOAT
cf_base = extract_r315("cf-", "Clearfloat")
cf_extra = [
    ("cf-x01", "x\n~~~~\ny"),
    ("cf-x02", "x\n~~~~>\ny"),
    ("cf-x03", "x\n~~~~<\ny"),
    ("cf-x04", "~~~~~>\n~~~~~~<\n~~~~~~~~~~"),
    ("cf-x05", "x\n~~~\n~~\n~\ny"),
    ("cf-x06", "x\n~~~~>>\n~~~~><\n~~~~>x\ny"),
    ("cf-x07", "x\n~~~~ >\n~~~~> \n~~~~ \n ~~~~\ny"),
    ("cf-x08", "~~~~\n~~~~<"),
    ("cf-x09", "~~~~>\n\n~~~~"),
    ("cf-x10", "[[div]]\n~~~~>\n[[/div]]"),
    ("cf-x11", "[[note]]\n~~~~\n[[/note]]"),
    ("cf-x12", "[[=]]\n~~~~<\n[[/=]]"),
    ("cf-x13", "* item\n~~~~\n* item2"),
    ("cf-x14", "|| a ||\n~~~~\n|| b ||"),
    ("cf-x15", "a _\n~~~~\nb"),
]
cf_probes = [
    ("p01", "~~~~"),
    ("p02", "~~~~>"),
    ("p03", "~~~~<"),
    ("p04", "x\n~~~~\ny"),
    ("p05", "x\n~~~~>\ny"),
    ("p06", "x\n~~~~<\ny"),
    ("p07", "~~~~~>\n~~~~~~<\n~~~~~~~~~~"),
    ("p08", "x\n~~~\n~~\n~\ny"),
    ("p09", "x\n~~~~>>\n~~~~><\n~~~~>x\ny"),
    ("p10", "x\n~~~~ >\n~~~~> \n~~~~ \n ~~~~\ny"),
    ("p11", "~~~~\n~~~~<"),
    ("p12", "~~~~>\n\n~~~~"),
    ("p13", "[[toc]]~~~~\n\n+ A"),
    ("p14", "[[div]]\n~~~~>\n[[/div]]"),
    ("p15", "* item\n~~~~\n* item2"),
    ("p16", "|| a ||\n~~~~\n|| b ||"),
    ("p17", "[[code]]\n~~~~\n[[/code]]\n@@\n~~~~\n@@\nx"),
    ("p18", "a _\n~~~~\nb"),
]
write_rule("clearfloat", cf_base, cf_extra, cf_probes)
