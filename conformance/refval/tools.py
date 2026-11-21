#!/usr/bin/env python3
"""Shared tooling for Mission REFVAL."""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-antigravity-refval")
PHP = "/usr/bin/php"
BATCH_PHP = ROOT / "ref-php/harness/batch.php"
PROBE_DIR = Path.home() / ".agents/skills/wikidot-py-operations"
SMOKE_JSONL = ROOT / "refval/smoke.jsonl"
SMOKE_BASE = ROOT / "refval/smoke-baseline.jsonl"


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def run_batch(cases_path, out_path, mode="render"):
    err_path = str(out_path) + ".err"
    with open(cases_path, "rb") as fin, open(out_path, "wb") as fout, open(err_path, "wb") as ferr:
        res = subprocess.run([PHP, str(BATCH_PHP), mode], stdin=fin, stdout=fout, stderr=ferr)
    if res.returncode != 0:
        raise RuntimeError(f"batch.php failed with rc={res.returncode}")
    return out_path, err_path


def check_smoke():
    out = ROOT / "refval/smoke-check.jsonl"
    run_batch(SMOKE_JSONL, out, "render")
    base_bytes = SMOKE_BASE.read_bytes()
    cur_bytes = out.read_bytes()
    if base_bytes == cur_bytes:
        return True, []
    base = {r["id"]: r for r in load_jsonl(SMOKE_BASE)}
    cur = {r["id"]: r for r in load_jsonl(out)}
    diffs = []
    for k in sorted(set(base) | set(cur)):
        if base.get(k) != cur.get(k):
            diffs.append((k, base.get(k), cur.get(k)))
    return False, diffs


def validate_captures(captures_path):
    caps = json.load(open(captures_path, encoding="utf-8"))
    bad = []
    for cid, rec in caps.items():
        if not (rec.get("valid") is True and rec.get("stable") is True and rec.get("saved_source_matches") is True):
            bad.append((cid, rec.get("valid"), rec.get("stable"), rec.get("saved_source_matches")))
    return len(caps), bad


def frame_norm(html):
    """Minimal documented framing normalization for classifying Stage 2/pretty-print differences."""
    s = html.strip()
    # Normalize CRLF
    s = s.replace("\r\n", "\n")
    # Collapse runs of whitespace between tags only if needed - actually keep strict!
    # Just normalize <br> vs <br /> and <hr> vs <hr /> and trailing/inter-block newlines for diagnostics
    s = re.sub(r"<br\s*/?>", "<br />", s)
    s = re.sub(r"<hr\s*/?>", "<hr />", s)
    s = re.sub(r"\n+", "\n", s)
    return s.strip()


def compare_rule(rule_dir, render_jsonl, captures_json, out_txt):
    renders = {r["id"]: r for r in load_jsonl(render_jsonl)}
    captures = json.load(open(captures_json, encoding="utf-8"))
    lines = []
    exact = 0
    trim_eq = 0
    fnorm_eq = 0
    diffs = []
    for cid, cap in captures.items():
        live_html = cap["html"]
        ref_rec = renders.get(cid)
        if ref_rec is None:
            diffs.append((cid, "MISSING_IN_REF", live_html, None))
            continue
        if "error" in ref_rec:
            diffs.append((cid, "REF_ERROR", live_html, ref_rec["error"]))
            continue
        ref_html = ref_rec["output"]
        if ref_html == live_html:
            exact += 1
            trim_eq += 1
            fnorm_eq += 1
            lines.append(f"EXACT     {cid} ({cap['fullname']})")
        elif ref_html.strip() == live_html.strip():
            trim_eq += 1
            fnorm_eq += 1
            lines.append(f"TRIM_EQ   {cid} ({cap['fullname']})")
            lines.append(f"  REF : {ref_html!r}")
            lines.append(f"  LIVE: {live_html!r}")
        elif frame_norm(ref_html) == frame_norm(live_html):
            fnorm_eq += 1
            lines.append(f"FNORM_EQ  {cid} ({cap['fullname']})")
            lines.append(f"  REF : {ref_html!r}")
            lines.append(f"  LIVE: {live_html!r}")
        else:
            diffs.append((cid, "DIFF", live_html, ref_html))
            lines.append(f"DIFF      {cid} ({cap['fullname']})")
            lines.append(f"  SRC : {cap['source']!r}")
            lines.append(f"  REF : {ref_html!r}")
            lines.append(f"  LIVE: {live_html!r}")
    summary = f"Total={len(captures)} exact={exact} trim_eq={trim_eq} fnorm_eq={fnorm_eq} diffs={len(diffs)}"
    text = summary + "\n" + "\n".join(lines) + "\n"
    Path(out_txt).write_text(text, encoding="utf-8")
    return summary, diffs
