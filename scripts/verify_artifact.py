#!/usr/bin/env python3
"""Verify package integrity and recompute headline reported quantities."""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    failures = []
    for line in (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            failures.append(relative)
    report = json.loads((ROOT / "results" / "corpus_wide" / "corpus_wide_security_adg_report.json").read_text(encoding="utf-8"))
    population = report["population"]
    expected = {
        "manifest_repositories": 67,
        "candidates": 23866,
        "dependency_path": 9821,
        "guard_candidate": 3075,
    }
    for key, value in expected.items():
        if population.get(key) != value:
            failures.append(f"headline:{key}")
    guard = json.loads((ROOT / "results" / "representation" / "guard_ablation_summary.json").read_text(encoding="utf-8"))
    views = {row["view"]: row for row in guard["view_rows"]}
    checks = {
        "sink_only": (9, 45),
        "plain_adg": (18, 45),
        "security_adg": (41, 45),
    }
    for view, pair in checks.items():
        row = views[view]
        actual = (row["context_completeness_numerator"], row["context_completeness_denominator"])
        if actual != pair:
            failures.append(f"representation:{view}")
    manifest = list(csv.DictReader((ROOT / "corpus" / "frozen_manifest.csv").open(encoding="utf-8")))
    if len(manifest) != 67 or len({row["git_commit"] for row in manifest}) != 67:
        failures.append("corpus_manifest")
    if failures:
        raise SystemExit("verification failed: " + ", ".join(failures))
    print(json.dumps({"status": "pass", "files_verified": sum(1 for line in (ROOT / "SHA256SUMS.txt").read_text().splitlines() if line), "repositories": 67, "candidates": 23866, "context_retention": {"sink_only": "9/45", "plain_adg": "18/45", "security_adg": "41/45"}}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
