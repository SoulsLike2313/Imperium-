# Packaging Finalization Policy

STATUS: BINDING_FOR_FOUNDATION_0_1A

Rules:
- CONTENT_MANIFEST.json lists payload files only.
- CONTENT_MANIFEST.json excludes itself.
- CONTENT_MANIFEST.json excludes SHA256SUMS.txt.
- CONTENT_MANIFEST.json excludes 07_BUNDLE.
- CONTENT_MANIFEST.json excludes final ZIP and final sidecar.
- SHA256SUMS.txt lists payload files plus CONTENT_MANIFEST.json.
- SHA256SUMS.txt excludes itself.
- FINALIZATION_RECEIPT.json lives outside zipped payload in 07_BUNDLE.
- No self-referential hash loops.
