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
  "base_branch": "main",
  "pr_description": "Why this change exists and what trade-offs were intentional.",
  "reviewer_context": "initial|re-review",
  "previous_result": null,
  "team_standards": {
    "style_guide": "project-default",
    "allowed_exceptions": ["TODO allowed in experimental modules"],
    "required_checks": ["unit", "api", "e2e", "security"]
  },
  "context_budget": {
    "max_context_files": 30,
    "call_graph_depth": 2,
    "max_file_bytes": 120000
  },
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

Use `pr_description` to understand intent, but do not let intent override a concrete correctness, security, data-loss, or compatibility issue. Use `reviewer_context: "re-review"` with `previous_result` to verify whether previous findings were actually fixed and to avoid re-reporting already-resolved issues. `previous_result` should be the prior full `code_inspector_result` object, or `null` when unavailable. Use `team_standards` to tune style-only findings; never use team preferences to suppress critical defects.

### Step 2: Gather Context (Beyond the Diff)

A diff hunk alone is insufficient — surrounding code determines whether a change is safe. For each modified function/method:

1. **Read the full function body** from the source file — not just the diff hunk. Many bugs are invisible in the diff because the problematic code sits just outside the ± lines.
2. **Find callers**: grep for the function name. If a signature changed, check that all callers were updated.
3. **Find callees**: note what the modified function calls — if a dependency was also changed, check consistency.
4. **Check imports/dependencies**: if new packages were added, note them. If existing imports were removed, verify they're unused elsewhere.
5. **For API handlers**: grep for the route registration to understand middleware chain, auth guards, validation pipes applied to this handler.

#### Context Budget

Bound context gathering so reviews stay predictable on large repositories:
- Default `max_context_files`: 30. Count changed files, direct test files, and caller/callee files.
- Default `call_graph_depth`: 2. Depth 1 = direct callers/callees; depth 2 = callers of callers and callees of callees.
- Default `max_file_bytes`: 120000 per file. If a file is larger, read only the relevant symbol, imports, nearby type definitions, and route/registration code.
- Stop expanding when the budget is reached. Record skipped files or truncated reads in `limitations[]`.

Without LSP or a language server, approximate dependency discovery with `rg`:
- Search exact symbol names first.
- For methods, search receiver/class + method where the language makes that possible.
- For routes, search route path, handler name, controller class, and exported registration function.
- Treat dynamic dispatch, reflection, monkey patching, dependency injection containers, and framework magic as lower-confidence call graph evidence.

### Step 3: Classify the Change

Determine `service_type` first — different service types need fundamentally different review strategies. Read `references/classification-guide.md` for the mapping of service types to their primary reviewers, extra checks, and recommended weight adjustments.

Classify which reviewers to activate. The baseline reviewers always run. Conditional reviewers activate on signal:

| Signal | Additionally Activates |
|---|---|
| `.sql`, `.prisma`, migration dir, `CREATE TABLE`, `ALTER TABLE`, ORM model/schema changes | `database` |
| `go func`, `goroutine`, `sync.Mutex`, `sync.WaitGroup`, `chan `, `async`/`await`, `Promise`, `threading`, `concurrent` | `concurrency` |
| New/changed HTTP routes, RPC definitions, GraphQL schema, public exported functions, API handler files | `api_design` |
| **Always active** (baseline) | `code_quality`, `test_coverage`, `performance`, `error_handling`, `logging`, `security` |

Reviewer file names use hyphens: `api_design` → `reviewers/api-design.md`, `test_coverage` → `reviewers/test-coverage.md`, `error_handling` → `reviewers/error-handling.md`. All others match literally: `reviewers/<name>.md`.

User-specified `focus_areas` force-activate reviewers. Valid values match the category names in output-schema.md: `code_quality`, `test_coverage`, `performance`, `database`, `error_handling`, `concurrency`, `api_design`, `logging`, `security`.

Output the classification:

