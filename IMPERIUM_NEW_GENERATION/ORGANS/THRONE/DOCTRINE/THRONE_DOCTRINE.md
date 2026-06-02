# Throne Doctrine

Status: `CANDIDATE_V0_1`

Throne is the local seal of git truth for IMPERIUM. It exists because web availability and local repository truth are different evidence channels. A remote commit page can fail while the local commit object, tree, diff, receipts, and hashes remain valid.

## Doctrine Rules

### TDR-01 Local Git Object First

A commit exists for Throne when `git cat-file -e <sha>^{commit}` succeeds in the accepted local repository mirror. Web URLs may supplement that proof but do not replace it.

### TDR-02 Evidence Bundle Before Narrative

Every review claim about a commit should point to a bundle manifest, changed files manifest, diff patch, commit metadata, and hashes. Agent explanation is not the bundle.

### TDR-03 Task Grouping Is Indexing, Not Admission

Task-to-commit grouping helps reviewers find related changes. It does not admit a candidate as clean, canonical, or safe.

### TDR-04 Admission Truth Is Recorded, Not Invented

Before Custodes exists, Throne may record `INDEXED_ONLY`, `BUNDLE_EXPORTED`, `REVIEW_REQUESTED`, or `OWNER_ACCEPTED_WITH_WARNING`. It must not claim strict admission enforcement.

### TDR-05 Custodes Remains Future Only

Custodes will later own strict candidate admission, dirty candidate alarms, and final admission pass/fail enforcement. Throne prepares records and handoff fields only.

### TDR-06 Local SSH Only

Throne operator access is local-network SSH by default. Public tunnels, public web servers, and private data collection are outside this foundation.

## Fake-Green Bar

Throne must trigger a cap when:

- a commit is claimed without local object verification;
- a bundle is claimed without a manifest;
- a stale bundle is used as current-target evidence;
- GitHub URL status is treated as stronger than local git object truth;
- Custodes admission is claimed before Custodes exists.
