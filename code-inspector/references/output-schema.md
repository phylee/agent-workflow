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
      "performance_score": 0
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
        "evidence_chain": [],
        "impact": "",
        "recommendation": ""
      }
    ],
    "coverage": {
      "unit_test": {
        "test_files_found": 0,
        "changed_lines_covered_pct": 0,
        "assertion_density": 0.0,
        "mutation_score": 0
      },
      "e2e": {
        "critical_journeys_covered": 0,
        "total_critical_journeys": 0,
        "pseudo_e2e_detected": false
      }
    },
    "gates": {
      "merge_blocked": true,
      "reasons": [],
      "warnings": []
    },
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

### inspections (the core)

A flat list of all findings across all dimensions. Every inspection must include:

- `id`: unique identifier for this finding (e.g., `SEC-001`, `PERF-003`)
- `category`: which dimension — `security`, `code_quality`, `performance`, `database`, `error_handling`, `concurrency`, `api_design`, `logging`, `test_coverage`
- `type`: specific issue type within the category (e.g., `sql_injection`, `n_plus_1_query`, `breaking_change`)
- `severity`: `critical` (blocks merge, causes crash/data loss), `high` (likely bug, should fix before deploy), `medium` (should fix in this sprint), `low` (cosmetic, nice to fix)
- `confidence`: **0.0 to 1.0**. How certain is this finding?
  - 0.9+: tool-verified, deterministic match
  - 0.7-0.9: strong pattern match with some LLM interpretation
  - 0.5-0.7: moderate confidence, likely correct but could be false positive
  - <0.5: speculative — consumer should verify before acting
- `deterministic`: **true** if from a tool (Semgrep, ESLint, AST, compiler, mutation testing), **false** if LLM inference or pattern matching
- `source`: which tool or method produced this finding (e.g., `semgrep`, `eslint`, `golangci-lint`, `mutmut`, `llm-inference`)
- `file` / `line`: exact location
- `evidence_chain`: **ordered list of observations** tracing from input to impact:
  - `["user input from query param 'search'", "passed to fmt.Sprintf without sanitization", "executed as raw SQL via db.Query()", "allows attacker to read/modify/delete all user data"]`
  - Each step links to the next, forming a traceable path from root cause to consequence
  - This is what makes a finding auditable — a reviewer can validate each link in the chain independently
- `impact`: what happens if this is not fixed
- `recommendation`: concrete fix with code example where possible

### coverage
- `unit_test`: test quality metrics
  - `changed_lines_covered_pct`: % of changed lines exercised by tests (informational only — do not trust)
  - `assertion_density`: assertions per test
  - `mutation_score`: % of injected mutations killed by tests (the actual quality signal)
- `e2e`: journey coverage
  - `critical_journeys_covered` / `total_critical_journeys`
  - `pseudo_e2e_detected`: true if existing E2E tests are page-visit-only or fully mocked

### gates
- `merge_blocked`: **true** if any critical-severity finding OR if `reasons` contains blocking conditions
- `reasons[]`: list of blocking reasons (e.g., `critical_security_issue`, `missing_test`, `breaking_api_change`, `migration_without_rollback`)
- `warnings[]`: non-blocking concerns that should be addressed (e.g., `low_assertion_density`, `console_log_in_production`)

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
