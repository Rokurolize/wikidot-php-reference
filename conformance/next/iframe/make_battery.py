#!/usr/bin/env python3
"""Build the R2-next Iframe differential battery as JSONL on stdout.
Each case is {"id": ..., "source": ...}; sources use LF and no trailing newline.
The categories cover schemes, URL charset edges, attributes, malformed forms,
positions, and adjacency with neighbors in the reference pipeline order.
"""
import json

CASES = []

def add(name, source):
    CASES.append({"id": "if-" + name, "source": source})

# A. Recognized schemes, including case variants (parse-conf list is case-insensitive in live/ftml).
add("scheme-http", "[[iframe http://example.com/a]]")
add("scheme-https", "[[iframe https://example.com/a]]")
add("scheme-ftp", "[[iframe ftp://example.com/a]]")
add("scheme-gopher", "[[iframe gopher://example.com/a]]")
add("scheme-news", "[[iframe news://example.com/a]]")
add("scheme-mailto", "[[iframe mailto:a@example.com]]")
add("scheme-mms", "[[iframe mms://example.com/a]]")
add("scheme-upper", "[[iframe HTTPS://EXAMPLE.COM/A]]")
add("scheme-mixed", "[[iframe HtTp://Example.Com/MiXeD]]")
add("scheme-news-upper", "[[iframe NEWS://example.com/a]]")
add("scheme-mms-upper", "[[iframe MMS://example.com/a]]")

# B. Refused / non-scheme forms that must stay literal (and exercise the Url rule tail).
add("scheme-git", "[[iframe git://example.com/a]]")
add("scheme-javascript", "[[iframe javascript:alert(1)]]")
add("scheme-data", "[[iframe data:text/html,x]]")
add("scheme-none", "[[iframe example.com/a]]")
add("scheme-empty-url", "[[iframe ]]")
add("scheme-no-opener", "[[iframe]]")

# C. Slash, quote, space, tab and delimiter edges inside the URL.
add("url-slash-segments", "[[iframe https://example.com/a/b/c]]")
add("url-no-path", "[[iframe https://example.com]]")
add("url-trailing-slash", "[[iframe https://example.com/]]")
add("url-doublequote", '[[iframe http://example.com/a"b]]')
add("url-singlequote-final", "[[iframe http://example.com/a'b]]")
add("url-singlequote-mid", "[[iframe http://example.com/a'b/c]]")
add("url-singlequote-two", "[[iframe http://example.com/a'b'c/d]]")
add("url-space", "[[iframe http://example.com/a b]]")
add("url-tab", "[[iframe http://example.com/a\tb]]")
add("url-backslash", "[[iframe http://example.com/a\\b]]")
add("url-delim-u00ff", "[[iframe http://example.com/ÿ]]")
add("url-percent", "[[iframe http://example.com/%20x]]")
add("url-query-fragment", "[[iframe http://example.com/?q=1&x=2#frag]]")
add("url-utf8-path", "[[iframe http://example.com/日本語]]")
add("url-utf8-query", "[[iframe http://example.com/?q=日本語#frag日]]")
add("url-braces", "[[iframe http://example.com/{a}]]")
add("url-angle", "[[iframe http://example.com/<x>]]")

# D. Attributes: all recognized names, order, unknown, duplicate, quoted, spaced equals.
add("attr-none", "[[iframe http://example.com/]]")
add("attr-all-unquoted", "[[iframe http://example.com/ align=left frameborder=0 height=7 scrolling=no width=100 class=z style=color:red]]")
add("attr-all-quoted", '[[iframe http://example.com/ align="left" frameborder="0" height="7" scrolling="no" width="100" class="z" style="color:red"]]')
add("attr-order-shuffled", '[[iframe http://example.com/ style="color:red" width="5" scrolling="auto" align="right" frameborder="1" height="7" class="z"]]')
add("attr-unknown-filtered", '[[iframe http://example.com/ title="T" id="i" data-x="1" allowtransparency="true" scrolling="auto"]]')
add("attr-duplicate", '[[iframe http://example.com/ width="1" width="2"]]')
add("attr-spaced-equals", '[[iframe http://example.com/ id = "my-example" class="iframe" width = "90%"]]')
add("attr-mixed-spaced", '[[iframe http://example.com/ width = "1" height="2"]]')
add("attr-single-quoted", "[[iframe http://example.com/ width='1' height='2']]")
add("attr-escaped-quote", '[[iframe http://example.com/ class="a\\"b"]]')
add("attr-empty-value", '[[iframe http://example.com/ width=""]]')
add("attr-only-src-space", "[[iframe http://example.com/   ]]")
add("attr-scheme-and-attrs", '[[iframe https://example.net/my-page frameborder="0"]]')

