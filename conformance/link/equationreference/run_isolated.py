#!/usr/bin/env python3
"""Run a JSONL battery through the reference one case per fresh PHP process.

The ftml dumper and live Wikidot give each page a fresh equation-number
context.  The shared batch.php driver keeps Text_Wiki_Parse_Math::$equationsArray
as a process-static, so batching cases leaks labels and numbers between them.
One process per case restores the same fresh context on the reference side.

Usage: run_isolated.py MODE INPUT.jsonl OUTPUT.jsonl
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / "ref-php" / "harness" / "batch.php"

mode, inp, outp = sys.argv[1], sys.argv[2], sys.argv[3]
cases = [json.loads(line) for line in Path(inp).read_text(encoding="utf-8").splitlines() if line.strip()]
with Path(outp).open("w", encoding="utf-8") as fh:
    for case in cases:
        proc = subprocess.run(
            ["/usr/bin/php", str(BATCH), mode],
            input=json.dumps(case, ensure_ascii=False) + "\n",
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            rec = {"id": case["id"], "error": f"exit={proc.returncode} {proc.stderr.strip()}"}
        else:
            rec = json.loads(proc.stdout.strip())
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"{mode}: {len(cases)} isolated cases -> {outp}")
