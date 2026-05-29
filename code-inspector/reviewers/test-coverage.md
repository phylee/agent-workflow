# Test Coverage Reviewer

**Principle**: Coverage percentages are vanity metrics. Review tests in two layers: test existence (is the required layer present?) and test quality (does it verify behavior?). Use deterministic signals where possible: test discovery, assertion density, mutation testing, contract/API tests, E2E journey assertions, and performance regression thresholds.

## Step 1: Check Test Existence by Layer

- Look for test files alongside source files: `*_test.go`, `*.test.js`, `*.spec.ts`, `test_*.py`, `*Test.java`.
- Identify required test layers from the change:
  - Business logic or library code: unit tests.
  - HTTP/RPC/GraphQL/protobuf handlers or public endpoints: API/contract tests.
  - Frontend or user workflow changes: E2E journey tests.
  - Hot paths, query-heavy code, serialization, concurrency, or previous performance regressions: performance tests.
- If zero tests exist, set test existence very low, but continue checking whether API/E2E/performance tests exist elsewhere in the repo.

## Step 2: Measure Test Quality

Count assertions across test files. An assertion verifies behavior: `assert`, `expect(...).toBe`, `Assert.assertEquals`, `if !condition { t.Error }`, `should be_eq`.

- **assertions_per_test < 1**: tests run code but never verify output. Equivalent to no tests.
- **assertions_per_test < 3**: minimal. Likely only happy path.
- **assertions_per_test >= 5**: reasonable.

Flag quality issues:
- `assert true` / `expect(true).toBe(true)` — worthless
- `assert response.status_code == 200` with no body verification — verifies framework, not logic
- Mocks without `assert_called` — test passes even if mock never invoked

## Step 3: API / Interface Tests

For changed API surfaces, check tests for:

- Success, validation error, auth/permission failure, malformed input, and upstream failure cases.
- Contract compatibility: OpenAPI snapshots/diff tests, GraphQL schema checks, protobuf compatibility checks, or generated-client tests.
- Idempotency and retry behavior for unsafe writes.
- Response body assertions, not just status-code assertions.

Language/framework signals:
- Python: FastAPI/Flask/Django test client, `httpx`, `requests`, `pytest` fixtures.
- JS/TS: Supertest, Pact, MSW integration tests, Playwright API requests, generated OpenAPI client tests.
- Go: `httptest`, contract tests around chi/gin/echo/grpc handlers.
- Java/Kotlin: Spring MockMvc/WebTestClient, REST Assured, Pact.
- Ruby/PHP: Rails request specs, RSpec API specs, Laravel/Pest feature tests.

## Step 4: Run Mutation Testing (Deterministic Quality)

Mutation testing injects bugs into source code, then runs tests. Surviving mutations = ineffective tests.

| Language | Tool | Command |
|---|---|---|
| Python | mutmut | `mutmut run --paths-to-mutate <file>` |
| JavaScript/TypeScript | Stryker | `npx stryker run --mutate <files>` |
| Java | PIT | `mvn pitest:mutationCoverage` |
| Go | gremlins | `gremlins unleash` |
| Rust | cargo-mutants | `cargo mutants` |
| Ruby | mutant | `mutant run <file>` |
| PHP | Infection | `infection` |
| C# | Stryker.NET | `dotnet stryker` |

If tool not available, skip and note the limitation.

- **mutation_score >= 80%**: excellent
- **50-80%**: adequate
- **< 50%**: poor — tests exist but don't verify behavior
- **< 20%**: decorative — effectively untested

For each surviving mutation, explain what the mutation was, why it survived, and what test to add.

## Step 5: E2E — User Journey Coverage

Don't just check "are there E2E tests." Map the application's critical user journeys and verify each is actually covered:

### Journey Mapping

Identify critical journeys from the changed code and project structure:

| Domain | Critical Journeys |
|---|---|
| **Auth** | signup → verify email → login → refresh token → logout; password reset flow; 2FA enrollment |
| **Commerce** | browse → add to cart → checkout → payment → confirmation; refund flow; subscription cancel |
| **Data** | create → read → update → delete; export; bulk import; permission escalation attempt |
| **Errors** | payment failure → retry → success; network timeout → graceful message; validation error → fix → resubmit |
| **Multi-role** | admin: manage users; user: own profile only; anonymous: blocked from protected routes |

