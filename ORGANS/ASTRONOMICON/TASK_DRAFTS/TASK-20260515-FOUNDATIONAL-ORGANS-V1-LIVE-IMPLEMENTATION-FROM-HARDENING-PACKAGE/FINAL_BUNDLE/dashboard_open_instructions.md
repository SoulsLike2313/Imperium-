# Dashboard Open Instructions

Open these local static dashboards directly from filesystem:
- `ORGANS/ASTRONOMICON/DASHBOARD_V1/index.html`
- `ORGANS/ADMINISTRATUM/DASHBOARD_V1/index.html`
- `ORGANS/OFFICIO_AGENTIS/DASHBOARD_V1/index.html`
- `ORGANS/DOCTRINARIUM/DASHBOARD_V1/index.html`
- `SANCTUM/FOUNDATIONAL_ORGANS_V1/index.html`

Run these checks from repo root:
- `py -3 scripts/foundational_organs_v1/check_foundational_organs_v1_no_fake_green.py`
- `py -3 scripts/foundational_organs_v1/check_foundational_organs_v1_stale_status.py`
- `py -3 scripts/foundational_organs_v1/check_foundational_organs_v1_repo_purity_utf8.py`
- `py -3 scripts/foundational_organs_v1/run_foundational_organs_v1_e2e_proof.py`
