"""Create root's tagged cross-rule probes under muse-probe-r2block-x-.

The probe CLI has no tag subcommand, so tagged pages go through wikidot.py's
site.page.publish(tags=[...]) through the pinned wrapper. Capture afterwards is
done by wikidot-probe capture with the map this script writes. Sources have no
trailing newline because Wikidot strips one on save and the probe tool requires
byte-identical read-back. Adapted from conformance-refphp/notes/make_tagged_x.py.
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

PREFIX = "muse-probe-r2block-x-"
SITE = "sandbox-for-codex"
cases = [json.loads(line) for line in
         open("conformance-refphp/block/probe-x-tagged.jsonl", encoding="utf-8") if line.strip()]
result = {}
with probe.make_client(SITE, "A") as client:
    if not client.is_logged_in:
        raise SystemExit("login failed")
    site = client.site.get(SITE)
    for case in cases:
        fullname = PREFIX + probe.slugify(case["id"])
        res = site.page.publish(fullname, title="probe " + case["id"],
                                source=case["source"], tags=case["tags"],
                                verify_source=True)
        saved = probe.read_saved_source(site, fullname)
        result[case["id"]] = {"fullname": fullname, "source": saved,
                              "action": "publish-tags", "tags": case["tags"]}
        print(case["id"], "->", fullname, "source_match=", saved == case["source"], flush=True)
        time.sleep(1.0)
with open("conformance-refphp/block/probe-x-tagged-map.json", "w", encoding="utf-8") as fh:
    fh.write(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
print("wrote", len(result), "tagged probe pages", flush=True)
