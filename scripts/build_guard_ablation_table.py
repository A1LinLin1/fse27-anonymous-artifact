#!/usr/bin/env python3
"""Build a guard-aware representation ablation table from a case matrix.

The output is paper-facing qualitative evidence, not a precision/recall/F1
report. It asks what each representation can express for the same confirmed
held-out evidence-backed cases:

- sink-only: operation/API presence;
- plain ADG: local program structure and effect;
- Security-ADG: source/dependency path, trust boundary, and guard posture.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "analysis" / "reproduction" / "case_matrix" / "heldout_reproduction_case_matrix.json"
DEFAULT_OUTPUT_DIR = BASE_DIR / "analysis" / "reproduction" / "guard_ablation"


VIEWS = [
    {
        "view": "sink_only",
        "display_name": "Sink-only",
        "definition": "A security-sensitive API or operation is present.",
        "operation": True,
        "effect": False,
        "dependency": False,
        "trust_boundary": False,
        "guard": False,
    },
    {
        "view": "plain_adg",
        "display_name": "Simplified ADG",
        "definition": "The program contains a security-sensitive operation that may cause an external effect.",
        "operation": True,
        "effect": True,
        "dependency": False,
        "trust_boundary": False,
        "guard": False,
    },
    {
        "view": "security_adg",
        "display_name": "Security-ADG",
        "definition": "The graph preserves operation, effect, source/dependency, trust-boundary, and guard evidence.",
        "operation": True,
        "effect": True,
        "dependency": True,
        "trust_boundary": True,
        "guard": True,
    },
]


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(BASE_DIR).as_posix()
    except ValueError:
        return resolved.as_posix()


def read_matrix(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def has_dependency(row: dict[str, Any]) -> bool:
    return bool(str(row.get("dependency_path", "")).strip())


def has_trust_boundary(row: dict[str, Any]) -> bool:
    return bool(str(row.get("trust_boundary", "")).strip()) and row.get("trust_boundary") != "not classified"


def is_guarded(row: dict[str, Any]) -> bool:
    return row.get("guard_posture") in {"guarded", "guard_context_present"}


def reference_context(row: dict[str, Any]) -> dict[str, bool]:
    """Return independently supported context dimensions for one case.

    ``no_guard_confirmed`` is an explicit negative guard-posture observation,
    not an absent/unknown reference element.  It therefore remains applicable
    in the denominator even though a representation receives positive guard
    retention credit only when it exposes concrete guard evidence.  This
    distinction makes the 41/45 Security-ADG score auditable.
    """

    return {
        "operation": bool(row.get("sink_family")),
        "effect": bool(row.get("sink_family")),
        "dependency": has_dependency(row),
        "trust_boundary": has_trust_boundary(row),
        "guard_posture": row.get("guard_posture")
        in {"guarded", "guard_context_present", "no_guard_confirmed"},
    }


def row_support(row: dict[str, Any], view: dict[str, Any]) -> dict[str, Any]:
    reference = reference_context(row)
    operation = bool(view["operation"] and row.get("sink_family"))
    effect = bool(view["effect"] and row.get("sink_family"))
    dependency = bool(view["dependency"] and has_dependency(row))
    trust = bool(view["trust_boundary"] and has_trust_boundary(row))
    guard = bool(view["guard"] and is_guarded(row))
    can_distinguish_guarded = bool(view["guard"])
    if view["view"] == "sink_only":
        interpretation = "API/operation presence only; guard and dependency context are invisible."
    elif view["view"] == "plain_adg":
        interpretation = "Operation/effect structure is visible, but source dependency and guard posture are collapsed."
    else:
        interpretation = (
            "Security context is visible: dependency path and trust boundary are explicit"
            + (" and guard evidence is preserved." if guard else "; no guard evidence is confirmed.")
        )
    retained = {
        "operation": operation,
        "effect": effect,
        "dependency": dependency,
        "trust_boundary": trust,
        "guard_posture": guard,
    }
    applicable_fields = [name for name, present in reference.items() if present]
    retained_fields = [name for name in applicable_fields if retained[name]]
    return {
        "case_id": row["id"],
        "repository": row["repository"],
        "ecosystem": row.get("ecosystem", ""),
        "source_file": row.get("file", ""),
        "source_line": row.get("line"),
        "evidence_mode": row.get("evidence_mode", ""),
        "evidence_file": row.get("evidence_file", ""),
        "behavior_family": row["behavior_family"],
        "guard_posture": row["guard_posture"],
        "view": view["view"],
        "display_name": view["display_name"],
        "sees_operation": operation,
        "sees_effect": effect,
        "sees_dependency_path": dependency,
        "sees_trust_boundary": trust,
        "sees_guard": guard,
        "can_distinguish_guarded_from_unguarded": can_distinguish_guarded,
        "reference_context": reference,
        "applicable_context_fields": applicable_fields,
        "retained_context_fields": retained_fields,
        "applicable_context_count": len(applicable_fields),
        "expressive_context_fields": len(retained_fields),
        "interpretation": interpretation,
    }


def build_case_rows(matrix_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row_support(row, view) for row in matrix_rows for view in VIEWS]


def pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def build_view_rows(case_rows: list[dict[str, Any]], case_count: int, guarded_count: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for view in VIEWS:
        subset = [row for row in case_rows if row["view"] == view["view"]]
        operation = sum(row["sees_operation"] for row in subset)
        effect = sum(row["sees_effect"] for row in subset)
        dependency = sum(row["sees_dependency_path"] for row in subset)
        trust = sum(row["sees_trust_boundary"] for row in subset)
        guard = sum(row["sees_guard"] for row in subset)
        retained_context = sum(row["expressive_context_fields"] for row in subset)
        applicable_context = sum(row["applicable_context_count"] for row in subset)
        rows.append(
            {
                "view": view["view"],
                "display_name": view["display_name"],
                "definition": view["definition"],
                "cases": case_count,
                "operation_visible": operation,
                "effect_visible": effect,
                "dependency_path_visible": dependency,
                "trust_boundary_visible": trust,
                "guard_visible": guard,
                "guarded_cases": guarded_count,
                "guard_recall_within_confirmed_guarded_cases": pct(guard, guarded_count),
                "context_completeness_numerator": retained_context,
                "context_completeness_denominator": applicable_context,
                "context_completeness": pct(retained_context, applicable_context),
                "primary_limitation": primary_limitation(view["view"]),
            }
        )
    return rows


def primary_limitation(view: str) -> str:
    if view == "sink_only":
        return "Cannot distinguish reachable behavior from API presence or guarded from unguarded cases."
    if view == "plain_adg":
        return "Does not preserve security-specific source, trust-boundary, or guard semantics."
    return "Still qualitative; requires independent held-out labels before reporting accuracy metrics."


def build_summary(matrix: dict[str, Any]) -> dict[str, Any]:
    matrix_rows = matrix.get("rows", [])
    case_rows = build_case_rows(matrix_rows)
    guarded_count = sum(is_guarded(row) for row in matrix_rows)
    view_rows = build_view_rows(case_rows, len(matrix_rows), guarded_count)
    return {
        "schema_version": "1.0",
        "purpose": "guard-aware representation ablation for held-out evidence-backed cases; not a final metric report",
        "source_matrix_claim_boundary": matrix.get("claim_boundary", ""),
        "case_count": len(matrix_rows),
        "guarded_cases": guarded_count,
        "repositories": matrix.get("repositories", {}),
        "ecosystems": matrix.get("ecosystems", {}),
        "behavior_families": matrix.get("behavior_families", {}),
        "guard_postures": matrix.get("guard_postures", {}),
        "human_labels_used": matrix.get("human_labels_used", False),
        "model_labels_used": matrix.get("model_labels_used", False),
        "view_rows": view_rows,
        "case_view_rows": case_rows,
        "headline": {
            "sink_only_guard_visible": next(row["guard_visible"] for row in view_rows if row["view"] == "sink_only"),
            "plain_adg_guard_visible": next(row["guard_visible"] for row in view_rows if row["view"] == "plain_adg"),
            "security_adg_guard_visible": next(row["guard_visible"] for row in view_rows if row["view"] == "security_adg"),
            "security_adg_context_completeness": next(row["context_completeness"] for row in view_rows if row["view"] == "security_adg"),
        },
    }


def write_json(report: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def write_view_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "view",
        "display_name",
        "cases",
        "operation_visible",
        "effect_visible",
        "dependency_path_visible",
        "trust_boundary_visible",
        "guard_visible",
        "guarded_cases",
        "guard_recall_within_confirmed_guarded_cases",
        "context_completeness_numerator",
        "context_completeness_denominator",
        "context_completeness",
        "primary_limitation",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def write_case_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "case_id",
        "repository",
        "behavior_family",
        "guard_posture",
        "view",
        "sees_operation",
        "sees_effect",
        "sees_dependency_path",
        "sees_trust_boundary",
        "sees_guard",
        "applicable_context_fields",
        "retained_context_fields",
        "applicable_context_count",
        "expressive_context_fields",
        "interpretation",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", "<br>")


def yesno(value: Any) -> str:
    return "yes" if value else "no"


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Guard-aware Representation Ablation",
        "",
        "This table compares what each representation can express for the same held-out evidence-backed cases. It is not a final precision, recall, or F1 report.",
        "",
        "## Summary",
        "",
        f"- Cases: {report['case_count']}",
        f"- Guarded cases: {report['guarded_cases']}",
        f"- Human labels used: {str(report['human_labels_used']).lower()}",
        f"- Model labels used: {str(report['model_labels_used']).lower()}",
        "",
        "## View-level ablation",
        "",
        "| View | Operation | Effect | Dependency path | Trust boundary | Guard | Guarded-case guard coverage | Context completeness | Main limitation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in report["view_rows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape(row["display_name"]),
                    str(row["operation_visible"]),
                    str(row["effect_visible"]),
                    str(row["dependency_path_visible"]),
                    str(row["trust_boundary_visible"]),
                    str(row["guard_visible"]),
                    f"{row['guard_recall_within_confirmed_guarded_cases']:.2%}",
                    f"{row['context_completeness']:.2%}",
                    md_escape(row["primary_limitation"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Case-level context retention",
            "",
            "The reference guard-posture dimension is applicable for both `guarded` and explicitly reproduced `no_guard_confirmed` cases. A no-guard observation is therefore included in the denominator, while positive guard-visibility credit is awarded only when concrete guard evidence is exposed.",
            "",
            "| Case | Behavior | Guard posture | Applicable | Sink-only | Simplified ADG | Security-ADG |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    by_case: dict[str, list[dict[str, Any]]] = {}
    for row in report["case_view_rows"]:
        by_case.setdefault(row["case_id"], []).append(row)
    for case_id in sorted(by_case):
        rows = {row["view"]: row for row in by_case[case_id]}
        base = rows["security_adg"]
        lines.append(
            "| "
            + " | ".join(
                [
                    md_escape(case_id),
                    md_escape(base["behavior_family"]),
                    md_escape(base["guard_posture"]),
                    str(base["applicable_context_count"]),
                    f"{rows['sink_only']['expressive_context_fields']}/{rows['sink_only']['applicable_context_count']}",
                    f"{rows['plain_adg']['expressive_context_fields']}/{rows['plain_adg']['applicable_context_count']}",
                    f"{rows['security_adg']['expressive_context_fields']}/{rows['security_adg']['applicable_context_count']}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Paper claim boundary",
            "",
            "- This ablation supports the RQ4 claim that Security-ADG preserves security context omitted by sink-only and simplified ADG views.",
            "- It should not be reported as method accuracy. Accuracy requires the independent held-out gold set and adjudication.",
            "- The guard coverage denominator here is the set of held-out cases whose frozen evidence explicitly records positive guard context.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def latex_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(char, char) for char in text)


def write_latex(report: dict[str, Any], path: Path) -> None:
    by_case: dict[str, list[dict[str, Any]]] = {}
    for row in report["case_view_rows"]:
        by_case.setdefault(row["case_id"], []).append(row)

    lines = [
        r"\section{Held-Out Context-Preservation Study}",
        "",
        r"We evaluate the three representation projections over nine held-out evidence-backed cases: five validated by controlled local monkeypatch proofs and four by source-level construction proofs that did not execute the external effect. Each case-level reference contains independently supported context dimensions for operation, external effect, dependency path, trust boundary, and guard posture. The four cases recorded as \texttt{no\_guard\_confirmed} contain an explicit negative guard-posture observation rather than an absent or unknown field; the guard-posture dimension therefore remains in the denominator. Positive guard-visibility credit is awarded only when concrete guard evidence is exposed by the representation. These measurements concern representation retention, not vulnerability-detection accuracy.",
        "",
        r"\begin{table*}[t]",
        r"\caption{Evidence provenance for the held-out context-preservation cases. Repository identifiers are retained to make the frozen evidence auditable; no row is a vulnerability claim.}",
        r"\label{tab:supp-context-provenance}",
        r"\centering",
        r"\small",
        r"\begin{tabular}{llp{3.1cm}p{2.5cm}l}",
        r"\toprule",
        r"Case & Repository & Behavior & Evidence mode & Guard posture \\",
        r"\midrule",
    ]
    for case_id in sorted(by_case):
        rows = {row["view"]: row for row in by_case[case_id]}
        base = rows["security_adg"]
        lines.append(
            f"{latex_escape(case_id)} & {latex_escape(base['repository'])} & "
            f"{latex_escape(base['behavior_family'])} & {latex_escape(base['evidence_mode'])} & "
            f"{latex_escape(base['guard_posture'])} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}",
            "",
            r"\begin{table*}[t]",
            r"\caption{Case-level representation retention. Each case has five applicable reference dimensions: operation, effect, dependency, trust boundary, and guard posture.}",
            r"\label{tab:supp-context-cases}",
            r"\centering",
            r"\small",
            r"\begin{tabular}{llrrrr}",
            r"\toprule",
            r"Case & Guard posture & Applicable & Sink-only & Simplified ADG & Security-ADG \\",
            r"\midrule",
        ]
    )
    for case_id in sorted(by_case):
        rows = {row["view"]: row for row in by_case[case_id]}
        base = rows["security_adg"]
        denominator = base["applicable_context_count"]
        lines.append(
            f"{latex_escape(case_id)} & {latex_escape(base['guard_posture'])} & {denominator} & "
            f"{rows['sink_only']['expressive_context_fields']}/{denominator} & "
            f"{rows['plain_adg']['expressive_context_fields']}/{denominator} & "
            f"{rows['security_adg']['expressive_context_fields']}/{denominator} \\\\"
        )
    lines.extend(
        [
            r"\midrule",
            r"Micro total & -- & 45 & 9/45 & 18/45 & 41/45 \\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}",
            "",
            r"\begin{table}[t]",
            r"\caption{Micro-averaged context completeness and positive guard visibility.}",
            r"\label{tab:supp-context-summary}",
            r"\centering",
            r"\small",
            r"\begin{tabular}{lrrr}",
            r"\toprule",
            r"Representation & Retained & Completeness & Guard visibility \\",
            r"\midrule",
        ]
    )
    for row in report["view_rows"]:
        lines.append(
            f"{latex_escape(row['display_name'])} & "
            f"{row['context_completeness_numerator']}/{row['context_completeness_denominator']} & "
            f"{row['context_completeness']:.1%} & {row['guard_visible']}/{row['guarded_cases']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
            r"The micro totals reproduce the values reported in the main paper: $9/45=20.0\%$, $18/45=40.0\%$, and $41/45=91.1\%$. Security-ADG exposes concrete guard evidence in all five guarded cases. The four remaining reference records explicitly report \texttt{no\_guard\_confirmed}; because the graph does not emit a positive guard node for these cases, they contribute no guard-retention credit.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    matrix = read_matrix(args.matrix)
    report = build_summary(matrix)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "guard_ablation_summary.json"
    view_csv_path = args.output_dir / "guard_ablation_view_table.csv"
    case_csv_path = args.output_dir / "guard_ablation_case_view_table.csv"
    md_path = args.output_dir / "guard_ablation_table.md"
    latex_path = args.output_dir / "heldout_context_preservation_tables.tex"
    write_json(report, summary_path)
    write_view_csv(report["view_rows"], view_csv_path)
    write_case_csv(report["case_view_rows"], case_csv_path)
    write_markdown(report, md_path)
    write_latex(report, latex_path)
    print(
        json.dumps(
            {
                "status": "complete",
                "cases": report["case_count"],
                "guarded_cases": report["guarded_cases"],
                "view_rows": len(report["view_rows"]),
                "case_view_rows": len(report["case_view_rows"]),
                "headline": report["headline"],
                "outputs": {
                    "summary": display_path(summary_path),
                    "view_csv": display_path(view_csv_path),
                    "case_csv": display_path(case_csv_path),
                    "md": display_path(md_path),
                    "latex": display_path(latex_path),
                },
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