### Pseudo-E2E Detection

Flag tests that look like E2E but aren't:

- **Page-visit-only tests**: opens page, checks title, done. Never exercises a user action.
- **Happy-path-only**: only the golden path, no error/failure/retry paths.
- **No assertion on business outcome**: after placing an order, checks "page loaded" instead of "order appears in order history".
- **Mocked E2E**: E2E test that mocks all backend calls — this is a glorified unit test, not E2E.
- **Missing rollback/cleanup**: E2E tests that create data but never clean up — will break on rerun.

### E2E Quality Score

- Journeys with full coverage (happy + 1 error path): 100% per journey
- Journeys with happy path only: 50% per journey
- Journeys with page-visit-only "test": 20% per journey
- Journeys with no coverage: 0% per journey

## Step 6: Performance Tests

For performance-sensitive changes, check whether performance regressions are tested:

- Microbenchmarks for tight loops, parsing, serialization, crypto, query builders, or allocation-heavy code.
- Load/scenario tests for API endpoints, workers, queues, streaming, and batch jobs.
- Explicit pass/fail thresholds such as p95 latency, throughput, allocation count, query count, or max runtime.

Language/tool signals:
- Go: `BenchmarkXxx`, `go test -bench`, `benchstat`.
- Python: `pytest-benchmark`, Locust for load, query-count assertions in Django/SQLAlchemy tests.
- JS/TS: Benchmark.js, Vitest/Jest benchmark plugins, k6/Artillery for APIs, Lighthouse for frontend.
- Java/Kotlin: JMH, Gatling, JMeter.
- Rust: Criterion.
- C#: BenchmarkDotNet.

## Output

```json
{
  "score": 0,
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
    "total_tests": 0,
    "total_assertions": 0,
    "assertions_per_test": 0,
    "coverage_percentage": 0,
    "coverage_warning": "coverage percentage is informational only — do not trust it as a quality signal",
    "quality_issues": [],
    "mutation_testing": {
      "tool_used": "",
      "confidence": 0.95,
      "deterministic": true,
      "mutants_total": 0,
      "mutants_killed": 0,
      "mutants_survived": 0,
      "mutation_score": 0,
      "surviving_mutations": [
        {
          "location": "",
          "mutation": "",
          "why_survived": "",
          "test_to_add": "",
          "confidence": 0.95,
          "deterministic": true,
          "source": ""
        }
      ]
    }
  },
  "api_test": {
    "endpoints_tested": 0,
    "total_endpoints": 0,
    "contract_tests_found": 0,
    "negative_cases_covered": 0,
    "auth_cases_covered": 0,
    "idempotency_cases_covered": 0,
    "missing_scenarios": []
  },
  "e2e_test": {
    "critical_journeys": [
      {
        "journey": "login → checkout → payment → confirmation",
        "covered": false,
        "happy_path": false,
        "error_path": false,
        "pseudo_e2e_risk": true,
        "gap_description": ""
      }
    ],
    "score": 0,
    "gaps": []
  },
  "performance_test": {
    "benchmarks_found": 0,
    "load_tests_found": 0,
    "regression_thresholds_defined": false,
    "hot_paths_covered": 0,
    "total_hot_paths": 0
  },
  "issues": [
    {
      "category": "test_coverage",
      "severity": "critical|high|medium|low",
      "confidence": 0.0,
      "deterministic": true,
      "source": "",
      "file": "",
      "line": 0,
      "location": {"file": "", "start_line": 0, "end_line": 0},
      "diff_hunk": "",
      "type": "missing_unit_test|missing_test_layer|low_assertion_density|surviving_mutation|missing_api_test|missing_negative_case|missing_auth_case|missing_e2e_journey|pseudo_e2e|missing_performance_test|missing_regression_threshold",
      "evidence_chain": [],
      "impact": "",
      "recommendation": "",
      "metadata": {
        "journey": "",
        "mutation": "",
        "endpoint": "",
        "auto_fixable": false,
        "fix_command": "",
        "suggested_patch": ""
      }
    }
  ]
}
```

- `critical_journeys[]`: each identified journey with coverage status
- `pseudo_e2e_risk`: true if existing tests match pseudo-E2E patterns (page-visit-only, happy-path-only, mocked)
- Score 0-100: mutation score overrides coverage percentage for unit tests. For E2E: weighted by journey criticality.
