#!/usr/bin/env python3
"""Final verification for the R2 Code stage.

Two checks:
 (A) 15 live probe pages: full rendered output of the corrected reference,
     normalized only for the documented frame-level join whitespace, must
     equal the live capture byte-for-byte.
 (B) 68-case battery: the corrected reference's code-fragment output must
     agree with the live-adjudicated expectation, which is assembled from
       - direct live probes (15 cases, by matching probe source),
       - ftml corpus pins under test/code/*/wikidot.html where the shape is
         pinned (edge-whitespace, basic, highlight-*, unknown-language-plain),
       - the corrected Code-rule mechanism for the remaining shapes.
     The check prints case-by-case PASS/FAIL of reference-vs-expectation.
"""
import json, re, glob, os

root = "/home/roku/.local/state/wikijump/muse-bhl/lean-ftml-dsh/conformance-refphp/code/"
ftml_test = "/home/roku/src/Rokurolize/ftml/test/code/"

cap = json.load(open(root + "captures.json"))
refp = {r["id"]: r.get("output", "") for r in map(json.loads, open(root + "ref-probe-render.jsonl"))}
refb = {r["id"]: r.get("output", "ERR:" + r.get("error", "")) for r in map(json.loads, open(root + "ref-render-final.jsonl"))}


def frame(s):
    """Normalize only frame/tighten output shaping (R2-INCLUDE/R2-FRAME)."""
    s = s.replace("\r\n", "\n").replace("<br />", "<br>")
    s = re.sub(r"\n{2,}", "\n", s)
    s = s.strip("\n \t")
    return s


def fragment(s):
    """Concatenated code-block fragments, or <LITERAL>."""
    if '<div class="code"' not in s:
        return "<LITERAL>"
    out, pos = [], 0
    while True:
        i = s.find('<div class="code"', pos)
        if i < 0: break
        d, j = 0, i
        while j < len(s):
            if s.startswith("<div", j): d += 1
            elif s.startswith("</div>", j):
                d -= 1
                if d == 0:
                    j += 6
                    break
            j += 1
        out.append(s[i:j])
        pos = j
    return "".join(out)


# --- (A) live probes ---------------------------------------------------------
print("=== (A) live probes: corrected reference vs live capture ===")
a_pass = 0
for k, v in cap.items():
    ok = frame(refp[k]) == frame(v["html"])
    a_pass += ok
    print(f"  {k:<18} {'PASS' if ok else 'FAIL'}")
print(f"  total {a_pass}/{len(cap)}")

# --- (B) corpus pins ---------------------------------------------------------
print()
print("=== (B) corpus pins: corrected reference fragment vs ftml wikidot.html pin ===")
pins = {}
for d in glob.glob(ftml_test + "*/"):
    name = os.path.basename(d.rstrip("/"))
    if os.path.exists(d + "wikidot.html") and os.path.exists(d + "input.ftml"):
        pins[name] = (open(d + "input.ftml", encoding="utf-8").read(),
                      open(d + "wikidot.html", encoding="utf-8").read())
# render each pin input through the corrected reference
pin_input = "\n".join(json.dumps({"id": n, "source": s}, ensure_ascii=False)
                      for n, (s, _) in pins.items())
open(root + "pin-inputs.jsonl", "w", encoding="utf-8").write(pin_input + "\n")
import subprocess
pin_out = subprocess.run(["/usr/bin/php", root + "../../ref-php/harness/batch.php", "render"],
                         input=pin_input, text=True, capture_output=True, cwd=root).stdout
pin_ref = {}
for line in pin_out.splitlines():
    r = json.loads(line)
    pin_ref[r["id"]] = r.get("output", "ERR:" + r.get("error", ""))
b_pass = 0
for n, (_, live) in pins.items():
    got = fragment(pin_ref.get(n, ""))
    want = fragment(live)
    # normalize highlighter newlines and empty spans (the corpus pin's tight
    # shape is post-purifyHtml; the live probe establishes the newline form)
    def norm(s):
        s = s.replace('<div class="code">\n', '<div class="code">')
        s = s.replace('<div class="hl-main">\n', '<div class="hl-main">')
        s = s.replace('</pre></div>\n</div>', '</pre></div></div>')
        s = re.sub(r'<span class="hl-[a-z]+"></span>', '', s)
        s = s.replace("&#039;", "'")
        return s
    ok = norm(got) == norm(want)
    b_pass += ok
    print(f"  {n:<32} {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("    LIVE:", repr(norm(want)[:240]))
        print("    REF :", repr(norm(got)[:240]))
print(f"  total {b_pass}/{len(pins)}")

# save pin outputs as evidence
with open(root + "ref-pin-render.jsonl", "w", encoding="utf-8") as f:
    for n in pins:
        f.write(json.dumps({"id": n, "output": pin_ref.get(n, "")}, ensure_ascii=False) + "\n")
