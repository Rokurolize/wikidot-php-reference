#!/usr/bin/env python3
"""Generate the Url-rule whole-document battery.

Each case is a JSONL {"id","source"} record run through the reference harness
(render and tokens) and the shared ftml dumper. Cover the whole Url matching
space: recognized and unrecognized schemes, host and path shapes, trailing
punctuation and bracket/parenthesis balancing, single-bracket described links
and their labels, plain double-bracket autolink targets with the pipe split,
and malformed or unterminated forms. Sources are whole documents; no trailing
newline is required (battery sources need not survive a Wikidot save)."""
import json
import os

CASES = [
    # scheme forms (u01-u14)
    ("u01-http", "See http://example.com here"),
    ("u02-https", "https://example.com/a/b?x=1&y=2"),
    ("u03-ftp", "ftp://example.com/file.txt here"),
    ("u04-gopher", "gopher://example.com/g here"),
    ("u05-news", "news://example.com/n here"),
    ("u06-mms", "mms://example.com/m here"),
    ("u07-mailto", "mailto:user@example.com here"),
    ("u08-ssh", "Go ssh://example.com/a here"),
    ("u09-git", "Go git://example.com/b here"),
    ("u10-sftp", "Go sftp://example.com/c here"),
    ("u11-svn", "Go svn://example.com/d here"),
    ("u12-telnet", "Go telnet://example.com/e here"),
    ("u13-cvs", "Go cvs://example.com/f here"),
    ("u14-www-schemeless", "www.example.com and example.com/path here"),
    # scheme edges: case, glued digit, bare scheme (u15-u19)
    ("u15-upper-scheme", "HTTPS://EXAMPLE.COM/P here"),
    ("u16-mixed-scheme", "HtTpS://example.com/p here"),
    ("u17-glued-digit", "See 9https://example.com/a and x9gopher://example.com/b here"),
    ("u18-bare-scheme", "http:// here"),
    ("u19-scheme-no-host", "https:// here"),
    # host and path shapes (u20-u31)
    ("u20-trailing-slash", "https://example.com/ here"),
    ("u21-query-fragment", "https://example.com/search?q=free+wiki&lang=en#top here"),
    ("u22-percent-encode", "https://example.com/a%20b here"),
    ("u23-port", "http://example.com:8080/path here"),
    ("u24-ip-host", "http://127.0.0.1/index here"),
    ("u25-subdomain", "https://deep.sub.example.co.uk/page here"),
    ("u26-inner-dot", "https://example.com/a.b/c next"),
    ("u27-tilde-underscore", "https://example.com/a~b_c here"),
    ("u28-plus-path", "https://example.com/a+b here"),
    ("u29-at-in-path", "http://example.com/user@name here"),
    ("u30-nonascii-path", "http://example.com/page\u3053\u3053 here"),
    ("u31-nbsp-in-url", "https://example.com/a.png\u00a0width= next"),
    # trailing punctuation and bracket/parenthesis balancing (u32-u46)
    ("u32-terminal-period", "Visit https://example.com/test. next"),
    ("u33-period-eoi", "Visit https://example.com/test."),
    ("u34-period-linebreak", "https://snippets.wikidot.com/code:collapsible-block-unleashed.\n"),
    ("u35-exclaim-suite", "See https://example.com/a!;:) next"),
    ("u36-hash-tail", "See https://example.com/b# here"),
    ("u37-comma-tail", "http://example.com/page, mid"),
    ("u38-comma-inner", "http://example.com/a,b next"),
    ("u39-star-tail", "http://example.com/b** end"),
    ("u40-dash-tail", "http://example.com/a-- next"),
    ("u41-dash-inner", "http://example.com/a--b next"),
    ("u42-brace-tail", "http://example.com/a}} next"),
    ("u43-paren-open-close", "(https://example.com/a) here"),
    ("u44-paren-in-url", "See https://example.com/a_(b) here"),
    ("u45-bracket-in-url", "See https://example.com/a[b]c here"),
    ("u46-quote-pair", "https://example.com/aa``bb''cc here"),
    # single-bracket described links and labels (u47-u55)
    ("u47-described", "[https://example.com Example Description]"),
    ("u48-described-spaces", "[https://example.com/example A label with many words]"),
    ("u49-described-double-space", "[https://example.com  Label Here]"),
    ("u50-described-star", "[*https://example.com Label]"),
    ("u51-described-hash", "[#anchor My Label]"),
    ("u52-described-path", "[/start Go Home]"),
    ("u53-described-no-label", "[http://x/]"),
    ("u54-described-unterminated", "[https://example.com label"),
    ("u55-described-midline", "Before [https://example.com Described] after"),
    # plain double-bracket target grammar and pipe placement (u56-u62)
    ("u56-double-bare", "[[https://example.com/]]"),
    ("u57-double-pipe", "[[http://x/|raw]]"),
    ("u58-double-pipe-raw", "[[http://x/|@@raw@@]]"),
    ("u59-double-pipe-multi", "[[http://x/|a|b]]"),
    ("u60-double-pipe-unterminated", "[[http://x/|label here"),
    ("u61-double-bare-midline", "See [[http://x/]] and text"),
    ("u62-double-pipe-midline", "See [[http://x/|Label]] and text"),
    # star / bold-star forms (u63-u66)
    ("u63-star-bare", "*https://example.com/newtab"),
    ("u64-star-mid", "star mid *http://example.com/star-mid x"),
    ("u65-bold-star", "bold **http://example.com/b** end"),
    ("u66-star-killed-fallback", "[*https://a.example @@x@@ https://b.example]"),
    # malformed / unterminated / raw adjacency (u67-u72)
    ("u67-raw-adjacency", "https://example.com/a@@b end"),
    ("u68-raw-alt-terminates", "https://example.com/@<x>@ end"),
    ("u69-nonascii-terminates", "http://example.com/page\u3059 here"),
    ("u70-block-syntax-stops", "https://example.com/video[[/embedvideo]]"),
    ("u71-empty-after-scheme", "[\u0023 Label]"),
    ("u72-tagged-pipe-url", "[https://example.com Label|With Pipe]"),
    # described-link label swallowing an inline-math opener (root x02)
    ("u73-described-math-label", "[https://example.com/target [[$x$]]]"),
    ("u74-described-math-label-pin", "[https://example.com [[$x$]]]"),
    ("u75-double-pipe-many", "[[http://x/|a|b|c]]"),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "battery.jsonl"), "w", encoding="utf-8") as fh:
        for cid, source in CASES:
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print(f"wrote {len(CASES)} cases")


if __name__ == "__main__":
    main()
