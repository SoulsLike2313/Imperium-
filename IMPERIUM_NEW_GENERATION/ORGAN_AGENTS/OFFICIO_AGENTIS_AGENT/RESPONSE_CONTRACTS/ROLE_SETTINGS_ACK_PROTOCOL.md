# ROLE SETTINGS ACK PROTOCOL

## Purpose
Before serious Officio-controlled work, an agent must be able to acknowledge which role, mode, settings, restrictions, stop conditions, and response contract it received.

## ACK_ROLE Shape
ACK_ROLE:
- agent_id:
- role_name:
- role_family:
- operating_nature:
- default_mode:
- role_profile_path:
- role_profile_hash:
- timestamp_utc:

## ACK_SETTINGS Shape
ACK_SETTINGS:
- agent_id:
- role_name:
- active_mode:
- permissions_ref:
- forbidden_actions_ref:
- stop_conditions_ref:
- evidence_policy_ref:
- response_contract_ref:
- settings_hash:
- timestamp_utc:

## Failure Rule
If role/settings ACK is required but missing, Servitor must stop with:

VERDICT: BLOCKED_OFFICIO_ACK_MISSING

## Evidence Rule
ACK files should be saved into the task run evidence folder when execution is launched through Officio.
