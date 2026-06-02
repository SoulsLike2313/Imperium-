# PC Transfer Requirements

The task must package web research data and send it to the PC IMPERIUM context folder by SSH if a route exists.

## Candidate PC routes

Use existing configured routes only. Try safe route discovery, for example:

- SSH config aliases containing `pc` or `imperium-pc`;
- known local route if already configured by the Owner;
- do not modify keys;
- do not print private key contents.

## Candidate PC context folders

Try safe non-destructive detection. Candidate folders may include:

- `E:/IMPERIUM_CONTEXT/INBOX/`
- `E:/IMPERIUM_CONTEXT/LOCAL/TASK_BUNDLES/`
- `C:/Users/PC/IMPERIUM_CONTEXT/INBOX/`
- `C:/Users/PC/Downloads/IMPERIUM_CONTEXT_INBOX/`

If no PC route/path is confirmed, leave the bundle on VM3 and write exact retrieval commands for Owner.

## Receipt

`pc_transfer_receipt.json` must include:

- attempted routes;
- selected route;
- source path;
- target path;
- transferred files;
- SHA256 before/after if possible;
- transfer verdict;
- fallback command if failed.
