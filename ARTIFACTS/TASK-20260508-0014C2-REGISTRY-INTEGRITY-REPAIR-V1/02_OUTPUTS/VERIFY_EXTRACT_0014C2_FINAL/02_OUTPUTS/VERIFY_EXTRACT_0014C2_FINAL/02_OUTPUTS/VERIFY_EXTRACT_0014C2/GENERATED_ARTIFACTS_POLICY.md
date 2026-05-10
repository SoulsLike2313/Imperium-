# GENERATED ARTIFACTS POLICY

Generated Python cache files are excluded from source/control bundles.

Excluded patterns:
- __pycache__/
- *.pyc
- *.pyo

Rationale:
- cache files are environment-specific
- cache files are not source authority
- cache files should not affect registry trust or cleanhash checks
