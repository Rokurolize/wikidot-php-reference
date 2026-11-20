"""Capture the R2-next Iftags probes using wikidot-probe's own helpers.

The bundled capture subcommand is all-or-nothing and aborted twice on
transient Wikidot 503 / connect-timeout responses. This driver calls the same
probe helpers (fetch_rendered, extract_page_content, read_saved_source,
make_client, norm) with bounded retries and writes captures.json after every
case, so a transient network fault cannot discard earlier evidence. The
campaign discipline (two identical anonymous GETs, saved-source identity by
sha256) is unchanged. Prose is on single lines.
"""
import hashlib
import importlib.machinery
import importlib.util
import json
import time

loader = importlib.machinery.SourceFileLoader(
    "wikidot_probe", "/home/roku/.agents/skills/wikidot-py-operations/scripts/wikidot-probe")
spec = importlib.util.spec_from_loader("wikidot_probe", loader)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

mapping = json.load(open("probe-map.json", encoding="utf-8"))
captures = {}
try:
    captures = json.load(open("captures.json", encoding="utf-8"))
except Exception:
    pass


def fetch_with_retry(fullname, attempts=6):
    last = None
    for attempt in range(attempts):
        try:
            return probe.fetch_rendered("sandbox-for-codex", fullname)
        except Exception as exc:
            last = exc
            print("RETRY", fullname, attempt + 1, type(exc).__name__, flush=True)
            time.sleep(3 + 2 * attempt)
    raise last


def flush():
    with open("captures.json", "w", encoding="utf-8") as fh:
        fh.write(json.dumps(captures, ensure_ascii=False, indent=1) + "\n")


with probe.make_client("sandbox-for-codex", "A") as client:
    site = client.site.get("sandbox-for-codex")
    for case_id, value in mapping.items():
        if case_id in captures and captures[case_id].get("valid"):
            print("SKIP", case_id, flush=True)
            continue
        fullname = value["fullname"]
        expected = value.get("source")
        first = probe.extract_page_content(fetch_with_retry(fullname))
        time.sleep(1.0)
        second = probe.extract_page_content(fetch_with_retry(fullname))
        stable = first == second
        saved = probe.read_saved_source(site, fullname)
        matches = None if expected is None else (saved == expected)
        valid = stable and matches is not False and saved is not None
        captures[case_id] = {
            "fullname": fullname,
            "html": first,
            "html_sha256": hashlib.sha256(first.encode()).hexdigest(),
            "source": saved,
            "source_sha256": hashlib.sha256(saved.encode()).hexdigest() if saved is not None else None,
            "saved_source_matches": matches,
            "stable": stable,
            "valid": valid,
        }
        print(case_id, "stable=", stable, "matches=", matches, "valid=", valid, flush=True)
        flush()
        time.sleep(1.0)
flush()
print("captured", len(captures), "valid", sum(1 for v in captures.values() if v["valid"]), flush=True)
