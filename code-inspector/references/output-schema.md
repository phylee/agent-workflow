# Output Schema

The code review output MUST use this exact JSON structure. All fields are required unless marked optional.

```json
{
  "code_review_result": {
    "summary": {
      "total_files": 0,
      "total_lines": 0,
      "language": "",
      "review_timestamp": ""
    },
    "code_quality": {
      "score": 0,
      "tool_used": "",
      "tool_findings_count": 0,
      "issues": [
        {
          "severity": "critical|high|medium|low",
          "category": "bug-risk|style|complexity|anti-pattern|dead-code",
          "file": "",
          "line": 0,
          "rule_id": "",
          "message": "",
          "suggestion": ""
        }
      ],
      "standards_compliance": {
        "pep8_eslint_etc": 0,
        "naming_conventions": 0,
        "code_structure": 0
      }
    },
    "test_coverage": {
      "score": 0,
      "unit_test": {
        "test_files_found": 0,
        "total_tests": 0,
        "total_assertions": 0,
        "assertions_per_test": 0,
        "coverage_percentage": 0,
        "missing_cases": [],
        "quality_issues": [],
        "mutation_testing": {
          "tool_used": "",
          "mutants_total": 0,
          "mutants_killed": 0,
          "mutants_survived": 0,
          "mutation_score": 0,
          "surviving_mutations": [
            {
              "location": "",
              "mutation": "",
              "why_survived": "",
              "test_to_add": ""
            }
          ]
        }
      },
      "api_test": {
        "endpoints_tested": 0,
        "total_endpoints": 0,
        "missing_scenarios": []
      },
      "e2e_test": {
        "critical_journeys": [
          {
            "journey": "",
            "covered": false,
            "happy_path": false,
            "error_path": false,
            "pseudo_e2e_risk": true,
            "gap_description": ""
          }
        ],
        "score": 0,
        "gaps": []
      }
    },
    "performance": {
      "score": 0,
      "anti_patterns": [
        {
          "type": "",
          "severity": "critical|high|medium",
          "evidence": "",
          "mechanism": "",
          "fix": "",
          "location": ""
        }
      ],
      "complexity_analysis": {
        "time_complexity": "",
        "space_complexity": "",
        "bottlenecks": []
      }
    },
    "database": {
      "applicable": true,
      "score": 0,
      "migration_issues": [
        {
          "severity": "critical|high|medium|low",
          "file": "",
          "line": 0,
          "type": "locking|rollback|backfill|type_change|constraint_change",
          "message": "",
          "suggestion": ""
        }
      ],
      "schema_issues": [
        {
          "severity": "critical|high|medium|low",
          "table": "",
          "column": "",
          "type": "missing_constraint|wrong_type|missing_default|cascade_risk|normalization",
          "message": "",
          "suggestion": ""
        }
      ],
      "index_analysis": {
        "missing_indexes": [],
        "redundant_indexes": [],
        "recommendations": []
      },
      "query_issues": [
        {
          "severity": "critical|high|medium|low",
          "file": "",
          "line": 0,
          "type": "n_plus_1|select_star|missing_limit|cartesian_join|correlated_subquery|missing_transaction",
          "message": "",
          "suggestion": ""
        }
      ]
    },
    "error_handling": {
      "score": 0,
      "issues": [
        {
          "severity": "critical|high|medium|low",
          "file": "",
          "line": 0,
          "type": "swallowed_error|missing_context|bare_except|missing_retry|resource_leak|no_fallback",
          "message": "",
          "suggestion": ""
        }
      ]
    },
    "concurrency_safety": {
      "applicable": true,
      "score": 0,
      "issues": [
        {
          "severity": "critical|high|medium|low",
          "file": "",
          "line": 0,
          "type": "race_condition|deadlock_risk|goroutine_leak|unsynchronized_access|loop_variable_capture|missing_done_channel",
          "message": "",
          "suggestion": ""
        }
      ]
    },
    "api_design": {
      "applicable": true,
      "score": 0,
      "contract_type": "openapi|graphql|protobuf|implicit",
      "contract_diff": {
        "tool_used": "",
        "breaking_changes": 0,
        "warnings": 0
      },
      "issues": [
        {
          "severity": "critical|high|medium|low",
          "file": "",
          "line": 0,
          "type": "breaking_change|inconsistent_signature|missing_idempotency|poor_naming|bool_parameter_smell|too_many_params|sensitive_field_leak|missing_validation|missing_pagination|missing_rate_limit",
          "message": "",
          "suggestion": "",
          "migration_path": ""
        }
      ]
    },
    "logging": {
      "score": 0,
      "issues": [
        {
          "severity": "critical|high|medium|low",
          "file": "",
          "line": 0,
          "type": "wrong_level|string_interpolation|pii_leak|missing_trace_id|console_log|missing_metric",
          "message": "",
          "suggestion": ""
        }
      ]
    },
    "security": {
      "score": 0,
      "sast_tools_used": [],
      "findings_raw": 0,
      "vulnerabilities": [
        {
          "type": "",
          "severity": "critical|high|medium|low",
          "category": "input|auth|data|storage|network|browser|dependency|infra",
          "cwe_id": "",
          "source_tool": "",
          "location": "",
          "description": "",
          "remediation": ""
        }
      ],
      "dependency_issues": [
        {
          "package": "",
          "current_version": "",
          "fixed_version": "",
          "cve_id": "",
          "severity": "",
          "reachable": true,
          "advisory": ""
        }
      ],
      "compliance": {
        "owasp_top10": true,
        "data_privacy": true
      }
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
- `total_files`: Number of source files reviewed
- `total_lines`: Total lines of code examined
- `language`: Detected or specified programming language
- `review_timestamp`: ISO 8601 timestamp of the review

### code_quality
- `score`: 0-100. 95+ if lint tool passes clean. Capped at 80 for prompt-based fallback.
- `tool_used`: Name and version of the static analysis tool (e.g., `"ruff 0.13.2"`) or `"none (prompt-based fallback)"`
- `tool_findings_count`: Raw lint findings count before merging/deduplication
- `issues[]`: LLM-interpreted findings (classified, merged, explained)
  - `severity`: Actual impact-based severity (may differ from tool's default level)
  - `category`: `bug-risk` (likely incorrect behavior), `style` (cosmetic), `complexity` (maintainability risk), `anti-pattern` (fragile but functional), `dead-code` (unused/unreachable)
  - `rule_id`: The lint tool's rule identifier (e.g., `B007`, `no-unused-vars`, `errcheck`)
  - `file`/`line`: Where the issue is located
  - `message`: Human-language explanation of the issue
  - `suggestion`: How to fix it
- `standards_compliance`: Percentage scores (0-100) for each sub-dimension, inferred from tool output

### test_coverage
- `score`: 0-100. Mutation score overrides coverage percentage. No tests = 0.
- `unit_test`: Unit test analysis
  - `test_files_found`: Number of test files that exist
  - `total_tests`/`total_assertions`/`assertions_per_test`: Assertion density metrics — <1 = decorative tests, <3 = minimal, >=5 = reasonable
  - `coverage_percentage`: Informational only — do not trust as quality signal
  - `mutation_testing`: Deterministic test quality via mutation injection
    - `tool_used`: e.g., `"stryker 8.2"`, `"mutmut 3.1"`, or `"none (not available)"`
    - `mutants_total`/`mutants_killed`/`mutants_survived`: Mutation counts
    - `mutation_score`: `killed / total * 100` — the actual test effectiveness percentage
    - `surviving_mutations[]`: Each surviving mutation with explanation and remediation
- `api_test`: API/integration test analysis (only if applicable)
- `e2e_test`: User journey coverage — `critical_journeys[]` with `journey`, `covered`, `happy_path`, `error_path`, `pseudo_e2e_risk` (detects page-visit-only or fully-mocked E2E), `gap_description`

### performance
- `score`: 0-100
- `anti_patterns[]`: Performance issues with mandatory evidence
  - `type`: Category (e.g., "N+1 query", "nested loop O(n²)", "sync IO in async context")
  - `severity`: Impact severity — critical (will cause outage under load), high (significant degradation), medium (noticeable in production), low (minor)
  - `evidence`: Exact code location proving the pattern exists
  - `mechanism`: Why this causes performance degradation (e.g., "for 1000 users, executes 1,000,000 queries")
  - `fix`: Concrete optimization with code example
- `complexity_analysis`: Big-O estimates, bottlenecks ranked by impact

### database
- `applicable`: true if database-related code was detected (SQL files, migrations, ORM models, query builders), false if no DB code present
- `score`: 0-100 (set to 100 if `applicable: false`)
- `migration_issues[]`: Problems with schema migration scripts
  - `type`: `locking` (dangerous lock), `rollback` (not reversible), `backfill` (unsafe data migration), `type_change` (lossy cast), `constraint_change` (adding constraints to large tables)
- `schema_issues[]`: Problems with table/column design
  - `table`/`column`: Affected database objects
  - `type`: `missing_constraint`, `wrong_type`, `missing_default`, `cascade_risk`, `normalization`
- `index_analysis`: Index review
  - `missing_indexes[]`: Columns that should be indexed
  - `redundant_indexes[]`: Indexes that duplicate or can be removed
  - `recommendations[]`: Strings with specific index suggestions
- `query_issues[]`: Problems in application-layer queries
  - `type`: `n_plus_1`, `select_star`, `missing_limit`, `cartesian_join`, `correlated_subquery`, `missing_transaction`
  - `file`/`line`: Where the query is located
  - `message`/`suggestion`: What's wrong and how to fix it

### error_handling
- `score`: 0-100
- `issues[]`: Error handling problems found
  - `type`: `swallowed_error` (error silently dropped), `missing_context` (no wrapping/wrapping without context), `bare_except` (overly broad catch), `missing_retry` (transient error not retried), `resource_leak` (cleanup skipped on error path), `no_fallback` (no graceful degradation when dependency fails)
  - `file`/`line`: Where the issue is located
  - `message`/`suggestion`: What's wrong and how to fix it

### concurrency_safety
- `applicable`: true if concurrent code detected (goroutines, threads, async, shared state), false otherwise
- `score`: 0-100 (set to 100 if `applicable: false`)
- `issues[]`: Concurrency problems found
  - `type`: `race_condition`, `deadlock_risk`, `goroutine_leak`, `unsynchronized_access`, `loop_variable_capture`, `missing_done_channel`
  - `file`/`line`: Where the issue is located
  - `message`/`suggestion`: What's wrong and how to fix it

### api_design
- `applicable`: true if public function signatures, HTTP endpoints, RPC, or library interfaces were added/modified
- `score`: 0-100 (set to 100 if `applicable: false`)
- `contract_type`: `openapi`, `graphql`, `protobuf`, or `implicit` (inferred from code)
- `contract_diff`: Results from schema diff tool — `tool_used`, `breaking_changes` count, `warnings` count
- `issues[]`: API design problems found
  - `type`: `breaking_change`, `sensitive_field_leak`, `missing_validation`, `missing_pagination`, `missing_rate_limit`, plus previous types
  - `migration_path`: If breaking, a concrete deprecation/migration strategy

### logging
- `score`: 0-100
- `issues[]`: Observability problems found
  - `type`: `wrong_level` (ERROR for info, DEBUG for critical), `string_interpolation` (not using structured key-value pairs), `pii_leak` (personal data in logs), `missing_trace_id` (no request correlation ID), `console_log` (print/console.log instead of proper logger), `missing_metric` (key operational counter not implemented)
  - `file`/`line`: Where the issue is located
  - `message`/`suggestion`: What's wrong and how to fix it

### security
- `score`: 0-100. Capped at 70 if no SAST tools were run (AI-only assessment).
- `sast_tools_used[]`: Tools run (e.g., `["semgrep 1.x", "trivy 0.x"]`). Empty = AI-only.
- `findings_raw`: Count before triage/deduplication.
- `vulnerabilities[]`: Triaged findings
  - `category`: Security surface classification — `input`, `auth`, `data`, `storage`, `network`, `browser`, `dependency`, `infra`
  - `source_tool`: Which tool found it (for auditability)
- `dependency_issues[]`: Each with `reachable` flag — is the vulnerable code actually exercised?
- `compliance`: `owasp_top10` false if any OWASP category violated; `data_privacy` false if PII handling issues found

### overall_score
0-100, weighted average of all applicable category scores using these default weights:

| Dimension | Weight | Conditional? |
|-----------|--------|-------------|
| code_quality | 15% | always active |
| test_coverage | 15% | always active |
| performance | 10% | always active |
| database | 10% | yes — 0% if no DB changes |
| error_handling | 15% | always active |
| concurrency_safety | 10% | yes — 0% if no concurrent code |
| api_design | 4% | yes — 0% if no API surface changes |
| logging | 5% | always active |
| security | 16% | always active |

When a conditional dimension is skipped, its weight is redistributed proportionally among the remaining active dimensions.

### recommendations
Actionable next steps sorted by priority:
- `priority`: `immediate` (blocking), `short-term` (this sprint), `long-term` (future improvement)
- `category`: Which dimension this addresses
- `action`: What to do
- `effort_estimate`: Rough time estimate (e.g., "30m", "2h", "1d", "1w")

## Scoring Guidelines

| Range | Meaning |
|-------|---------|
| 90-100 | Excellent, few or no issues |
| 75-89 | Good, minor improvements possible |
| 60-74 | Acceptable, some issues to address |
| 40-59 | Needs improvement, multiple significant issues |
| 20-39 | Poor, major problems present |
| 0-19 | Critical, serious issues must be resolved |
