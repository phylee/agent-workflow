# Test Coverage Reviewer

**Principle**: Coverage percentages are vanity metrics. Use three deterministic signals: test existence, assertion density, and mutation testing. For E2E, check user journey coverage — not "do E2E tests exist?" but "are critical journeys actually verified end-to-end?"

## Step 1: Check Test Existence

- Look for test files alongside source files: `*_test.go`, `*.test.js`, `*.spec.ts`, `test_*.py`, `*Test.java`.
- If zero tests exist, set `score: 0` and stop.

## Step 2: Measure Assertion Density (Quick Heuristic)

Count assertions across test files. An assertion verifies behavior: `assert`, `expect(...).toBe`, `Assert.assertEquals`, `if !condition { t.Error }`, `should be_eq`.

- **assertions_per_test < 1**: tests run code but never verify output. Equivalent to no tests.
- **assertions_per_test < 3**: minimal. Likely only happy path.
- **assertions_per_test >= 5**: reasonable.

Flag quality issues:
- `assert true` / `expect(true).toBe(true)` — worthless
- `assert response.status_code == 200` with no body verification — verifies framework, not logic
- Mocks without `assert_called` — test passes even if mock never invoked

## Step 3: Run Mutation Testing (Deterministic Quality)

Mutation testing injects bugs into source code, then runs tests. Surviving mutations = ineffective tests.

| Language | Tool | Command |
|---|---|---|
| Python | mutmut | `mutmut run --paths-to-mutate <file>` |
| JavaScript/TypeScript | Stryker | `npx stryker run --mutate <files>` |
| Java | PIT | `mvn pitest:mutationCoverage` |
| Go | gremlins | `gremlins unleash` |
| Ruby | mutant | `mutant run <file>` |

If tool not available, skip and note the limitation.

- **mutation_score >= 80%**: excellent
- **50-80%**: adequate
- **< 50%**: poor — tests exist but don't verify behavior
- **< 20%**: decorative — effectively untested

For each surviving mutation, explain what the mutation was, why it survived, and what test to add.

## Step 4: E2E — User Journey Coverage

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

## Output

```json
{
  "score": 0,
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
  }
}
```

- `critical_journeys[]`: each identified journey with coverage status
- `pseudo_e2e_risk`: true if existing tests match pseudo-E2E patterns (page-visit-only, happy-path-only, mocked)
- Score 0-100: mutation score overrides coverage percentage for unit tests. For E2E: weighted by journey criticality.
