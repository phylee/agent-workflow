# Output Schema

The review output is a strongly-structured inspection report. Every finding must include a confidence score and a deterministic flag so consumers know which findings are tool-verified vs. LLM-inferred.

```json
{
  "code_inspector_result": {
    "summary": {
      "total_files": 0,
      "total_lines": 0,
      "language": "",
      "review_timestamp": "",
      "risk_score": 0,
      "quality_score": 0,
      "security_score": 0,
      "test_score": 0,
      "performance_score": 0,
      "human_summary": ""
    },
    "tool_runs": [
      {
        "tool": "",
        "status": "success|failed|unavailable|skipped",
        "deterministic": true,
        "summary": ""
      }
    ],
    "limitations": [],
    "review_delta": {
      "mode": "initial|re-review",
      "resolved_since_last": [],
      "new_since_last": [],
      "unchanged_since_last": []
    },
    "inspections": [
      {
        "id": "",
        "category": "security|code_quality|performance|database|error_handling|concurrency|api_design|logging|test_coverage",
        "type": "",
        "severity": "critical|high|medium|low",
        "confidence": 0.0,
        "deterministic": true,
        "source": "",
        "file": "",
        "line": 0,
        "location": {
          "file": "",
          "start_line": 0,
          "end_line": 0
        },
        "diff_hunk": "",
        "evidence_chain": [],
        "impact": "",
        "recommendation": "",
        "metadata": {
          "auto_fixable": false,
          "fix_command": "",
          "suggested_patch": ""
        }
      }
    ],
    "coverage": {
      "test_existence": {
        "source_files_changed": 0,
        "source_files_with_nearby_tests": 0,
        "required_test_layers": ["unit", "api", "e2e", "performance"],
        "missing_test_layers": []
      },
      "test_quality": {
        "assertion_density": 0.0,
        "mutation_score": 0,
        "behavior_assertions_found": 0,
        "mock_only_tests_detected": false
      },
      "unit_test": {
        "test_files_found": 0,
        "changed_lines_covered_pct": 0,
        "assertion_density": 0.0,
        "mutation_score": 0
      },
      "api_test": {
        "endpoints_tested": 0,
        "total_endpoints": 0,
        "contract_tests_found": 0,
        "negative_cases_covered": 0,
        "auth_cases_covered": 0,
        "idempotency_cases_covered": 0
      },
      "e2e": {
        "critical_journeys_covered": 0,
        "total_critical_journeys": 0,
        "pseudo_e2e_detected": false
      },
      "performance_test": {
        "benchmarks_found": 0,
        "load_tests_found": 0,
        "regression_thresholds_defined": false,
        "hot_paths_covered": 0,
        "total_hot_paths": 0
      }
    },
    "gates": {
      "merge_blocked": true,
      "verdict": "",
      "reasons": [],
      "warnings": []
    },
    "top_findings": [
      {
        "id": "",
        "title": "",
        "severity": "critical|high|medium|low",
        "category": "",
        "file": "",
        "line": 0
      }
    ],
    "overall_score": 0,
    "recommendations": [
      {
        "priority": "immediate|short-term|long-term",
        "category": "",
        "action": "",
        "effort_estimate": ""
      }
    ]
  }
}
```

## Field Descriptions

### summary
- `total_files`: Files reviewed
- `total_lines`: Lines of code examined
- `language`: Detected or specified language
- `review_timestamp`: ISO 8601 timestamp
- `risk_score`: 0-100 overall risk (higher = riskier)
- `quality_score`: 0-100 code quality
- `security_score`: 0-100 security posture
- `test_score`: 0-100 test quality
- `performance_score`: 0-100 performance health
- `human_summary`: 2-3 sentence structured summary for human readers. Keep it inside JSON.

### tool_runs
- `tool`: Tool command or name attempted (e.g., `ruff check`, `semgrep`, `npm audit`)
- `status`: `success`, `failed`, `unavailable`, or `skipped`
- `deterministic`: `true` if the result came from actual tool output
- `summary`: concise outcome, including failure reason when relevant

### limitations
List missing context, unavailable tools, skipped network-dependent checks, or any reason the report may be incomplete.

### review_delta
Used when the input has `reviewer_context: "re-review"` and previous review data is available.
- `mode`: `initial` for first review or `re-review` for follow-up reviews
- `resolved_since_last`: previous finding IDs or stable finding fingerprints that no longer reproduce
- `new_since_last`: current inspection IDs that were not present in the previous review
- `unchanged_since_last`: finding IDs or fingerprints still present from the previous review

When previous review data is unavailable, set `mode` from input, leave the arrays empty, and add a `limitations[]` entry.

### inspections (the core)

