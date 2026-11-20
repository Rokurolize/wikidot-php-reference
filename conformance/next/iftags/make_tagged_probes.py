"""Create the tagged R2-next Iftags live probes with wikidot.py's publish API.

The bundled wikidot-probe CLI has create/capture/norm but no tag-setting
subcommand, so tagged pages are published with site.page.publish(tags=[...])
through the same pinned wrapper and then captured by wikidot-probe capture.
The saved source is read back and recorded in the map so capture verifies it.
Prose is on single lines.
"""
import importlib.machinery
import importlib.util
import json
import time

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

PREFIX = "muse-probe-r2next-iftags-"
SITE = "sandbox-for-codex"
cases = [json.loads(line) for line in open("probe-tagged.jsonl", encoding="utf-8") if line.strip()]
result = {}
with probe.make_client(SITE, "A") as client:
    if not client.is_logged_in:
        raise SystemExit("login failed")
    site = client.site.get(SITE)
    for case in cases:
        fullname = PREFIX + probe.slugify(case["id"])
        res = site.page.publish(fullname, title="probe " + case["id"], source=case["source"], tags=case["tags"], verify_source=True)
        saved = probe.read_saved_source(site, fullname)
        result[case["id"]] = {"fullname": fullname, "source": saved, "action": "publish-tags"}
        print(case["id"], "->", fullname, "tags=", case["tags"], "source_match=", saved == case["source"], flush=True)
        time.sleep(1.0)
with open("map-tagged.json", "w", encoding="utf-8") as fh:
    fh.write(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
print("wrote", len(result), "tagged probe pages", flush=True)
