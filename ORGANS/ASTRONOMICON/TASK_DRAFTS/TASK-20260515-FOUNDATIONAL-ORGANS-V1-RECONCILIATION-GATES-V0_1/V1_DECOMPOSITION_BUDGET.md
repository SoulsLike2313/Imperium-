# V1 Decomposition Budget

## Target structure
- 1 General Task.
- Target 6 Local Tasks.
- Acceptable range: 6-9 Local Tasks.
- Target approximately 20 stages total.

## Warning and stop thresholds
- Hard warning above 45 stages.
- Each Local Task target: 3-6 stages.
- Owner gate is required after each Local Task.

## Stage composition constraints
- A stage must not combine schema creation and dependent implementation.
- A stage must not mix organ ownership boundaries.
- A stage must not combine dashboard UI polish with backend truth implementation.

## Replan stop conditions
- stage count breaches budget threshold;
- unresolved ownership collision appears;
- critical gate cannot be satisfied with current decomposition;
- blocker cascade indicates incorrect task partitioning.
