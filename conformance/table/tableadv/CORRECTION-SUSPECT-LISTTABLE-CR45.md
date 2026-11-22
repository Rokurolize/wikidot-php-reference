# CORRECTION C-SUSPECT-LISTTABLE-1/2/6/7 and C-R45-1/2/3 — Deflist/List/Tableadv (REFCORR3 lane, 2026-11-22)

Status: APPLIED in this tree. The SUSPECT-LISTTABLE lane confirmed four reference divergences (all sixteen of its live probes valid, stable and source-matched) and the coordinator's MEASURE-TABLE round showed three further shapes where the frozen reference pin and the R2 dumper carry older bytes while live and ftml agree. All seven are reference-and-pin corrections here; ftml is untouched.

## The settling evidence (fresh live probes, all valid, stable, and saved-source-matching)

Probes are under the permanent muse-probe-suspect-listtable- prefix on sandbox-for-codex (conformance-suspect-listtable/{probe-cases.jsonl,probe-map.json,captures.json,ref-render.jsonl,adjudication.txt}). s01/s02: `: [[# foo]] : def` and `: [[user alice]] : def` keep a visible `<dt>` on live where the reference stripped the placeholder; the s16 Comment control keeps the empty term. s04: `[[cell]]X[[/HCELL]]` is a plain `<td>` on live, while the s05 opener-case control and S3/S5 confirm the /i opener grammar. s09: stacked empty items (`* \n  * \nx`) leave no list on live, where the reference kept a spurious parent; p06/p07's empty parent with a real child still survives. s12: `data-x="it's"` is emitted raw on live, while s11 pins List's already-correct ENT_COMPAT behaviour. For the re-pin, R2's M49/M50/M51 (conformance-refphp/R2-TABLE.md and table/tableadv/SECTION.md) record the old pins; REPORT-MEASURE-TABLE.md shows live and ftml byte-identical on adv23 (`data-name="bad" colspan="abc"`), adv30 (aria-label dropped) and adv39 (align dropped), so only the reference and its pins move.

## The correction (reference)

Parse/Default/Deflist.php's termRendersEmpty now strips only placeholders whose token rule is Comment, keeping Anchor/User/Bibcite terms non-empty. Parse/Default/Tableadv.php compares the closer case-sensitively, drops the aria- branch and the align allowlist entry, and replaces ksort with the wikidot rank order (id, class, style, role, type, data-*, then other in authored order). Parse/Default/List.php uses a backward fixpoint over surviving items for the empty-parent test (this file also carries C-SUSPECT-G15-1, recorded under conformance-refphp/list/). Render/Xhtml/Tableadv.php escapes attributes with ENT_COMPAT instead of ENT_QUOTES|ENT_SUBSTITUTE. Before-copies (all `.before-refcorr3`, beside their files): Deflist.php de9433170ad1ced8..., Tableadv.php parse 1b9abca3d5154400..., List.php 2fd92a9d247e78ad..., Tableadv.php render 84678c1420be482a...; corrected hashes 4c1f2192d7b2f21e..., 0498e35c3f5cf467..., 242a0b08885344e2..., 72807c6c333cf867.... The frozen pins in conformance-refphp/table/tableadv/ref-render-final.jsonl are regenerated from the corrected reference at cases adv23/adv30/adv39, and the R2/R45/SECTION prose is updated to re-pin ADV-F1/2/3 to live; the historical ftml dumper file is annotated, not edited.

## Firsthand verification (REFCORR3 lane, 2026-11-22)

The corrected reference matches live's structural fragment on all four decisive probes and leaves every S-control unchanged; the R2 tableadv battery and the r45 family are re-run with every movement named in REPORT-REFCORR3.md.

## Mirror consequence

ListTableRules.lean's attribute fragment uses the ENT_COMPAT escaper and ListTableRender.lean's tableadv_cell_attrs_order is restated to `<td data-name="it's" colspan="2">`; the parse mirrors ListRules.lean (Comment-only strip and backward fixpoint) and TableRules.lean (dropped align/aria, case-sensitive closer) are corrected with new characterizations. The r45 gates are re-run; see REPORT-REFCORR3.md.
