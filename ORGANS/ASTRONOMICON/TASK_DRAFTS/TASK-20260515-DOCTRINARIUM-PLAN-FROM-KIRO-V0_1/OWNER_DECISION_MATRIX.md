# Owner Decision Matrix (Draft)

All rows are advisory-derived candidates and are not canonical decisions.

Allowed draft statuses in this file:
- `accept_candidate`
- `accept_with_modification_candidate`
- `defer_candidate`
- `reject_candidate`
- `reference_only`
- `needs_owner_review`

| source_reference | recommendation | affected_area | proposed_status | Owner_decision | reason | implementation_destination | stage_id | risks | evidence_required | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| advisory://section/B | Doctrinarium ownership boundaries | ownership | accept_candidate | needs_owner_review | Define strict authority boundary | ORGANS/DOCTRINARIUM/foundation | STAGE-1 | Ownership collision | Boundary contract plus validation report | Candidate only |
| advisory://section/B | Doctrinarium must not own other organ domains | ownership | accept_candidate | needs_owner_review | Preserve existing organ sovereignty | ORGANS/DOCTRINARIUM/policies | STAGE-1 | Scope creep | Policy constraints plus integration check | Candidate only |
| advisory://section/D-E | JSON canonical law format with paired MD | law_format | accept_candidate | needs_owner_review | Require machine and human format pair | ORGANS/DOCTRINARIUM/laws | STAGE-2 | Schema-doc drift | Schema validation plus sample pair | Candidate only |
| advisory://section/C | Law hierarchy levels 0-4 | law_model | accept_with_modification_candidate | needs_owner_review | Might require simplification for MVP | ORGANS/DOCTRINARIUM/laws | STAGE-2 | Over-complexity | Hierarchy specification evidence | Candidate only |
| advisory://section/F | Active law definition | law_state | accept_candidate | needs_owner_review | Required for deterministic gate behavior | ORGANS/DOCTRINARIUM/laws | STAGE-2 | Ambiguous law status | Registry report with active-state fields | Candidate only |
| advisory://section/H | Organ alive definition | organ_health | accept_candidate | needs_owner_review | Needed for health verdict logic | ORGANS/DOCTRINARIUM/health | STAGE-4 | False healthy status | Health verdict with checker_last_run_utc | Candidate only |
| advisory://section/I | Task execution allowed definition | task_gate | accept_candidate | needs_owner_review | Required for admission control | ORGANS/DOCTRINARIUM/task_gate | STAGE-5 | Unauthorized task execution | Gate verdict report | Candidate only |
| advisory://section/N-O | Law registry | law_registry | accept_candidate | needs_owner_review | Core law inventory contract | ORGANS/DOCTRINARIUM/laws | STAGE-2 | Invalid registry entries | Registry validation report with provenance | Candidate only |
| advisory://section/J | Law integrity guard | law_integrity | accept_candidate | needs_owner_review | Prevent contradictory law activation | ORGANS/DOCTRINARIUM/laws | STAGE-3 | Contradiction hidden by fake pass | Integrity report with contradiction metrics | Candidate only |
| advisory://section/H | Organ health self-report model | organ_health | accept_candidate | needs_owner_review | Deterministic self-report freshness gate | ORGANS/DOCTRINARIUM/health | STAGE-4 | Stale report accepted | Self-report collection + verdict report | Candidate only |
| advisory://section/I | Task start gate | task_gate | accept_candidate | needs_owner_review | Ensure task admission evidence exists | ORGANS/DOCTRINARIUM/task_gate | STAGE-5 | Missing blocking logic | Gate request/verdict pair | Candidate only |
| advisory://section/K | Disabled Inquisition hook | inquisition_hook | accept_candidate | needs_owner_review | Keep explicit disabled behavior in MVP | ORGANS/DOCTRINARIUM/integration | STAGE-6 | Implied active hook claims | Disabled hook verification report | Candidate only |
| advisory://section/T | Violation records | compliance | accept_candidate | needs_owner_review | Preserve traceability for blocked actions | ORGANS/DOCTRINARIUM/compliance | STAGE-5 | Silent policy failure | Violation record artifact | Candidate only |
| advisory://section/T | Fake green prevention | quality | accept_candidate | needs_owner_review | Evidence-first verification discipline | ORGANS/DOCTRINARIUM/tests | STAGE-7 | PASS without evidence | Fake-green test report | Candidate only |
| advisory://section/U | First four candidate laws | law_seed | reference_only | needs_owner_review | Do not activate at planning stage | ORGANS/DOCTRINARIUM/laws | STAGE-0 | Premature canonization | Owner decision before activation | Reference only |
| advisory://section/S | Sanctum dashboard future | dashboard | defer_candidate | needs_owner_review | Backend first, dashboard later | SANCTUM integration docs | STAGE-8 | UI over backend truth | Backend report contract and integration proof | Deferred candidate |
| advisory://section/S-T | No dashboard mock data | dashboard | accept_candidate | needs_owner_review | Prevent visual fake green | SANCTUM integration docs | STAGE-7 | Dashboard diverges from reports | Proof of dashboard reading real reports | Candidate only |
| policy://language | Language and encoding policy | governance | accept_candidate | needs_owner_review | Keep canonical artifacts English UTF-8 safe | Global task package policy | STAGE-0 | Parser drift and encoding ambiguity | Canonical file scan result | Candidate only |
