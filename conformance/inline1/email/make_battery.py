#!/usr/bin/env python3
"""Generate the R2 Email (pipeline rule 41) battery of whole-document Wikidot-source cases.

The battery covers the matching space of the Email rule: bare addresses in
isolation and in prose; local-part forms (dots, plus addressing, underscore,
dash, digits, uppercase, single character); domain forms (multi-label,
subdomain, country-code, numeric label, single-label host, trailing dot,
consecutive dots, leading or trailing label dash, underscore in domain,
adjacent punctuation); bracketed and described forms ([address label],
[address], <address>, [[address]], mailto: addresses and mailto inside a
single-bracket link); addresses inside URL targets and inside other markup
(code, raw, bold, table cells, comments); and malformed or unterminated shapes
(missing @, missing domain dot, double @, empty local part, unterminated
bracket). Every case id is prefixed e41- so it stays disjoint from the Url,
Mathinline, Interwiki and root's cross-rule cases. Sources are LF-only with
trailing newlines stripped, matching Wikidot's save normalization; JSON stores
their newlines as escaped \\n. Both the shared reference harness and the shared
ftml dumper accept this JSONL protocol. Reproduce with
`python3 conformance-refphp/inline1/email/make_battery.py`.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

CASES = [
    # --- bare addresses -------------------------------------------------------
    ("e41-01-bare-simple", "abc@example.com"),
    ("e41-02-bare-in-prose", "Contact us: info@example.net"),
    ("e41-03-bare-two-in-line", "a@one.com and b@two.org"),
    ("e41-04-bare-uppercase", "User.Name@Example.COM"),
    ("e41-05-bare-one-char", "x@y.io"),
    ("e41-06-bare-plus", "user+tag@example.com"),
    ("e41-07-bare-underscore", "first_last@example.com"),
    ("e41-08-bare-dash-local", "first-last@example.com"),
    ("e41-09-bare-dotted-local", "first.middle.last@example.com"),
    ("e41-10-bare-digits", "123@456.com"),
    # --- domain forms ---------------------------------------------------------
    ("e41-11-subdomain", "user@mail.sub.example.co.uk"),
    ("e41-12-domain-dash", "user@some-domain.example.com"),
    ("e41-13-domain-numeric-label", "user@123.example"),
    ("e41-14-single-label-host", "user@localhost"),
    ("e41-15-trailing-dot", "user@example.com."),
    ("e41-16-double-dot-domain", "user@example..com"),
    ("e41-17-leading-dash-domain", "user@-example.com"),
    ("e41-18-trailing-dash-domain", "user@example-.com"),
    ("e41-19-underscore-domain", "user@example_com.net"),
    ("e41-20-domain-close-paren", "user@example.com)"),
    # --- bracketed and described forms ---------------------------------------
    ("e41-21-described", "[user@example.com Contact us]"),
    ("e41-22-described-multiword", "[user@example.com The sales team here]"),
    ("e41-23-described-upper", "[USER@EXAMPLE.COM Mixed Case]"),
    ("e41-24-described-two-spaces", "[user@example.com  Double gap]"),
    ("e41-25-described-no-space", "[user@example.comContact]"),
    ("e41-26-described-empty-label", "[user@example.com ]"),
    ("e41-27-described-unterminated", "[user@example.com Label"),
    ("e41-28-bracketed-bare", "[user@example.com]"),
    ("e41-29-angle-bracketed", "<user@example.com>"),
    ("e41-30-double-bracketed", "[[user@example.com]]"),
    ("e41-31-bracketed-mailto", "[mailto:user@example.com]"),
    ("e41-32-bracketed-mailto-label", "[mailto:user@example.com Mail me]"),
    # --- address in URL / scheme forms ---------------------------------------
    ("e41-33-mailto-bare", "mailto:user@example.com"),
    ("e41-34-mailto-upper-scheme", "MAILTO:User@Example.COM"),
    ("e41-35-mailto-pipe-label", "mailto:user@example.com|Mail me"),
    ("e41-36-http-userinfo", "see http://user@example.com/path here"),
    ("e41-37-https-with-email-in-path", "https://example.com/a/user@x.org/z"),
    ("e41-38-url-then-email", "http://example.com and user@example.com"),
    # --- trailing punctuation and neighbors ----------------------------------
    ("e41-39-comma", "Write to user@example.com, please"),
    ("e41-40-semicolon-and-bang", "user@example.com; and other@example.net!"),
    ("e41-41-parenthesized", "(user@example.com)"),
    ("e41-42-question-and-colon", "user@example.com? next: a@b.co"),
    ("e41-43-quote-wrapped", "\"user@example.com\""),
    ("e41-44-apostrophe-after", "user@example.com's mailbox"),
    ("e41-45-exclamation-attached", "Hi user@example.com!"),
    # --- malformed and unterminated ------------------------------------------
    ("e41-46-no-at", "user.example.com"),
    ("e41-47-no-domain-dot", "user@example"),
    ("e41-48-double-at", "user@@example.com"),
    ("e41-49-empty-local", "@example.com"),
    ("e41-50-empty-domain", "user@"),
    ("e41-51-local-space", "user name@example.com"),
    ("e41-52-plus-only", "user+@example.com"),
    ("e41-53-dot-start-local", ".user@example.com"),
    ("e41-54-trailing-underscore-local", "user_@example.com"),
    ("e41-55-cjk-local", " użytkownik@example.com"),
    # --- inside other markup, where earlier rules may own the surface --------
    ("e41-56-in-bold", "**user@example.com**"),
    ("e41-57-in-raw", "@@user@example.com@@"),
    ("e41-58-in-code", "[[code]]\nuser@example.com\n[[/code]]"),
    ("e41-59-in-table-cell", "|| user@example.com || other@example.net ||"),
    ("e41-60-comment-inside", "support[!--x--]@wikidot.com"),
    ("e41-61-email-then-comment", "user@example.com[!--x--] tail"),
    ("e41-62-mixed-document", "Reach **sales@example.com** or [mailto:help@example.net Help] today."),
]


def main():
    ids = set()
    with open(OUT, "w", encoding="utf-8") as fh:
        for cid, source in CASES:
            assert cid not in ids, "duplicate id: " + cid
            ids.add(cid)
            assert "\r" not in source and not source.endswith("\n"), cid
            fh.write(json.dumps({"id": cid, "source": source}, ensure_ascii=False) + "\n")
    print("wrote %d cases to %s" % (len(CASES), OUT))


if __name__ == "__main__":
    main()
