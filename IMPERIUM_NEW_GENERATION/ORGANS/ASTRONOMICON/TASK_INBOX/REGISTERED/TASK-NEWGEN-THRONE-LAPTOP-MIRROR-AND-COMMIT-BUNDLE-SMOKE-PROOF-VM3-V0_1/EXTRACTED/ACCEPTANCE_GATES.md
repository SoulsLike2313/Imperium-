# ACCEPTANCE GATES

## PASS gate

PASS or PASS_WITH_WARNINGS is allowed only if all are true:

- Throne route status is explicitly reported as LIVE, PARTIAL, or BLOCKED_WITH_REASON.
- No private key, token, or credential is committed.
- SSH probe receipt exists.
- Git truth/mirror smoke receipt exists.
- Commit bundle smoke receipt exists.
- If live route succeeded, at least one commit object is verified from Throne local git object storage.
- If bundle export succeeded, SHA256SUMS and metadata are present.
- If live route failed, the task does not claim live proof and provides exact owner action required.
- Inquisition red-team verdict exists.
- Mechanicus validation receipt exists.
- Git closure receipt exists for non-BLOCK result.
- Final Owner response uses the 4-part contract.

## Clean PASS block conditions

Clean PASS is forbidden if any are true:

- Laptop/Throne route is not live-proven.
- No commit object was verified on Throne.
- No bundle or bundle-manifest was produced.
- Any global cap is mixed into local step verdict without classification.
- Any credential was exposed or copied into repo artifacts.
- Public server or Cloudflare route was introduced.

## BLOCK gate

Return BLOCK if:

- SSH work would require copying secrets into the repo.
- A destructive operation on laptop or repo would be needed.
- The task cannot determine a safe route and cannot produce a useful plan/receipt.
