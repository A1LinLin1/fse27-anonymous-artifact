# Held-out Annotation Operations

This is the operational companion to `annotations/recall_inventory/HELD_OUT_ANNOTATION_GUIDE.md`. Run it only after `scripts/validate_heldout_evaluation.py --allow-pending-labels` reports a pending-label pass.

## Reviewer isolation

Give reviewer A only the A URL and reviewer B only the B URL. Do not share a browser profile, label file, model output, Security-ADG output, reviewer03 output, or baseline output between them.

Start reviewer A locally:

```powershell
python scripts/serve_heldout_annotation.py --reviewer a --host 127.0.0.1 --port 8766
```

Start reviewer B in a separate terminal or machine:

```powershell
python scripts/serve_heldout_annotation.py --reviewer b --host 127.0.0.1 --port 8767
```

The service creates `reviewer_a_labels.jsonl` or `reviewer_b_labels.jsonl` on first start. A completed task is locked by the UI; a correction must be recorded through the study coordinator rather than silently overwriting a completed label.

## Safe handoff

If a reviewer works on another machine, provide that reviewer with only their own task bundle and an isolated copy of the UI/server, or expose exactly one reviewer-specific server through an authenticated private channel. Do not put either label file in the public repository.

Before annotation, verify task bundles have not changed:

```powershell
python scripts/freeze_heldout_experiment.py --check
python scripts/freeze_heldout_annotation_bundle.py --check
python scripts/validate_heldout_evaluation.py --allow-pending-labels
```

After both reviewers have completed all 344 tasks, stop the servers and run:

```powershell
python scripts/validate_heldout_evaluation.py
python scripts/analyze_heldout_human_agreement.py
python scripts/build_heldout_adjudication_tasks.py
```

Agreement must be computed before adjudication. Do not export or compare the two label files before that point.