A flat list of all findings across all dimensions. Every inspection must include:

- `id`: unique identifier for this finding (e.g., `SEC-001`, `PERF-003`)
- `category`: which dimension — `security`, `code_quality`, `performance`, `database`, `error_handling`, `concurrency`, `api_design`, `logging`, `test_coverage`
- `type`: specific issue type within the category (e.g., `sql_injection`, `n_plus_1_query`, `breaking_change`)
- `severity`: `critical` (blocks merge, causes crash/data loss), `high` (likely bug, should fix before deploy), `medium` (should fix in this sprint), `low` (cosmetic, nice to fix)
- `confidence`: **0.0 to 1.0**. How certain is this finding?
  - Use the canonical bands in the Confidence Guidelines section below.
- `deterministic`: **true** if from a tool (Semgrep, ESLint, AST, compiler, mutation testing), **false** if LLM inference or pattern matching
- `source`: which tool or method produced this finding (e.g., `semgrep`, `eslint`, `golangci-lint`, `mutmut`, `llm-inference`)
- `location`: canonical structured location for CI annotations and PR comment bots. Use `start_line` and `end_line` from the new file when the finding maps to a diff; otherwise use the best source location.
- `file` / `line`: backward-compatible shorthand only. These fields must always equal `location.file` and `location.start_line`. New consumers should read `location`.
- `diff_hunk`: the smallest relevant original diff hunk when available. Keep this short enough for machine consumers; do not include unrelated hunks.
- `evidence_chain`: **ordered list of observations** tracing from input to impact:
  - `["user input from query param 'search'", "passed to fmt.Sprintf without sanitization", "executed as raw SQL via db.Query()", "allows attacker to read/modify/delete all user data"]`
  - Each step links to the next, forming a traceable path from root cause to consequence
  - This is what makes a finding auditable — a reviewer can validate each link in the chain independently
- `impact`: what happens if this is not fixed
- `recommendation`: concrete fix with code example where possible
- `metadata`: category-specific machine-readable details such as `cwe_id`, `cve_id`, `contract_type`, `mutation`, `table`, `column`, `migration_path`, or `tool_rule_url`
  - `auto_fixable`: optional boolean. True when the issue can be fixed mechanically by a known tool or safe patch.
  - `fix_command`: optional command string for deterministic auto-fix tools, such as `ruff check --fix <file>` or `npx eslint --fix <file>`.
  - `suggested_patch`: optional unified diff for a concrete fix. Only include when the patch is small, local, and directly supported by the evidence chain.

### coverage
- `test_existence`: whether expected test layers exist for changed source files. This is about presence, not quality.
- `test_quality`: whether tests verify behavior. Prefer mutation score when available; otherwise use assertion density, behavior assertions, and mock-only detection.
- `unit_test`: test quality metrics
  - `changed_lines_covered_pct`: % of changed lines exercised by tests (informational only — do not trust)
  - `assertion_density`: assertions per test
  - `mutation_score`: % of injected mutations killed by tests (the actual quality signal)
- `api_test`: interface and contract test metrics
  - `endpoints_tested` / `total_endpoints`: changed or affected API endpoints with tests
  - `contract_tests_found`: OpenAPI/GraphQL/protobuf/schema contract tests found
  - `negative_cases_covered`: validation, malformed input, authorization failure, and error response tests
  - `auth_cases_covered`: anonymous, authenticated, and role-specific access tests
  - `idempotency_cases_covered`: retry or duplicate request tests for unsafe writes
- `e2e`: journey coverage
  - `critical_journeys_covered` / `total_critical_journeys`
  - `pseudo_e2e_detected`: true if existing E2E tests are page-visit-only or fully mocked
- `performance_test`: benchmark/load/regression-test coverage for changed hot paths
  - `benchmarks_found`: micro or component benchmarks, such as Go benchmarks, pytest-benchmark, JMH, BenchmarkDotNet
  - `load_tests_found`: scenario/load tests, such as k6, Locust, Gatling, Artillery, JMeter
  - `regression_thresholds_defined`: true only when the test has an explicit pass/fail budget
  - `hot_paths_covered` / `total_hot_paths`: changed performance-sensitive paths with test coverage

### gates
- `merge_blocked`: **true** if any critical-severity finding OR if `reasons` contains blocking conditions
- `verdict`: one-line verdict, e.g. `Merge blocked: critical_security_issue` or `Merge allowed with 3 warnings`
- `reasons[]`: list of blocking reasons (e.g., `critical_security_issue`, `missing_test`, `breaking_api_change`, `migration_without_rollback`)
- `warnings[]`: non-blocking concerns that should be addressed (e.g., `low_assertion_density`, `console_log_in_production`)

