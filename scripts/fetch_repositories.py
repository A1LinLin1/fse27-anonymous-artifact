#!/usr/bin/env python3
"""Fetch public corpus repositories at frozen commits without shell=True."""
from __future__ import annotations
import argparse, csv, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "corpus" / "frozen_manifest.csv")
    parser.add_argument("--destination", type=Path, default=ROOT / "dataset" / "repos")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows = list(csv.DictReader(args.manifest.open(encoding="utf-8")))
    for index, row in enumerate(rows, 1):
        target = args.destination / row["sample_id"]
        print(f"[{index}/{len(rows)}] {row['repo']} @ {row['git_commit']} -> {target}")
        if args.dry_run:
            continue
        if target.exists():
            raise SystemExit(f"refusing to overwrite existing path: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", row["url"], str(target)], check=True)
        subprocess.run(["git", "-C", str(target), "checkout", "--detach", row["git_commit"]], check=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