```json
{
  "change_classification": {
    "service_type": "api",
    "change_type": "feature|bugfix|refactor|hotfix",
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

For each reviewer in `activated_reviewers`, read its file at `reviewers/<name>.md` and apply its instructions. Only load activated reviewers.

Apply the `service_type`'s extra checks from `references/classification-guide.md`.

Before applying a reviewer, select the language/framework branch inside that reviewer. If the reviewer has no exact branch for the language, use the closest runtime family from `references/language-standards.md` and record the fallback in `limitations[]`. Do not apply a rule from one language/runtime to another without evidence; for example, Go goroutine leaks, JavaScript unhandled promises, Python swallowed exceptions, and Hibernate N+1 queries are different failure modes.

#### Tool Policy

Use deterministic tools when they are already available in the environment. Do not install dependencies, download rule packs, or make network calls unless the user explicitly approves it.

For each tool attempt, record the outcome in `tool_runs[]`:
- `tool`: command or tool name
- `status`: `success|failed|unavailable|skipped`
- `deterministic`: `true` for tool output, `false` for LLM-only fallback
- `summary`: short result or failure reason

If a tool is unavailable or skipped, continue with prompt-based review and add a matching item to `limitations[]`. Prompt-based findings must use `deterministic: false` and should not exceed `confidence: 0.85` unless backed by exact code evidence.

Every finding from every reviewer must include:
- `confidence` (0.0-1.0): use the exact bands in `references/output-schema.md`; do not redefine thresholds locally
- `deterministic` (true/false): from a tool (Semgrep, ESLint, AST) = true; LLM inference = false
- `location` with `file`, `start_line`, and `end_line`: use new-file line numbers for PR annotations when possible
- `diff_hunk`: smallest relevant changed hunk when available, or `""` if the issue is outside the diff context
- `evidence_chain` (ordered list): trace from input → dataflow → unsafe sink → impact
- `metadata` (object, optional): reviewer-specific extra fields such as CVE IDs, contract type, mutation details, database table/column names, `auto_fixable`, `fix_command`, or `suggested_patch`

In `reviewer_context: "re-review"` mode, compare current findings against the previous review when available. Use the fingerprint algorithm in `references/output-schema.md`:
1. Compute a fingerprint for every `previous_result.code_inspector_result.inspections[]` item and build the previous fingerprint set.
2. Compute a fingerprint for every current `inspections[]` item and build the current fingerprint set.
3. Populate `review_delta.resolved_since_last[]`, `review_delta.new_since_last[]`, and `review_delta.unchanged_since_last[]` from previous-current set differences and intersections.

### Step 5: Aggregate Results

Combine all reviewer findings into `inspections[]` — a flat list. Map reviewer-specific fields to the canonical `inspections[]` field names:

| Reviewer Field | `inspections[]` Field |
|---|---|
| `message` / `description` / `mechanism` / `why_survived` | `impact` (what happens if not fixed) |
| `suggestion` / `fix` / `remediation` / `test_to_add` / `migration_path` | `recommendation` (concrete fix) |
| `file` + `line` (separate fields) | `location.file` + `location.start_line`; also copy to `file` + `line` shorthand for compatibility |
| `file` + `start_line` + `end_line` | `location` and compatibility shorthand |
| raw changed hunk text | `diff_hunk` |
| `location` (combined string) | `location` (parse apart if possible) |
| `rule_id` | `source` (prepend tool name: `"eslint:no-unused-vars"`) |
| `type` | `type` (keep as-is) |
| `severity` | `severity` (keep as-is) |
| `confidence`, `deterministic`, `evidence_chain` | pass through as-is |
| reviewer-specific fields | `metadata` |

`location` is canonical. `file` and `line` are backward-compatible shorthand only and must always equal `location.file` and `location.start_line`.

Assign a unique `id` (e.g., `SEC-001`, `PERF-003`) to each inspection.

Populate `coverage` with assertion density and mutation score from the test reviewer.
Populate `gates`: `merge_blocked: true` if any `critical AND deterministic` finding, or `critical AND confidence >= 0.7`, or any gate rule from output-schema.md fires.
Calculate `summary` scores per dimension using the weight table.

Read `references/output-schema.md` for the exact structure. Root key is `code_inspector_result`.

### Step 6: Summarize

Return exactly one JSON object with root key `code_inspector_result`. Do not output prose before or after the JSON. Put the gate verdict in `gates.verdict`, the short explanation in `summary.human_summary`, and inline summary objects for the most impactful findings in `top_findings[]`.

## Parameters

- `language`: `"auto"` (default) or specific: `"python"`, `"javascript"`, `"typescript"`, `"java"`, `"go"`, `"rust"`, `"ruby"`, `"php"`, `"c"`, `"cpp"`, `"csharp"`
- `focus_areas`: Array to emphasize, e.g. `["security", "performance"]`. Forces activation of those reviewers.
- `strictness`: `"lenient"` (only clear bugs), `"normal"` (balanced, default), `"strict"` (flag everything)
- `service_type`: Override auto-detected service type. One of: `"api"`, `"frontend"`, `"worker"`, `"database"`, `"infra"`, `"library"`, `"cli"`

For language-specific conventions, read `references/language-standards.md` as needed.