### top_findings
List the 1-5 most important findings as inline summary objects, ordered by merge risk and impact. `id` must reference an `inspections[].id`, but consumers should be able to render this section without joining back to `inspections[]`.

### overall_score
0-100. Weighted across dimensions (see weight table below). Gate-blocked reviews cap at 40.

### recommendations
Prioritized action items: `immediate` (blocks merge), `short-term` (this sprint), `long-term` (future).

## Weight Table

| Dimension | Weight | Conditional? |
|-----------|--------|-------------|
| code_quality | 15% | always active |
| test_coverage | 15% | always active |
| performance | 10% | always active |
| database | 10% | 0% if no DB changes |
| error_handling | 15% | always active |
| concurrency | 10% | 0% if no concurrent code |
| api_design | 4% | 0% if no API surface changes |
| logging | 5% | always active |
| security | 16% | always active |

## Score Calculation

Canonical scores are calculated from `inspections[]`. Reviewer-local `score` fields are diagnostic inputs only; use them as hints when a reviewer produced no machine-readable inspections, but do not let them override inspection-based scoring.

1. Start each active dimension at 100.
2. For every inspection, subtract `severity_weight * confidence_multiplier` from its dimension:
   - `critical`: 45
   - `high`: 25
   - `medium`: 12
   - `low`: 4
   - `confidence_multiplier`: `confidence`; add `+0.10` capped at `1.0` when `deterministic: true`
3. Clamp each dimension score to 0-100.
4. Inactive conditional dimensions (`database`, `concurrency`, `api_design`) receive no score and their weight is redistributed proportionally across active dimensions.
5. `test_score` combines test existence and test quality. Suggested split: 25% existence, 35% unit quality, 20% API test coverage, 15% E2E journey quality, 5% performance-test coverage. For performance-critical changes, raise performance-test coverage to 15% and reduce existence/unit weights proportionally.
6. `risk_score = 100 - overall_score`, then increase by up to 20 points for critical/high findings that affect externally reachable paths.
7. If `gates.merge_blocked` is true, cap `overall_score` at 40.

### Weight Normalization Example

For an API PR that also activates `database` and `concurrency`, start with active base weights:

`code_quality 15 + test_coverage 15 + performance 10 + database 10 + error_handling 15 + concurrency 10 + api_design 4 + logging 5 + security 16 = 100`

Apply API adjustments: `security +5`, `api_design +5`, `code_quality -5`, `performance -5`.

Adjusted weights become:

`code_quality 10, test_coverage 15, performance 5, database 10, error_handling 15, concurrency 10, api_design 9, logging 5, security 21 = 100`

If an adjustment references an inactive dimension, ignore that adjustment first, then normalize all active weights so the final total is exactly 100. For example, if `concurrency` is inactive, remove its 10 weight and scale the remaining adjusted active weights by `100 / active_weight_sum`.

## Confidence Guidelines

| Confidence | When to Use |
|---|---|
| 0.95+ | Tool exact match (Semgrep rule fired, ESLint error, mutation killed=1, compiler error) |
| 0.85-0.95 | Tool match with simple LLM interpretation (explaining what the rule means in context) |
| 0.70-0.85 | Strong heuristic with clear evidence chain (N+1 query detected by identifying loop + DB call) |
| 0.50-0.70 | Plausible finding with some evidence but requires human judgment (API design inconsistency) |
| 0.30-0.50 | Speculative — pattern suggests issue but could be intentional (performance concern without load data) |
| <0.30 | Gut feel — flag for human reviewer, always `deterministic: false` |

## Deterministic vs Heuristic

| Deterministic (`true`) | Heuristic (`false`) |
|---|---|
| Semgrep / CodeQL rule match | LLM pattern recognition |
| ESLint / Ruff / golangci-lint output | "this looks like an anti-pattern" |
| Compiler warning/error | "this function might be too long" |
| Mutation testing: killed/survived | "these tests might be insufficient" |
| `npm audit` / `go vulncheck` CVE | "this dependency might be risky" |
| Breaking change detected by OpenAPI diff | "this change might break callers" |
| Assertion density < 1 (counted) | "these assertions might be weak" |

Deterministic findings can be acted on immediately. Heuristic findings should be reviewed by a human before blocking merge — unless confidence is >= 0.8.

## Gate Rules

Block merge (`merge_blocked: true`) when:
- Any finding with `severity: critical` AND `confidence >= 0.7`
- Any finding with `severity: critical` AND `deterministic: true` (regardless of confidence)
- `test_score < 10` (effectively no tests)
- `security_score < 30` (critical security issues)
- Breaking API change without deprecation path
- Database migration without rollback
