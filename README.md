
# Anonymous Replication Package

This package accompanies the anonymous submission **"Beyond Predefined
Sinks: Security-Aware Dependency Analysis for LLM Agents."**

It contains the supplementary material, the Security-ADG implementation,
framework adapters, deterministic tests, the frozen corpus manifest, aggregate
evaluation outputs, and lightweight reproduction checks. It does **not**
contain the authors' development history, API credentials, third-party source
repositories, or technical details withheld for responsible disclosure.

## Start here

1. Read `SUPPLEMENTARY.pdf` for detailed methodology and audit tables.
2. Run `python scripts/verify_artifact.py` to verify hashes and headline values.
3. Run `python -m unittest discover -s tests -p "test_*.py"` for deterministic tests.
4. Run `python scripts/fetch_repositories.py --dry-run` to inspect the frozen
   repository checkout plan. Remove `--dry-run` only when network access and
   third-party cloning are acceptable.

## Package map

- `corpus/frozen_manifest.csv`: public repository coordinates and immutable commits.
- `scripts/`: method, evaluation, verification, and repository-fetch scripts.
- `tests/`: deterministic unit tests and fixtures.
- `config/`: frozen method, baseline, and microbenchmark configurations.
- `results/`: archived aggregate outputs used by the paper.
- `docs/`: method-level protocols and claim boundaries.

## Claim boundaries

- Static candidates are not vulnerability findings.
- The 22-case reference set contains reproduced security-relevant behaviors,
  not 22 vulnerabilities.
- The 344-operation inventory is finite and incompletely adjudicated; no
  aggregate recovery metrics are reported for it.
- The model panel supports triage only and is not ground truth.

## Environment

The core implementation and verification scripts use Python 3.11+ and the
standard library. Semgrep, CodeQL, Docker, and Graphviz are optional and are
required only for their corresponding baseline or visualization workflows.

See `REPRODUCIBILITY.md` for the longer workflow and `THIRD_PARTY.md` for the
repository-fetch and licensing policy.
