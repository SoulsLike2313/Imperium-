# OWNER VISUAL TARGET MATRIX V0.1

This matrix defines review requirements only. It does not claim current UI compliance.

## Target Visual Feeling
- Command bridge discipline with neural-map clarity.
- Imperial sci-fi identity with readable operator control.
- Calm authority over noisy spectacle.

## Direction: Command Bridge / Neural Map / Imperial Sci-Fi
- Dark structured backdrop with selective accent lighting.
- Central cognition object as visual spine.
- Tactical lines/zones must remain readable at a glance.

## Central Brain Object Requirements
- Must be visually dominant but not semantic-truth-bearing by itself.
- Must support low-cost pulse/drift animation.
- Must have fallback static representation for reduced-motion mode.

## Zone/Capsule Requirements
- Zone capsules must be consistently named and visibly grouped.
- Zone state labels must bind to truth manifest entries.
- Warning/blocked states must never rely on color alone.

## Top Rail Requirements
- Show context, snapshot, run identifiers, and stale/fresh markers.
- Any PASS/READY wording requires receipt-backed evidence.
- Bilingual RU/EN labels should preserve consistent intent.

## Right Operator Panel Requirements
- Must prioritize action clarity over decoration.
- Must expose gate state, receipt references, and blockers.
- Must differentiate handoff vs execution wording.

## Readability Requirements
- Text contrast and spacing must support prolonged operator reading.
- Key labels should remain readable at 100% and 125% zoom.
- Dense visual clusters must include hierarchy and separation cues.

## Bilingual RU/EN Expectations
- Key operational labels available in RU and EN, with stable mapping.
- Safety-critical states must avoid ambiguous translation.
- PASS/FAIL/READY semantics must remain identical across languages.

## Screenshot Matrix (For Future Review Evidence)
| Capture ID | View | Required Elements | Risk To Check |
|---|---|---|---|
| SS-01 | Full dashboard | Brain + topology + operator panel | visual noise hiding truth |
| SS-02 | Top rail focus | snapshot/run/receipt indicators | fake green wording |
| SS-03 | Zone/capsule focus | zone labels + state markers | color-only status |
| SS-04 | Receipt overlay | receipt id + timestamp + source | stale data shown as fresh |
| SS-05 | Reduced motion mode | static fallback readability | motion-required understanding |

## Forbidden Patterns
- Global decorative green not tied to evidence.
- Animated progress implying backend completion without receipt.
- Screenshots used as sole readiness proof.
- Decorative layers carrying live counters/status.

## Owner Review Checklist
- [ ] Layer split respected (decorative vs semantic vs live truth).
- [ ] Truth-bearing labels map to backend source placeholders/receipts.
- [ ] No fake green language or implied PASS without evidence.
- [ ] Performance budget fields and blockers are explicit.
- [ ] Reduced-motion behavior is defined.
- [ ] Handoff vs execution wording is explicit and safe.
