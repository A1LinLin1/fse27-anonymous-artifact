"""Build a blinded-review inventory for an exhaustive held-out recall study.

The inventory combines the frozen scanner's candidates with a deliberately
separate lexical operation lexicon.  It is a review frame, not a ground truth
file: every entry remains unlabelled until independent human inspection.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import tarfile
from collections import Counter
from pathlib import Path, PurePosixPath


BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx"}
DEFAULT_REPOS = ("dddabtc/winremote-mcp", "nexu-io/html-anything")
LEXICON = (
    ("command_execution", re.compile(r"\b(?:subprocess\.(?:run|Popen|call|check_call|check_output)|os\.system|child_process\.(?:exec|execFile|spawn)|(?:exec|spawn)\s*\()")),
    ("dynamic_code_execution", re.compile(r"\b(?:eval|exec)\s*\(|\bnew\s+Function\s*\(")),
    ("network_access", re.compile(r"\b(?:requests\.(?:get|post|put|delete)|httpx\.|urllib\.|fetch\s*\(|axios\.)")),
    ("filesystem_write", re.compile(r"\b(?:write_text|write_bytes|writeFile(?:Sync)?|\.write\s*\()")),
    ("filesystem_read", re.compile(r"\b(?:read_text|read_bytes|readFile(?:Sync)?|\.read\s*\()")),
    ("external_tool_invocation", re.compile(r"\b(?:browser\.(?:goto|click|navigate)|playwright\.|selenium\.)")),
)


def archive_sources(repository: Path, commit: str) -> dict[str, str]:
    process = subprocess.run(
        ["git", "-c", f"safe.directory={repository.as_posix()}", "-C", str(repository), "archive", "--format=tar", commit],
        capture_output=True, check=False,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.decode("utf-8", errors="replace").strip())
    sources: dict[str, str] = {}
    with tarfile.open(fileobj=io.BytesIO(process.stdout), mode="r:") as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if not member.isfile() or path.suffix.lower() not in SOURCE_EXTENSIONS:
                continue
            extracted = archive.extractfile(member)
            if extracted is not None:
                sources[path.as_posix()] = extracted.read().decode("utf-8", errors="replace")
    return sources


def context(text: str, line: int, radius: int) -> dict:
    lines = text.splitlines()
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    return {"line_start": start, "line_end": end, "text": "\n".join(f"{index}: {lines[index - 1]}" for index in range(start, end + 1))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=BASE_DIR / "dataset" / "corpus_manifest.csv")
    parser.add_argument("--findings", type=Path, default=BASE_DIR / "analysis" / "full_corpus_static_findings_v1.jsonl")
    parser.add_argument("--repo", action="append", default=[])
    parser.add_argument("--output", type=Path, default=BASE_DIR / "annotations" / "recall_inventory" / "held_out_operation_inventory.jsonl")
    parser.add_argument("--summary", type=Path, default=BASE_DIR / "annotations" / "recall_inventory" / "held_out_operation_inventory_summary.json")
    parser.add_argument("--context-radius", type=int, default=3)
    args = parser.parse_args()
    selected_repos = tuple(args.repo or DEFAULT_REPOS)
    with args.manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        metadata = {row["repo"]: row for row in csv.DictReader(handle)}
    missing = sorted(set(selected_repos) - set(metadata))
    if missing:
        raise SystemExit(f"repositories absent from manifest: {', '.join(missing)}")
    records: dict[tuple[str, str, int, str], dict] = {}
    for line in args.findings.read_text(encoding="utf-8").splitlines():
        finding = json.loads(line)
        if finding["repo"] not in selected_repos:
            continue
        for evidence_line in finding["evidence_lines"]:
            key = (finding["repo"], finding["file"], evidence_line, finding["category"])
            records[key] = {
                "repo": finding["repo"], "sample_id": finding["sample_id"], "commit": finding["git_commit"],
                "file": finding["file"], "line": evidence_line, "behavior_category": finding["category"],
                "discovery_channels": ["static_scanner"],
                "static_candidate_ids": [finding.get("candidate_id", finding.get("annotation_id"))],
                "lexicon_matchers": [], "gold_label": "unlabelled", "requires_independent_human_review": True,
            }
    for repo in selected_repos:
        row = metadata[repo]
        sources = archive_sources(BASE_DIR / row["repository_path"], row["git_commit"])
        for file_name, text in sources.items():
            for line_number, source_line in enumerate(text.splitlines(), start=1):
                for category, pattern in LEXICON:
                    if not pattern.search(source_line):
                        continue
                    key = (repo, file_name, line_number, category)
                    record = records.setdefault(key, {
                        "repo": repo, "sample_id": row["sample_id"], "commit": row["git_commit"],
                        "file": file_name, "line": line_number, "behavior_category": category,
                        "discovery_channels": [], "static_candidate_ids": [], "lexicon_matchers": [],
                        "gold_label": "unlabelled", "requires_independent_human_review": True,
                    })
                    if "independent_operation_lexicon" not in record["discovery_channels"]:
                        record["discovery_channels"].append("independent_operation_lexicon")
                    record["lexicon_matchers"].append(pattern.pattern)
        for record in records.values():
            if record["repo"] == repo and record["file"] in sources:
                record["context"] = context(sources[record["file"]], record["line"], args.context_radius)
    ordered = sorted(records.values(), key=lambda item: (item["repo"], item["file"], item["line"], item["behavior_category"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in ordered), encoding="utf-8")
    summary = {
        "scope": "unlabelled held-out operation inventory for an exhaustive recall study",
        "repos": list(selected_repos), "records": len(ordered),
        "by_repo": dict(sorted(Counter(item["repo"] for item in ordered).items())),
        "by_category": dict(sorted(Counter(item["behavior_category"] for item in ordered).items())),
        "discovery_channels": dict(sorted(Counter(channel for item in ordered for channel in item["discovery_channels"]).items())),
        "gold_labels_present": False,
        "warning": "This inventory is not a recall gold set until independently reviewed and adjudicated.",
    }
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
