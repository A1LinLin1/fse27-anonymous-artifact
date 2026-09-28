# Corpus-wide Security-ADG characterization

> Candidate/evidence counts only; these values are not vulnerability counts and do not estimate corpus-wide recall.

## Population

| Measure | Count | Rate |
|---|---:|---:|
| Static candidates | 23866 | 100.00% |
| Framework evidence | 749 | 3.14% |
| Source provenance | 9821 | 41.15% |
| Dependency path | 9821 | 41.15% |
| Trust-crossing candidate | 9821 | 41.15% |
| Privilege context | 0 | 0.00% |
| Guard candidate | 3075 | 12.88% |
| External-effect model node | 23866 | 100.00% |
| Confirmed external effect | 0 | 0.00% |

## By behavior category

| Category | Candidates | Dependency | Guard | Trust-crossing |
|---|---:|---:|---:|---:|
| browser_control | 588 | 11 (1.87%) | 13 (2.21%) | 11 (1.87%) |
| command_execution | 2722 | 933 (34.28%) | 315 (11.57%) | 933 (34.28%) |
| credential_access | 2548 | 251 (9.85%) | 454 (17.82%) | 251 (9.85%) |
| database_access | 1304 | 106 (8.13%) | 36 (2.76%) | 106 (8.13%) |
| dynamic_code_execution | 55 | 24 (43.64%) | 23 (41.82%) | 24 (43.64%) |
| external_tool_invocation | 5344 | 603 (11.28%) | 73 (1.37%) | 603 (11.28%) |
| filesystem_delete | 583 | 235 (40.31%) | 299 (51.29%) | 235 (40.31%) |
| filesystem_read | 4182 | 2730 (65.28%) | 1062 (25.39%) | 2730 (65.28%) |
| filesystem_write | 5013 | 4218 (84.14%) | 632 (12.61%) | 4218 (84.14%) |
| message_or_email_send | 164 | 70 (42.68%) | 32 (19.51%) | 70 (42.68%) |
| network_access | 1157 | 553 (47.80%) | 121 (10.46%) | 553 (47.80%) |
| permission_or_auth_change | 206 | 87 (42.23%) | 15 (7.28%) | 87 (42.23%) |

## Scalability

Population consistency: **True**.
End-to-end comparable: **True**.

| Stage | Population | Wall time (s) | Candidates/s | Peak RSS (MB) | Python peak allocation (MB) |
|---|---:|---:|---:|---:|---:|
| candidate_extraction | 23866 | 1508.456 | 15.821 | n/a | n/a |
| graph_construction | 23866 | 1538.164 | 15.516 | n/a | n/a |

End-to-end wall time: **3046.620 s**; throughput: **7.834 candidates/s**.
Per-repository median/P90/P95: **9.562 / 203.008 / 236.191 s**.

Memory profiling was disabled for this timing run, so wall time excludes `tracemalloc` overhead.

Graph input SHA-256: `7c73795e4cd7fa59d7fe3df01f2cb7e38c6f5a30481719586b26b0d84d015fd7`
