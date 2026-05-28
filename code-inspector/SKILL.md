---
name: code-inspector
description: Comprehensive code review and inspection — code standards, test coverage, performance, and security audit with structured scoring. Use this skill whenever the user asks for code review, code inspection, code audit, code quality check, PR review, security audit of code, or wants a detailed analysis of any code file/directory/diff. Also trigger when the user wants to "check my code", "review this PR", "audit for vulnerabilities", "inspect code quality", "analyze test coverage", or mentions code review in the context of CI/CD or pre-commit checks.
---

# Code Inspector

Orchestrate a multi-dimensional code review by classifying changes first, then dispatching only to relevant specialized reviewers. This keeps token usage proportional to change complexity — a simple frontend PR doesn't load the database or concurrency reviewer.

## Workflow

### Step 1: Discover Input

Read the code from the user's provided path, directory, snippet, or `git diff`. Auto-detect language from file extensions. For directories, skip `node_modules`, `.git`, `vendor`, `__pycache__`, `venv`, `.venv`, `dist`, `build`, `target`.

### Step 2: Classify the Change

Scan the diff/code and output a classification. Use these heuristics:

| Signal | Activated Reviewer |
|---|---|
| `.sql`, `.prisma`, migration dir, `CREATE TABLE`, `ALTER TABLE`, ORM model/schema changes | `database` |
| `auth`/`login`/`token`/`password`/`session`/`oauth`/`jwt` in changed paths or code | `security` |
| `go func`, `goroutine`, `sync.Mutex`, `sync.WaitGroup`, `chan `, `async`/`await`, `Promise`, `threading`, `concurrent` | `concurrency_safety` |
| New/changed HTTP routes, RPC definitions, GraphQL schema, public exported functions, API handler files | `api_design` |
| `try`/`catch`/`except`/`recover`/`defer`/`err != nil`/`if err` patterns | `error_handling` |
| `log.`, `logger.`, `console.log`, `print(`, `logging.`, observability config | `logging` |
| `.jsx`, `.tsx`, `.vue`, `.svelte`, `.css`, `.scss` files | `code_quality` (frontend focus) |
| **Always active** (baseline): all code changes | `code_quality`, `test_coverage`, `performance` |

For user-specified `focus_areas`, force-activate those reviewers regardless of classification.

Output the classification as:

```json
{
  "change_classification": {
    "change_types": ["api", "database"],
    "risk_level": "high|medium|low",
    "languages": ["typescript", "go"],
    "affected_layers": ["auth", "payment"],
    "files_changed": 12,
    "lines_changed": 340
  },
  "activated_reviewers": [
    "code_quality", "test_coverage", "performance",
    "database", "api_design", "security"
  ]
}
```

### Step 3: Dispatch to Reviewers

For each reviewer in `activated_reviewers`, read its file at `reviewers/<name>.md` and apply its instructions to the relevant portions of the code. Each reviewer file is ~40-60 lines and focused on one dimension. You only load the reviewers that are activated — do not read reviewer files that aren't needed.

The baseline reviewers (`code_quality`, `test_coverage`, `performance`) are always activated. Conditional reviewers (`database`, `error_handling`, `concurrency_safety`, `api_design`, `logging`, `security`) are only loaded when the classification signals match.

For language-specific conventions, read `references/language-standards.md` as needed.

### Step 4: Aggregate Results

Combine each reviewer's output into the final `code_review_result` JSON. Read `references/output-schema.md` for the exact structure. The root key is `code_review_result`.

Set `applicable: false` and `score: 100` for any dimension whose reviewer was not activated.

Calculate `overall_score` using these weights (from `references/output-schema.md`). Conditional dimensions that were not activated have their weight redistributed proportionally among active ones.

### Step 5: Summarize

After the JSON, output a 3-5 sentence human-readable summary highlighting the most important findings.

## Parameters

- `language`: `"auto"` (default) or specific: `"python"`, `"javascript"`, `"typescript"`, `"java"`, `"go"`, `"rust"`, `"ruby"`, `"php"`, `"c"`, `"cpp"`, `"csharp"`
- `focus_areas`: Array to emphasize, e.g. `["security", "performance"]`. Forces activation of those reviewers.
- `strictness`: `"lenient"` (only clear bugs), `"normal"` (balanced, default), `"strict"` (flag everything)
