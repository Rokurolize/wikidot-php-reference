#!/usr/bin/env python3
"""Generate the Date-rule battery for the R2-next stage.

Each record is {"id","source"} for the shared reference harness (batch.php)
and the shared ftml dumper (r2next-rust-dump). The battery covers the Date
matching space: unix timestamps (leading zeros, negatives, huge and
over-i128 integers), non-unix and blank values, attribute and format edges,
name-case variants, mid-line and line-start positions, malformed forms, and
adjacency with the neighboring rules in pipeline order (Iftags, Comment,
Iframe before Date, Math after Date). Sources are LF-only with no trailing
newline so the same source can be reused verbatim for live probes.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "battery.jsonl")

cases = []


def add(cid, src):
    cases.append({"id": cid, "source": src})


# Numeric value forms.
add("d01-basic", "[[date 1216153821]]")
add("d02-basic-format", '[[date 1216153821 format="%Y"]]')
add("d03-leading-zeros", '[[date 00001216153821 format="%Y"]]')
add("d04-zero", "[[date 0]]")
add("d05-one", "[[date 1]]")
add("d06-negative", "[[date -1000]]")
add("d07-negative-one", "[[date -1]]")
add("d08-huge-14", "[[date 99999999999999]]")
add("d09-huge-20", "[[date 99999999999999999999]]")
add("d10-huge-42", "[[date 999999999999999999999999999999999999999999]]")
add("d11-neg-huge-14", "[[date -99999999999999]]")
add("d12-neg-huge-42", "[[date -999999999999999999999999999999999999999999]]")
add("d13-plus", '[[date +1216153821 format="%Y"]]')

# Non-unix, blank and missing values.
add("d14-iso-date", "[[date 2009-12-25]]")
add("d15-iso-datetime", "[[date 2009-12-25T08:18:05+02:00]]")
add("d16-rfc3339-z", "[[date 2007-05-12T09:34:51Z]]")
add("d17-now", "[[date now]]")
add("d18-NOW", "[[date NOW]]")
add("d19-dot", "[[date .]]")
add("d20-blank", "[[date  ]]")
add("d21-blank-with-format", '[[date  format="%Y"]]')
add("d22-no-value", "[[date]]")
add("d23-nonnumeric", "[[date foobar]]")
add("d24-partial-date", "[[date 2001-09]]")
add("d25-quoted-number", '[[date "1216153821"]]')
add("d26-leading-tab", "[[\tdate 1216153821]]")
add("d27-decimal", "[[date 1216153821.5]]")
add("d28-hex", "[[date 0x10]]")

# Attributes and format handling.
add("d29-unquoted-format", "[[date 1216153821 format=%Y]]")
add("d30-single-quoted-format", "[[date 1216153821 format='%Y']]")
add("d31-duplicate-format", '[[date 1216153821 format="%Y" format="%m"]]')
add("d32-unknown-attr", '[[date 1216153821 foo="bar"]]')
add("d33-empty-format", '[[date 1216153821 format=""]]')
add("d34-agohover", '[[date 1216153821 format="%Y|agohover"]]')
add("d35-g-format", '[[date 1216153821 format="%g"]]')
add("d36-spaced-format", '[[date 1216153821 format="%d. %m. %Y"]]')
add("d37-html-format", '[[date 1216153821 format="<b>&"]]')
add("d38-tz-attr", '[[date 1216153821 format="%Y" tz="+8"]]')
add("d39-hover", '[[date 1216153821 hover="true"]]')
add("d40-raw-format", '[[date 0 format="@@a@@"]]')

# Name-case variants.
add("d41-case-DATE", "[[DATE 1216153821]]")
add("d42-case-Date", "[[Date 1216153821]]")
add("d43-case-dAtE", "[[dAtE 1216153821]]")

# Position and repetition.
add("d44-midline", "before [[date 1216153821]] after")
add("d45-line-start", "[[date 1216153821]]\ntail")
add("d46-indented", "  [[date 1216153821]]")
add("d47-two-same-line", "[[date 1]] and [[date 2]]")
add("d48-trailing-tail", "[[date 1216153821]]tail")

# Malformed and unterminated forms.
add("d49-unterminated", "[[date 1216153821")
add("d50-unterminated-attr", '[[date 1216153821 format="%Y"')
add("d51-extra-bracket", "[[date 1216153821]]]")
add("d52-spaced-brackets", "[[ date 1216153821 ]]")
add("d53-no-space", "[[date1216153821]]")
add("d54-newline-in-opener", "[[date\n1216153821]]")

# Adjacency with neighboring rules in pipeline order.
add("d55-iframe-then-date", "[[iframe https://example.com/a]]\n[[date 1216153821]]")
add("d56-date-then-math", "[[date 1216153821]]\n[[math E]]\nx=1\n[[/math]]")
add("d57-comment-hides-date", "before[!-- [[date 1216153821]] --]after")
add("d58-comment-in-format", '[[date 1216153821 format=[!-- x --]"%Y"]]')
add("d59-iftags-date", "[[iftags +alpha]]\n[[date 1216153821]]\n[[/iftags]]")
add("d60-date-in-code", "[[code]]\n[[date 1216153821]]\n[[/code]]")

with open(OUT, "w", encoding="utf-8") as handle:
    for record in cases:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
print("wrote %d cases to %s" % (len(cases), OUT))
