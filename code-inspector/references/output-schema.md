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
      "issues": [
        {
          "severity": "critical|high|medium|low",
          "category": "naming|structure|complexity|readability",
          "file": "",
          "line": 0,
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
        "coverage_percentage": 0,
        "missing_cases": [],
        "quality_issues": []
      },
      "api_test": {
        "endpoints_tested": 0,
        "total_endpoints": 0,
        "missing_scenarios": []
      },
      "e2e_test": {
        "critical_paths_covered": 0,
        "total_critical_paths": 0,
        "gaps": []
      }
    },
    "performance": {
      "score": 0,
      "anti_patterns": [
        {
          "type": "",
          "severity": "critical|high|medium",
          "location": "",
          "impact": "",
          "optimization": ""
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
      "issues": [
        {
          "severity": "critical|high|medium|low",
          "file": "",
          "line": 0,
          "type": "breaking_change|inconsistent_signature|missing_idempotency|poor_naming|bool_parameter_smell|too_many_params",
          "message": "",
          "suggestion": ""
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
      "vulnerabilities": [
        {
          "type": "",
          "severity": "critical|high|medium|low",
          "cwe_id": "",
          "location": "",
          "description": "",
          "remediation": ""
        }
      ],
      "dependency_issues": [],
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
- `score`: 0-100, weighted average of standards compliance and issue severity
- `issues[]`: List of code quality problems found
  - `severity`: How urgently this should be fixed
  - `category`: The dimension of quality affected
  - `file`/`line`: Where the issue is located
  - `message`: What's wrong
  - `suggestion`: How to fix it
- `standards_compliance`: Percentage scores (0-100) for each sub-dimension
  - `pep8_eslint_etc`: Compliance with the primary language style guide
  - `naming_conventions`: Whether names follow language conventions
  - `code_structure`: Whether code is well-organized

### test_coverage
- `score`: 0-100
- `unit_test`: Unit test analysis
  - `coverage_percentage`: Estimated or reported test coverage (0-100)
  - `missing_cases[]`: Strings describing untested scenarios
  - `quality_issues[]`: Strings describing test quality problems (weak assertions, over-mocking, etc.)
- `api_test`: API/integration test analysis (only if applicable)
  - `endpoints_tested`/`total_endpoints`: Coverage counts
  - `missing_scenarios[]`: Untested API scenarios
- `e2e_test`: End-to-end test analysis (only if applicable)
  - `critical_paths_covered`/`total_critical_paths`: Coverage counts
  - `gaps[]`: Descriptions of missing E2E coverage

### performance
- `score`: 0-100
- `anti_patterns[]`: Performance issues found
  - `type`: Category (e.g., "N+1 query", "memory leak", "blocking I/O")
  - `severity`: impact severity
  - `location`: File/function reference
  - `impact`: What the performance consequence is
  - `optimization`: How to fix it
- `complexity_analysis`: Algorithm analysis
  - `time_complexity`: Big-O notation for the primary algorithm
  - `space_complexity`: Big-O notation for space usage
  - `bottlenecks[]`: Specific bottleneck locations

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
- `applicable`: true if public function signatures, HTTP endpoints, or library interfaces were added/modified, false if purely internal
- `score`: 0-100 (set to 100 if `applicable: false`)
- `issues[]`: API design problems found
  - `type`: `breaking_change`, `inconsistent_signature`, `missing_idempotency`, `poor_naming`, `bool_parameter_smell`, `too_many_params`
  - `file`/`line`: Where the issue is located
  - `message`/`suggestion`: What's wrong and how to fix it

### logging
- `score`: 0-100
- `issues[]`: Observability problems found
  - `type`: `wrong_level` (ERROR for info, DEBUG for critical), `string_interpolation` (not using structured key-value pairs), `pii_leak` (personal data in logs), `missing_trace_id` (no request correlation ID), `console_log` (print/console.log instead of proper logger), `missing_metric` (key operational counter not implemented)
  - `file`/`line`: Where the issue is located
  - `message`/`suggestion`: What's wrong and how to fix it

### security
- `score`: 0-100
- `vulnerabilities[]`: Security issues found
  - `type`: Vulnerability category (e.g., "SQL Injection", "XSS", "Sensitive Data Exposure")
  - `severity`: Risk level
  - `cwe_id`: Common Weakness Enumeration ID (e.g., "CWE-89" for SQL injection)
  - `location`: Where the vulnerability exists
  - `description`: What the vulnerability is and why it's dangerous
  - `remediation`: Concrete steps to fix it
- `dependency_issues[]`: Known-vulnerable or deprecated dependencies
- `compliance`: Boolean flags for major compliance categories
  - `owasp_top10`: true if no OWASP Top 10 issues found
  - `data_privacy`: true if no data privacy concerns found

### overall_score
0-100, weighted average of all applicable category scores (code_quality, test_coverage, performance, database, error_handling, concurrency_safety, api_design, logging, security).

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