# E. Malformed and unterminated forms.
add("bad-unterminated", "[[iframe http://example.com/")
add("bad-unterminated-attrs", '[[iframe http://example.com/ width="1"')
add("bad-extra-brackets", "[[iframe http://example.com/]]]")
add("bad-double-opener", "[[iframe http://a.com/]] [[iframe http://b.com/]]")
add("bad-closer-only", "[[/iframe]]")
add("bad-no-space", "[[iframehttp://example.com/]]")
add("bad-newline-in-head", "[[iframe\nhttp://example.com/]]")

# F. Mid-line and line-start positions.
add("pos-midline", "before [[iframe http://example.com/]] after")
add("pos-line-start", "text\n[[iframe http://example.com/]]")
add("pos-leading-space", "  [[iframe http://example.com/]]")
add("pos-after-blank", "a\n\n[[iframe http://example.com/]]")
add("pos-two-lines", "[[iframe http://a.com/]]\n[[iframe http://b.com/]]")
add("pos-newline-then-text", "[[iframe http://example.com/]]\nx ]]")

# G. Greedy-tail boundary (the Iframe-owned tail scan) and closer shapes.
add("tail-newline-closer", "[[iframe http://e.com/]]\n[[/div]]")
add("tail-no-newline-closer", "[[iframe http://e.com/]][[/div]]")
add("tail-two-closers", "[[iframe http://e.com/]]\n[[/div]][[/span]]")
add("tail-text-closer", "[[iframe http://e.com/]]\nfoo\n[[/div]]")
add("tail-space-stops", "[[iframe http://e.com/]] foo]]")
add("tail-tab-stops", "[[iframe http://e.com/]]\nfoo\tx]]")
add("tail-blank-span", "[[iframe http://e.com/]]\n\n[[span]]y[[/span]]")
add("tail-args-newline-closer", '[[iframe http://e.com/ width="1"]]\n[[/div]]')
add("tail-surviving-close", "[[div]]\n[[iframe http://example.com/]]\n[[/div]]\nspace here\n[[/div]]")
add("tail-invalidates-div", "[[div]]\n[[iframe http://example.com/]]\n[[/div]]")
add("tail-keeps-div-after-args", '[[div]]\n[[iframe http://example.com/ width="1"]]\n[[/div]]')

# H. Adjacency with neighbors in pipeline order: Iftags (before), Comment (before),
#    Code (earlier), Date/Math (after), Divprefilter/Anchor/Freelink (after).
add("adj-iftags-seam-name", "[[ifr[[iftags -zzz]][[/iftags]]ame http://example.com/]]")
add("adj-iftags-seam-url", "[[iframe http://a.example/b[[iftags -zzz]][[/iftags]]c]]")
add("adj-comment-in-url", "[[iframe https://exam[!--x--]ple.com/]]")
add("adj-comment-before", "[!-- hide --]\n[[iframe http://example.com/]]")
add("adj-code-before", "[[code]]\n[[iframe http://example.com/]]\n[[/code]]")
add("adj-greedy-iftags-failing", "[[iframe http://e.com/]]\n[[iftags a]]\nx\n[[/iftags]]\n[[/div]]")
add("adj-greedy-iftags-kept", "[[iframe http://e.com/]]\n[[iftags fruit]]\nx\n[[/iftags]]\n[[/div]]")
add("adj-date-after", "[[iframe http://example.com/]]\n[[date 0]]")
add("adj-math-after", "[[iframe http://example.com/]]\n[[math]]\nE=mc^2\n[[/math]]")
add("adj-anchor-around", '[[a href="/y"]][[iframe http://example.org/embed width="1"]][[/a]]')
add("adj-span-around", '[[span]][[iframe http://example.org/embed width="1"]][[/span]]')
add("adj-freelink-tail", "[[iframe https://example.com/a]]\n[[https://example.com/b]]")

def main():
    for case in CASES:
        print(json.dumps(case, ensure_ascii=False))

if __name__ == "__main__":
    main()
