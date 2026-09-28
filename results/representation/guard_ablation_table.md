# Guard-aware Representation Ablation

This table compares what each representation can express for the same held-out evidence-backed cases. It is not a final precision, recall, or F1 report.

## Summary

- Cases: 9
- Guarded cases: 5
- Human labels used: false
- Model labels used: false

## View-level ablation

| View | Operation | Effect | Dependency path | Trust boundary | Guard | Guarded-case guard coverage | Context completeness | Main limitation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Sink-only | 9 | 0 | 0 | 0 | 0 | 0.00% | 20.00% | Cannot distinguish reachable behavior from API presence or guarded from unguarded cases. |
| Simplified ADG | 9 | 9 | 0 | 0 | 0 | 0.00% | 40.00% | Does not preserve security-specific source, trust-boundary, or guard semantics. |
| Security-ADG | 9 | 9 | 9 | 9 | 5 | 100.00% | 91.11% | Still qualitative; requires independent held-out labels before reporting accuracy metrics. |

## Case-level context retention

The reference guard-posture dimension is applicable for both `guarded` and explicitly reproduced `no_guard_confirmed` cases. A no-guard observation is therefore included in the denominator, while positive guard-visibility credit is awarded only when concrete guard evidence is exposed.

| Case | Behavior | Guard posture | Applicable | Sink-only | Simplified ADG | Security-ADG |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| HSQ-0014 | shell command execution | no_guard_confirmed | 5 | 1/5 | 2/5 | 4/5 |
| HSQ-0087 | application launch | no_guard_confirmed | 5 | 1/5 | 2/5 | 4/5 |
| HSQ-0089 | desktop notification script | guarded | 5 | 1/5 | 2/5 | 5/5 |
| HSQ-0091 | network diagnostic process | no_guard_confirmed | 5 | 1/5 | 2/5 | 4/5 |
| HSQ-0103 | service control | guarded | 5 | 1/5 | 2/5 | 5/5 |
| HSQ-0211 | agent CLI discovery process | no_guard_confirmed | 5 | 1/5 | 2/5 | 4/5 |
| HSQ-0298 | external content file write | guarded | 5 | 1/5 | 2/5 | 5/5 |
| HSQ-0300 | external tarball extraction | guarded | 5 | 1/5 | 2/5 | 5/5 |
| HSQ-0302 | validated skill file write | guarded | 5 | 1/5 | 2/5 | 5/5 |

## Paper claim boundary

- This ablation supports the RQ4 claim that Security-ADG preserves security context omitted by sink-only and simplified ADG views.
- It should not be reported as method accuracy. Accuracy requires the independent held-out gold set and adjudication.
- The guard coverage denominator here is the set of held-out cases whose frozen evidence explicitly records positive guard context.
