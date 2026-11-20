// R2 Code stage ftml-side dumper.
// Reads JSONL {"id","source"} on stdin, emits JSONL
// {"id","html","errors","codes"} where `html` is the legacy-Wikidot-layout
// HtmlRender body (the same surface as ftml's code/*/wikidot.html pins),
// `errors` lists parse errors, and `codes` lists the tracked code blocks.
use ftml::data::PageInfo;
use ftml::layout::Layout;
use ftml::render::html::HtmlRender;
use ftml::render::Render;
use ftml::settings::{WikitextMode, WikitextSettings};
use std::io::{BufRead, Write};

fn main() {
    let settings = WikitextSettings::from_mode(WikitextMode::Page, Layout::Wikidot);
    let page_info = PageInfo {
        page: "some-page".into(),
        category: None,
        site: "sandbox".into(),
        title: "A page for the age".into(),
        alt_title: None,
        score: 69.0.into(),
        tags: vec![],
        language: "default".into(),
    };
    let stdin = std::io::stdin();
    let mut stdout = std::io::stdout().lock();
    for line in stdin.lock().lines() {
        let line = match line { Ok(l) => l, Err(_) => break };
        if line.trim().is_empty() { continue; }
        let v: serde_json::Value = serde_json::from_str(&line).unwrap();
        let id = v["id"].as_str().unwrap();
        let source = v["source"].as_str().unwrap();
        let mut processed = source.to_string();
        ftml::preprocess_for_layout(&mut processed, settings.layout);
        let tokenization = ftml::tokenize(&processed);
        let (tree, errors) = ftml::parse(&tokenization, &page_info, &settings).into();
        let html = HtmlRender.render(&tree, &page_info, &settings).body;
        let codes: Vec<serde_json::Value> = tree.code_blocks.iter().map(|c| {
            serde_json::json!({
                "contents": c.contents,
                "language": c.language,
                "name": c.name,
            })
        }).collect();
        let errs: Vec<String> = errors.iter().map(|e| format!("{e:?}")).collect();
        let rec = serde_json::json!({"id": id, "html": html, "errors": errs, "codes": codes});
        writeln!(stdout, "{}", rec).unwrap();
    }
}
