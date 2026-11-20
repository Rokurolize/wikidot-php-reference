#!/usr/bin/env python3
"""Generate the Url-rule live probe set.

Sources are LF-only with any trailing newline stripped, because Wikidot
rewrites those on save. The rendered anonymous saved-page HTML is the
definition of correct behavior; each source is chosen to arbitrate a shape
the battery cannot settle from corpus pins alone (star target spelling,
Wikidot-only schemes, plain double-bracket pipe grammar, label trimming,
non-ASCII and raw seams, and described-label ownership of inline math)."""
import json
import os

PROBES = [
    ("p01-star-bare", "*https://example.com/newtab"),
    ("p02-star-described", "[*https://example.com Label]"),
    ("p03-double-pipe", "[[http://x/|raw]]"),
    ("p04-double-pipe-raw", "[[http://x/|@@raw@@]]"),
    ("p05-double-pipe-multi", "[[http://x/|a|b]]"),
    ("p06-double-bare", "[[https://example.com/]]"),
    ("p07-double-pipe-unterminated", "[[http://x/|label here"),
    ("p08-double-space-label", "[https://example.com  Label Here]"),
    ("p09-ssh", "Go ssh://example.com/a here"),
    ("p10-git", "Go git://example.com/b here"),
    ("p11-sftp", "Go sftp://example.com/c here"),
    ("p12-svn", "Go svn://example.com/d here"),
    ("p13-telnet", "Go telnet://example.com/e here"),
    ("p14-cvs", "Go cvs://example.com/f here"),
    ("p15-nbsp-in-url", "https://example.com/a.png\u00a0width= next"),
    ("p16-quote-pair", "https://example.com/aa``bb''cc here"),
    ("p17-paren-in-url", "See https://example.com/a_(b) here"),
    ("p18-terminal-period", "Visit https://example.com/test. next"),
    ("p19-bracket-in-url", "See https://example.com/a[b]c here"),
    ("p20-trailing-suite", "See https://example.com/a!;:) next and https://example.com/b# here"),
    ("p21-upper-scheme", "HTTPS://EXAMPLE.COM/P here"),
    ("p22-glued-digit", "9https://example.com/a here"),
    ("p23-mailto", "mailto:user@example.com here"),
    ("p24-image-ext", "https://example.com/a.png here"),
    ("p25-described", "[https://example.com Example Description]"),
    ("p26-bracket-no-label", "[http://x/]"),
    ("p27-nonascii-path", "http://example.com/page\u3053\u3053 here"),
    ("p28-described-math-label", "[https://example.com/target [[$x$]]]"),
    ("p29-described-math-label-pin", "[https://example.com [[$x$]]]"),
    ("p30-bold-star", "bold **http://example.com/b** end"),
    ("p31-pipe-plain", "http://example.com/path|END next"),
    ("p32-raw-adjacency", "https://example.com/a@@b end"),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "probe-cases.jsonl"), "w", encoding="utf-8") as fh:
        for cid, source in PROBES:
            source = source.replace("\r\n", "\n").rstrip("\n")
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print(f"wrote {len(PROBES)} probes")


if __name__ == "__main__":
    main()
