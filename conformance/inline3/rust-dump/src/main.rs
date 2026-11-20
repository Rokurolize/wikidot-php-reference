// R2 Tt / Superscript / Subscript / Typography / Tighten ftml-side dumper, the one shared dumper for this final R2 stage.
// Reads JSONL {"id","source"[,"tags":[...]]} on stdin, emits JSONL
// {"id","html","errors"} where `html` is the legacy-Wikidot-layout
// HtmlRender body (the same surface as ftml's wikidot.html pins).
// Adapted from conformance-refphp/inline2/rust-dump/src/main.rs (the
// Colortext / Strong / Emphasis / Underline / Strikethrough stage dumper),
// itself descended from the inline1 and earlier stage dumpers. Uses
// the full preproc stage (preprocess_for_layout, tokenize, parse, HtmlRender)
// at the read-only ftml checkout HEAD recorded in FTML-HEAD.txt next to this
// crate. The optional per-case `tags` array is accepted for protocol
// compatibility with the shared harness and root's cross-rule
// (muse-probe-r2in3-x-) batteries; keeping the field identical lets every
// battery reuse the same driver.
use ftml::data::PageInfo;
use ftml::layout::Layout;
use ftml::render::html::HtmlRender;
use ftml::render::Render;
use ftml::settings::{WikitextMode, WikitextSettings};
use std::borrow::Cow;
use std::io::{BufRead, Write};

fn main() {
    let settings = WikitextSettings::from_mode(WikitextMode::Page, Layout::Wikidot);
    let stdin = std::io::stdin();
    let mut stdout = std::io::stdout().lock();
    for line in stdin.lock().lines() {
        let line = match line { Ok(l) => l, Err(_) => break };
        if line.trim().is_empty() { continue; }
        let v: serde_json::Value = serde_json::from_str(&line).unwrap();
        let id = v["id"].as_str().unwrap();
        let source = v["source"].as_str().unwrap();
        let tags: Vec<Cow<'static, str>> = match v.get("tags") {
            Some(serde_json::Value::Array(a)) => a
                .iter()
                .filter_map(|t| t.as_str().map(|s| Cow::Owned(s.to_string())))
                .collect(),
            _ => Vec::new(),
        };
        let page_info = PageInfo {
            page: "some-page".into(),
            category: None,
            site: "sandbox".into(),
            title: "A page for the age".into(),
            alt_title: None,
            score: 69.0.into(),
            tags,
            language: "default".into(),
        };
        let mut processed = source.to_string();
        ftml::preprocess_for_layout(&mut processed, settings.layout);
        let tokenization = ftml::tokenize(&processed);
        let (tree, errors) = ftml::parse(&tokenization, &page_info, &settings).into();
        let html = HtmlRender.render(&tree, &page_info, &settings).body;
        let errs: Vec<String> = errors.iter().map(|e| format!("{e:?}")).collect();
        let rec = serde_json::json!({"id": id, "html": html, "errors": errs});
        writeln!(stdout, "{}", rec).unwrap();
    }
}
