
# Reproducibility workflow

## Fast verification (no network, no third-party source)

```bash
python scripts/verify_artifact.py
python -m unittest discover -s tests -p "test_*.py"
```

The first command verifies package hashes and independently recomputes the
headline corpus and representation-study quantities from archived JSON/CSV.

## Frozen corpus checkout

```bash
python scripts/fetch_repositories.py --dry-run
python scripts/fetch_repositories.py --destination dataset/repos
```

The second command performs network access and checks out public third-party
repositories at the commits in `corpus/frozen_manifest.csv`. Third-party source
is intentionally not redistributed in this package.

## Full analysis

After fetching repositories, adapt the manifest repository paths to the local
checkout root and run:

```bash
python scripts/run_security_adg_pipeline.py --manifest corpus/frozen_manifest.csv --scope all_corpus --analysis-mode v2_5 --output-root work/full_run
```

The archived aggregate outputs used in the paper are under `results/`.
Runtime measurements are historical observations and are not expected to match
exactly on different hardware.
