---
name: code-inspector
description: Comprehensive code review and inspection — code standards, test coverage, performance, and security audit with structured scoring. Use this skill whenever the user asks for code review, code inspection, code audit, code quality check, PR review, security audit of code, or wants a detailed analysis of any code file/directory/diff. Also trigger when the user wants to "check my code", "review this PR", "audit for vulnerabilities", "inspect code quality", "analyze test coverage", or mentions code review in the context of CI/CD or pre-commit checks.
---

# Code Inspector

Orchestrate a multi-dimensional code review: gather context → classify → dispatch to specialized reviewers → aggregate. Token usage is proportional to change complexity — a simple frontend PR doesn't load the database or concurrency reviewer.

## Workflow

### Step 1: Parse Input

Accept input in one of these forms:

**A) Structured JSON** (preferred):
```json
{
  "language": "typescript",
  "framework": "nestjs",
  "change_type": "feature|bugfix|refactor|hotfix",
  "service_type": "api|frontend|worker|database|infra|library|cli",
  "git_diff": "...",
  "changed_files": ["src/auth/login.ts", "src/auth/middleware.ts"],
  "dependency_changes": ["added: rate-limiter@2.1.0"],
  "test_files": ["src/auth/login.test.ts"],
  "api_contract_changes": ["POST /auth/login response adds refreshToken"],
  "risk_level": "low|medium|high"
}
```
If the user provides this JSON, use it directly. Validate and fill gaps.

**B) PR URL**: Use `gh pr view <url> --json title,body,files,additions,deletions` and `gh pr diff <url>` to extract the structured input automatically. Parse the diff to identify changed files, languages, and service type.

**C) Raw `git diff` or file paths**: Read the diff/files directly, then auto-detect everything in Step 2.

### Step 2: Gather Context (Beyond the Diff)

A diff hunk alone is insufficient — surrounding code determines whether a change is safe. For each modified function/method:

1. **Read the full function body** from the source file — not just the diff hunk. Many bugs are invisible in the diff because the problematic code sits just outside the ± lines.
2. **Find callers**: grep for the function name. If a signature changed, check that all callers were updated.
3. **Find callees**: note what the modified function calls — if a dependency was also changed, check consistency.
4. **Check imports/dependencies**: if new packages were added, note them. If existing imports were removed, verify they're unused elsewhere.
5. **For API handlers**: grep for the route registration to understand middleware chain, auth guards, validation pipes applied to this handler.

### Step 3: Classify the Change

Determine `service_type` first — different service types need fundamentally different review strategies. Read `references/classification-guide.md` for the mapping of service types to their primary reviewers, extra checks, and recommended weight adjustments.

Classify which reviewers to activate using these signals:

| Signal | Activated Reviewer |
|---|---|
| `.sql`, `.prisma`, migration dir, `CREATE TABLE`, `ALTER TABLE`, ORM model/schema changes | `database` |
| `auth`/`login`/`token`/`password`/`session`/`oauth`/`jwt` in paths or code | `security` |
| `go func`, `goroutine`, `sync.Mutex`, `sync.WaitGroup`, `chan `, `async`/`await`, `Promise`, `threading`, `concurrent` | `concurrency_safety` |
| New/changed HTTP routes, RPC definitions, GraphQL schema, public exported functions, API handler files | `api_design` |
| `try`/`catch`/`except`/`recover`/`defer`/`err != nil`/`if err` patterns | `error_handling` |
| `log.`, `logger.`, `console.log`, `print(`, `logging.`, observability config | `logging` |
| `.jsx`, `.tsx`, `.vue`, `.svelte`, `.css`, `.scss` files | `code_quality` (frontend focus) |
| **Always active** (baseline) | `code_quality`, `test_coverage`, `performance`, `error_handling`, `logging`, `security` |

User-specified `focus_areas` override and force-activate their reviewers.

Output the classification:

```json
{
  "change_classification": {
    "service_type": "api",
    "change_types": ["api", "security-sensitive"],
    "risk_level": "high",
    "languages": ["typescript"],
    "framework": "nestjs",
    "affected_layers": ["auth"],
    "files_changed": 2,
    "lines_changed": 45
  },
  "activated_reviewers": [
    "code_quality", "test_coverage", "performance",
    "error_handling", "logging", "security", "api_design"
  ]
}
```

### Step 4: Dispatch to Reviewers

For each reviewer in `activated_reviewers`, read its file at `reviewers/<name>.md` and apply its instructions. Each reviewer is ~50 lines and focused on one dimension. Only load activated reviewers.

Apply the `service_type`'s extra checks (from `references/classification-guide.md`) as additional lenses on top of the base reviewer instructions. For example, an `api` service type means the security reviewer should emphasize auth/rate-limit/input validation; a `worker` service type means the error_handling reviewer should emphasize retry/idempotency/DLQ.

### Step 5: Aggregate Results

Combine each reviewer's output into the final `code_review_result` JSON. Read `references/output-schema.md` for the exact structure. Root key is `code_review_result`.

Set `applicable: false` and `score: 100` for any dimension whose reviewer was not activated.

Calculate `overall_score` using the weight table in `references/output-schema.md`. Apply any service-type weight adjustments from `references/classification-guide.md`. User-specified `focus_areas` get 2x weight. Conditional dimensions that were skipped have their weight redistributed.

### Step 6: Summarize

After the JSON, output a 3-5 sentence human-readable summary highlighting the most important findings — the things that would block deployment or warrant immediate attention.

## Parameters

- `language`: `"auto"` (default) or specific: `"python"`, `"javascript"`, `"typescript"`, `"java"`, `"go"`, `"rust"`, `"ruby"`, `"php"`, `"c"`, `"cpp"`, `"csharp"`
- `focus_areas`: Array to emphasize, e.g. `["security", "performance"]`. Forces activation of those reviewers.
- `strictness`: `"lenient"` (only clear bugs), `"normal"` (balanced, default), `"strict"` (flag everything)
- `service_type`: Override auto-detected service type. One of: `"api"`, `"frontend"`, `"worker"`, `"database"`, `"infra"`, `"library"`, `"cli"`

For language-specific conventions, read `references/language-standards.md` as needed.
