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
0-100, weighted average of the four category scores.

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
