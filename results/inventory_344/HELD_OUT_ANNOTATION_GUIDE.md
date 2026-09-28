# Held-out Independent Annotation Guide

You are reviewing one code location from a frozen repository snapshot. Work from the displayed source evidence and, when needed, the frozen full file. Do not consult other reviewers, model outputs, scanner results, Security-ADG output, or baseline results.

## What to decide

1. **Operation confirmed** — Does this location actually execute or invoke the stated security-sensitive operation?
2. **Agent relevant** — Is this operation in an Agent tool, Agent workflow, MCP-exposed capability, or an Agent-related execution chain? A dangerous API anywhere in the repository is not enough.
3. **Dependency confirmed** — Does a less-trusted or Agent-controlled value actually reach this operation?
   - `true`: direct or clearly transitive data/control dependency is established.
   - `partial`: plausible but incomplete evidence; an unresolved call, alias, or configuration boundary remains.
   - `false`: no such dependency, or a parameter/source is overwritten by a constant before the operation.
   - `uncertain`: the provided frozen code cannot establish the answer.
4. **Trust boundary crossed** — Does the established flow cross from a less-trusted source into a more privileged destination? State the source and destination in the rationale. Use `not_applicable` if no dependency exists.
5. **Guard present** — Is there an explicit validation, authorization, allowlist, policy check, sanitization, or comparable guard? A comment or implicit convention is not a guard.
6. **Weakness present** — Does the available code establish a security weakness? Be conservative: sensitive capability alone is not a weakness.
7. **Vulnerability status** — Select `confirmed`, `likely`, `not_vulnerable`, `insufficient_evidence`, or `not_applicable`. Prefer `insufficient_evidence` over overclaiming a vulnerability.

## Required rationale

For every completed item, write a short rationale identifying the operation, the relevant source/flow (if any), the privilege or trust boundary (if any), and any guard. If a label is uncertain, say exactly what evidence is absent.

## Important distinctions

```text
dangerous API present != Agent-relevant operation
source variable exists != source reaches the operation
dependency-positive != exploitable vulnerability
guard present != guard effective or system secure
```

Do not change the task category, infer labels from a tool name alone, or use external runtime tests. This is a frozen-source code-review study.
