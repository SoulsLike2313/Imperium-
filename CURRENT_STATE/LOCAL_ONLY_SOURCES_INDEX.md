# LOCAL ONLY SOURCES INDEX

- policy: local-only sources stay local and are represented in Git only by safe indexes.
- no secret content is stored here.

| Relative Path | Exists | File Count | Purpose | Secrecy | Include in Private Bundle | Publish to Git | Notes |
|---|---|---:|---|---|---|---|---|
| SSH_COMMAND_LIBRARY | yes | 240 | Private SSH/command library | HIGH | manual_only | False | Never publish command bodies or credentials |
| ARCHIVE | yes | SKIPPED_NO_RECURSIVE_SCAN_POLICY | Historical bulk archive | MEDIUM | manual_only | False | Archive recursive scan is blocked by policy |
| BUNDLES_LOCAL | no | 0 | Private task bundle staging | HIGH | true | False | Bundle contents depend on task scope |
| PRIVATE_CONTEXT_LOCAL | no | 0 | Private local context store | HIGH | manual_only | False | May not exist yet |
| RUNTIME_LOCAL | no | 0 | Runtime/local machine artifacts | MEDIUM | false | False | May not exist yet |
| OBSERVED\THRONE_REPO_COPY | yes | SKIPPED_NO_RECURSIVE_SCAN_POLICY | Legacy observed copy (local reference) | HIGH | manual_only | False | No recursive scan in this task |
| OBSERVED\VM3_REPO_COPY | yes | SKIPPED_NO_RECURSIVE_SCAN_POLICY | Legacy observed copy (local reference) | MEDIUM | manual_only | False | No recursive scan in this task |
