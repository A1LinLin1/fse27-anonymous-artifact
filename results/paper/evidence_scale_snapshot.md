# Evidence Scale Snapshot

This snapshot answers how much evidence exists at each strength level. It is not a single benchmark metric.

| Layer | N | Unit | Strength | Supports | Does not support |
| --- | ---: | --- | --- | --- | --- |
| Frozen corpus | 67 | repositories | dataset | Benchmark scale and ecosystem coverage | Behavior/vulnerability prevalence by itself |
| Full-corpus raw static scan | 25953 | raw candidate hits | candidate_generation | Scale of operation discovery input | Vulnerability count or confirmed security behavior |
| Five-model annotation panel | 750 | model calls | model_panel | Breadth of model-assisted screening | Independent ground truth |
| Reviewer03 model-assisted audit | 150 | reviewed tasks | single_reviewer_provisional | Larger provisional label distribution and case selection | Blind human agreement or final gold labels |
| Provisional development diagnostic | 50 | reviewed development tasks | development_diagnostic | Early method diagnostics against provisional labels | Final held-out performance |
| Held-out operation inventory | 344 | operation inventory records | unadjudicated_inventory | Recall-study worklist scale | Recall denominator until adjudicated |
| Held-out model-assisted silver labels | 256 | silver-labeled tasks | model_assisted_silver | Large-scale sensitivity analysis and prioritization | Human gold or final benchmark metrics |
| Agent ALR/ASE reviewed cases | 14 | reviewed agent cases | reviewed_case_evidence | Positive/downgraded case-study evidence and sink-only over-reporting analysis | Full-corpus automatic detection accuracy |
| Held-out reproduction cases | 9 | local/source reproduction cases | reproduction_backed_case_study | Qualitative RQ3/RQ4 case studies and representation ablation | Precision/recall or vulnerability prevalence |

## Key Takeaways

- The project is not limited to 14 cases: the 14 reviewed cases are the strongest agent-case layer.
- The broader evidence includes 150 reviewer03 model-assisted audit tasks and a 344-record held-out operation inventory.
- The 256-task silver held-out labels can support sensitivity analysis, but not final gold metrics.
- The current persuasive gap is not collection size; it is independent adjudication and held-out evaluation strength.
