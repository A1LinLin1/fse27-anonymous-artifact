# Model-assisted Reproducible Evidence Protocol

## Goal and evidence layers

This protocol reduces manual source-code labeling while preserving a clear distinction between repeatable model output and independently executable evidence.

| Layer | Scope | Source | Permitted name |
|---|---:|---|---|
| Controlled Gold | 80 mutation v4 cases | frozen mutation oracle | gold |
| Model-assisted Silver | 344 held-out operations | frozen five-model panel and deterministic consensus | silver labels |
| Reproduction-verified Gold | selected real-world cases | frozen source, isolated local execution, commands and logs | gold set |

Model agreement is not correctness. Fleiss' kappa measures agreement among model raters; it must not be presented as accuracy. No all-344 real-world precision, recall, or F1 claim may be labeled human-gold unless all required labels are independently reviewed and adjudicated.

## Frozen model panel

Every model request must record the task bundle hash, system-prompt hash, user-template hash, schema hash, provider, requested model, returned model, upstream provider, request identifier, token use, and raw response hash. The panel must not see Security-ADG output, static-scanner provenance, reviewer03 output, baseline output, or any human label.

For an atomic categorical label, the consensus rule is fixed before execution:

```text
high-confidence consensus = at least 4 of 5 successful model annotations
                             choose the same non-uncertain value
otherwise                = unresolved
```

The full response, including the rationale, remains an auditable local artifact. Public releases contain only prompts, schemas, hashes, aggregate statistics, and any disclosure-safe derived labels.

## Reproduction queue

The queue is built without human labels and uses a fixed, conservative policy:

1. include every high-confidence `dependency_confirmed=true` item;
2. include every high-confidence `weakness_present=true` item;
3. include every `likely` or `confirmed` model vulnerability status;
4. include a fixed-seed, stratified sample of consensus-negative items;
5. include a fixed-seed, stratified sample of unresolved items.

The two sample classes prevent a positive-only case series. Their quotas and seed are recorded in the queue manifest. A model suggestion is only a proposed local test plan; it is never a reproduction result.

## Reproduction evidence

Every execution is restricted to a locally owned or isolated repository/container. The result record must include the frozen commit, environment/container digest, exact command, safe input, exit status, stdout/stderr hashes, and an outcome:

```text
confirmed | rejected | inconclusive | environment_unavailable
```

`confirmed` means the documented, bounded behavior occurred in the local test. It does not automatically mean a public vulnerability, an affected version range, or a CVE.

## Paper-safe claims

Safe:

> We use a fixed multi-model panel for scalable triage and a separately archived, reproduction-verified case set for real-world evidence.

Not safe:

> Five models agreed, therefore all 344 labels are ground truth.

> A reproduction-confirmed capability automatically establishes an exploitable vulnerability.
