# Held-out Gold-set Definition

This document fixes the labels and derived targets for the held-out real-world evaluation. It applies only to the two frozen repositories and the 344-record inventory named in `artifacts/freeze/experiment_freeze_manifest.json`.

## Source of truth

The gold set is created only after two independent, blinded human annotations and subsequent adjudication. Model-panel votes, reviewer03 output, Security-ADG predictions, static-scanner metadata, and baseline output are not labels and must not be used to fill missing human labels.

The reviewer A and reviewer B source files remain immutable. `gold_labels.jsonl` preserves both original judgments and records the adjudicated values separately.

## Field values

- `operation_confirmed`: `true`, `false`, `uncertain`
- `agent_relevant`: `true`, `false`, `uncertain`
- `dependency_confirmed`: `true`, `partial`, `false`, `uncertain`
- `trust_boundary_crossed`: `true`, `false`, `uncertain`, `not_applicable`
- `guard_present`: `true`, `false`, `uncertain`
- `weakness_present`: `true`, `false`, `uncertain`
- `vulnerability_status`: `confirmed`, `likely`, `not_vulnerable`, `insufficient_evidence`, `not_applicable`

## Evaluation targets

Operation-positive is:

```text
operation_confirmed == true AND agent_relevant == true
```

Strict dependency-positive is:

```text
dependency_confirmed == true
```

Inclusive dependency-positive, used only as a sensitivity analysis, is:

```text
dependency_confirmed IN {true, partial}
```

Guard evidence is evaluated against `guard_present == true`. Uncertain and not-applicable values are never silently converted to positive or negative. The primary complete-case analysis excludes such cells; a separately labeled sensitivity analysis reports the alternative treatment.

## Interpretation boundary

A dependency-positive operation is not automatically a vulnerability. A `confirmed` vulnerability requires complete contextual evidence and is reported separately from operation and dependency metrics. Candidate counts, operation positives, dependency positives, and vulnerability positives are distinct quantities.
