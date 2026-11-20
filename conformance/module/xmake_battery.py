#!/usr/bin/env python3
"""Generate the root-owned cross-rule interaction battery for the R2 module stage.

This battery covers interactions the per-rule batteries cannot own: Modulepre's
early tokenization of module654 blocks versus Module654's own matching, a module654
block whose body contains a [[module]] block, a [[module]] block whose body contains
module654 syntax, and the [[/module]] versus [[/module654]] closer policy. Unknown
module names are used so the observable shape is the live error block rather than
serving-layer module evaluation (out of scope for this stage).
"""
import json

U = "UnknownModuleX"
U2 = "AnotherUnknownY"

cases = [
    # 1. A block both Modulepre and Module654 could claim.
    ("x-both-plain", f"[[module654 {U}]]\n"),
    ("x-both-body", f"[[module654 {U}]]\nbody\n[[/module]]\n"),
    ("x-both-empty-body", f"[[module654 {U}]]\n[[/module]]\n"),
    ("x-both-attr", f'[[module654 {U} foo="bar"]]\nbody\n[[/module]]\n'),
    ("x-both-no-newline", f"[[module654 {U}]]tail\n"),
    ("x-both-crlf", f"[[module654 {U}]]\r\nbody\r\n[[/module]]\r\n"),
    ("x-both-spaces-newline", f"[[module654 {U}]]   \nbody\n[[/module]]\n"),
    ("x-both-leading-space", f" [[module654 {U}]]\nbody\n[[/module]]\n"),
    # module form of the same block, for the contrast.
    ("x-mod-plain", f"[[module {U}]]\n"),
    ("x-mod-body", f"[[module {U}]]\nbody\n[[/module]]\n"),
    ("x-mod-attr", f'[[module {U} foo="bar"]]\nbody\n[[/module]]\n'),

    # 2. A module654 block whose body contains a [[module]] block.
    ("x-654-body-module", f"[[module654 {U}]]\nbefore\n[[module {U2}]]\ninner\n[[/module]]\nafter\n[[/module]]\n"),
    ("x-654-body-module-attr", f'[[module654 {U} a="1"]]\n[[module {U2} b="2"]]\ninner\n[[/module]]\n[[/module]]\n'),
    ("x-654-body-module-noclose", f"[[module654 {U}]]\n[[module {U2}]]\ninner\n[[/module]]\n"),

    # 3. A [[module]] block whose body contains module654 syntax.
    ("x-mod-body-654", f"[[module {U}]]\nbefore\n[[module654 {U2}]]\ninner\n[[/module]]\nafter\n[[/module]]\n"),
    ("x-mod-body-654-noinnerclose", f"[[module {U}]]\nbefore\n[[module654 {U2}]]\ninner\n[[/module]]\n"),
    ("x-mod-body-654-inline", f"[[module {U}]]\n[[module654 {U2}]]tail[[/module]]\n[[/module]]\n"),

    # 4. Closer policy: [[/module654]] versus [[/module]].
    ("x-close-654-tag", f"[[module654 {U}]]\nbody\n[[/module654]]\n"),
    ("x-close-mod-tag", f"[[module {U}]]\nbody\n[[/module654]]\n"),
    ("x-close-both", f"[[module654 {U}]]\nbody\n[[/module654]]\n[[/module]]\n"),
    ("x-close-stray-654", f"stray [[/module654]] after\n"),

    # 5. Nested module654 in module654 (Modulepre rewrite then Module nesting defense).
    ("x-654-in-654", f"[[module654 {U}]]\nouter\n[[module654 {U2}]]\ninner\n[[/module]]\n[[/module]]\n"),
    ("x-mod-in-mod", f"[[module {U}]]\nouter\n[[module {U2}]]\ninner\n[[/module]]\n[[/module]]\n"),

    # 6. Adjacency and mid-line seams.
    ("x-adjacent-654-mod", f"[[module654 {U}]]\na\n[[/module]]\n[[module {U2}]]\nb\n[[/module]]\n"),
    ("x-adjacent-mod-654", f"[[module {U}]]\na\n[[/module]]\n[[module654 {U2}]]\nb\n[[/module]]\n"),
    ("x-midline-654", f"prefix [[module654 {U}]]\nbody\n[[/module]]\n"),
    ("x-midline-mod", f"prefix [[module {U}]]\nbody\n[[/module]]\n"),

    # 7. Known module names in the same interactions (marker path, serving-layer OOS).
    ("x-known-654-body-css", "[[module654 CSS]]\nbody\n[[/module]]\n"),
    ("x-known-mod-body-654", f"[[module CSS]]\n[[module654 {U}]]\ninner\n[[/module]]\n[[/module]]\n"),
]

with open("conformance-refphp/module/xbattery.jsonl", "w", encoding="utf-8") as f:
    for cid, src in cases:
        f.write(json.dumps({"id": cid, "source": src}, ensure_ascii=False) + "\n")
print(f"wrote {len(cases)} cases")
