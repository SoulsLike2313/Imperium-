# External Finalization Receipt Contract

Status: `CANDIDATE_V0_1`
Owner organ: `Administratum`

## Core rule

A file inside a commit is not required to know the hash of that same containing commit.

Forbidden for clean PASS:

- strict self-finalization claim based on guessed current hash;
- ambiguous `final_head` without semantic split;
- hiding missing external delivery verification.

## Required semantic split

- `last_verified_head_before_this_commit`
- `receipt_content_head`
- `external_delivery_head`
- `remote_head_after_push`
- `followup_finalization_receipt_head` (optional when pending)

## Clean pass gate

`clean_pass_allowed` must be `false` when any cap in this set is active:

- `CAP_SELF_HEAD_PARADOX`
- `CAP_AMBIGUOUS_FINAL_HEAD`
- `CAP_EXTERNAL_FINALIZATION_RECEIPT_MISSING`
- `CAP_FINALIZATION_SEMANTICS_CONTRADICTORY`

## Migration note

Legacy `final_head` may exist for historical trace, but cannot be treated as authoritative clean-pass proof.
