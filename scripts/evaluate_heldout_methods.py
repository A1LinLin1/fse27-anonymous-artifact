"""Score normalized held-out predictions only against an adjudicated gold set."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RECALL_DIR = BASE_DIR / "annotations" / "recall_inventory"
OUTPUT_DIR = BASE_DIR / "analysis" / "heldout"
TARGETS = {
    "operation": lambda labels: labels["operation_confirmed"] == "true" and labels["agent_relevant"] == "true",
    "dependency_strict": lambda labels: labels["dependency_confirmed"] == "true",
    "dependency_inclusive": lambda labels: labels["dependency_confirmed"] in {"true", "partial"},
    "guard": lambda labels: labels["guard_present"] == "true",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def metric(pairs: list[tuple[bool, bool]]) -> dict:
    tp = sum(truth and prediction for truth, prediction in pairs)
    fp = sum(not truth and prediction for truth, prediction in pairs)
    tn = sum(not truth and not prediction for truth, prediction in pairs)
    fn = sum(truth and not prediction for truth, prediction in pairs)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = (2 * precision * recall / (precision + recall)) if precision is not None and recall is not None and precision + recall else None
    return {"support": len(pairs), "tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=RECALL_DIR / "gold_labels.jsonl")
    parser.add_argument("--tasks", type=Path, default=RECALL_DIR / "reviewer_a_tasks.jsonl")
    parser.add_argument("--predictions", type=Path, action="append", required=True, help="standardized prediction JSONL; repeat per method")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    if not args.gold.exists():
        raise SystemExit(f"gold set not available: {args.gold}; refusing to create held-out metrics")
    tasks = {row["task_id"]: row for row in read_jsonl(args.tasks)}
    gold = {row["task_id"]: row["adjudicated"] for row in read_jsonl(args.gold)}
    if len(tasks) != 344 or set(tasks) != set(gold):
        raise SystemExit("gold set must cover exactly the 344 frozen held-out tasks")
    predictions: dict[tuple[str, str], dict[str, bool]] = defaultdict(dict)
    for path in args.predictions:
        for row in read_jsonl(path):
            key = (row["method"], row["task"])
            if row["task"] not in TARGETS or not isinstance(row.get("prediction"), bool):
                continue
            if row["task_id"] in predictions[key]:
                raise SystemExit(f"duplicate prediction for {key} / {row['task_id']}")
            predictions[key][row["task_id"]] = row["prediction"]
    main_rows, group_rows = [], []
    for (method, target), values in sorted(predictions.items()):
        if set(values) != set(tasks):
            raise SystemExit(f"silent missing predictions for {method}/{target}: {len(values)} of {len(tasks)}")
        pairs = [(TARGETS[target](gold[task_id]), values[task_id]) for task_id in tasks]
        main_rows.append({"method": method, "target": target, **metric(pairs)})
        for grouping, key in (("repository", "repository"), ("language", "language"), ("category", "operation_category")):
            groups: dict[str, list[tuple[bool, bool]]] = defaultdict(list)
            for task_id, task in tasks.items():
                groups[task[key]].append((TARGETS[target](gold[task_id]), values[task_id]))
            group_rows.extend({"grouping": grouping, "group": name, "method": method, "target": target, **metric(group_pairs)} for name, group_pairs in sorted(groups.items()))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = {"status": "completed", "gold_records": len(gold), "metrics": main_rows, "label_inputs_used": True, "frozen_method_version": "v2.4"}
    (args.output_dir / "method_comparison.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.output_dir / "method_comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("method", "target", "support", "tp", "fp", "tn", "fn", "precision", "recall", "f1")); writer.writeheader(); writer.writerows(main_rows)
    for grouping, filename in (("repository", "per_repository.csv"), ("language", "per_language.csv"), ("category", "per_category.csv")):
        rows = [row for row in group_rows if row["grouping"] == grouping]
        with (args.output_dir / filename).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=("group", "method", "target", "support", "tp", "fp", "tn", "fn", "precision", "recall", "f1")); writer.writeheader(); writer.writerows([{key: value for key, value in row.items() if key != "grouping"} for row in rows])
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
