# Action Safety Contract

## Objective
Ensure every operator action is explicitly registered, scoped, and safety-rated before UI exposure.

## Action Types
- `READ_ONLY`: non-mutating inspections.
- `CHECK`: verification scripts that may generate reports/receipts.
- `EXPORT`: controlled data packaging actions.
- `MUTATING_DISABLED`: declared future actions, intentionally disabled.

## Policy Rules
1. UI buttons may call only action ids registered in `neural_action_registry.json`.
2. Mutating actions are disabled by default unless all of the following are true:
   - owner gate is true;
   - scope path is explicit;
   - proof-writing behavior is defined.
3. Dangerous filesystem or git mutation commands are forbidden from active actions.
4. Every enabled action must document whether it writes receipts or reports.

## Owner Gate
- `owner_gate_required: true` means action cannot be treated as autonomous.
- Even read-only actions should preserve proof traces when possible.

## Current V0.4 Stance
- This base enables safe read/check/export paths only.
- Mutation pathways remain declared but disabled.

