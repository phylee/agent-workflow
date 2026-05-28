---
name: code-inspector
description: Comprehensive code review and inspection — code standards, test coverage, performance, and security audit with structured scoring. Use this skill whenever the user asks for code review, code inspection, code audit, code quality check, PR review, security audit of code, or wants a detailed analysis of any code file/directory/diff. Also trigger when the user wants to "check my code", "review this PR", "audit for vulnerabilities", "inspect code quality", "analyze test coverage", or mentions code review in the context of CI/CD or pre-commit checks.
---

# Code Inspector

Perform comprehensive, multi-dimensional code review and output a structured JSON scoring report. This skill is designed to identify issues across code quality, testing, performance, and security — not just surface-level style nits.

## Core Principles

- **Be constructive, not pedantic.** Every issue flagged should include a concrete, actionable suggestion. Don't just point out what's wrong — explain how to fix it and why it matters.
- **Adapt strictness to context.** A prototype or hackathon project gets different treatment than production-critical code. Respect the user's `strictness` parameter.
- **Language awareness is essential.** Standards vary drastically by language. Don't apply Python conventions to Go code. Read `references/language-standards.md` for language-specific guidance when needed.
- **Focus matters.** If the user specifies `focus_areas`, spend disproportionate effort there. A security-focused review should dig deep into OWASP Top 10, auth flows, and data handling — not spend equal time on naming conventions.

## Input Discovery

The user may provide:
- A file path: read it directly
- A directory path: scan recursively for source files (exclude `node_modules`, `.git`, `vendor`, `__pycache__`, `venv`, `.venv`, `dist`, `build`, `target`)
- A code snippet: ask for the language if not obvious
- A git diff or PR: use `git diff` to inspect changes

If `language` is not specified, auto-detect from file extensions or shebangs. If ambiguous, ask.

## Review Dimensions

### 1. Code Quality (code_quality)
Examine naming, structure, complexity, and readability. Language-specific standards take priority — check `references/language-standards.md`. Key checks:
- **Naming**: Are names descriptive and following conventions? (camelCase, snake_case, PascalCase as appropriate)
- **Structure**: Are functions/classes reasonably sized? Is there deep nesting (>3 levels)? Are there god objects or functions with too many parameters?
- **Complexity**: Flag cyclomatic complexity issues. Nested loops/conditionals >3 deep. Functions >50 lines deserve scrutiny. Ternary chains or complex boolean expressions should be simplified.
- **Readability**: Magic numbers, unclear variable names, missing or misleading comments, dead code.

Score `standards_compliance` as a percentage (0-100) for each sub-dimension. For the `score` field, use a weighted average.

### 2. Test Coverage (test_coverage)
Analyze existing tests if present:
- **Unit tests**: Check if tests exist, what coverage they provide. Flag untested edge cases (null/empty inputs, boundary values, error paths). Review mock usage — are mocks verifying behavior or just papering over untestable code? Are assertions actually meaningful?
- **API tests**: If the code exposes HTTP endpoints, check whether all status codes are tested (including error codes like 400, 401, 403, 404, 500). Verify request validation and response schema testing.
- **E2E tests**: For applications, check whether critical user journeys have end-to-end coverage. Flag integration points that lack tests.

If no tests exist at all, the score should reflect that gap prominently.

### 3. Performance (performance)
Look for common anti-patterns:
- **N+1 queries**: Loops that make database calls on each iteration
- **Missing indexes**: Queries filtering/sorting on unindexed columns
- **Memory issues**: Large objects held in memory, missing pagination, unbounded collections, closure leaks in JS
- **Blocking I/O**: Synchronous operations in async contexts (especially in Python/Node)
- **Algorithm complexity**: O(n²) or worse where O(n log n) or O(n) is achievable
- **Caching gaps**: Repeated computation that could be memoized or cached
- **Bundle/asset size**: In frontend code, check for large imports, missing tree-shaking, unoptimized assets

Estimate time/space complexity for the main algorithm paths. Identify the top 1-3 bottlenecks.

### 4. Database (database)
When the change set includes SQL files, migration scripts, ORM model changes, or database-adjacent code, examine the database layer for correctness and safety. Skip this section if no database-related code is present — set `score` to 100 and mark `applicable: false`.

- **Migration safety**: Does the migration acquire heavy locks (e.g., `ALTER TABLE ... ADD COLUMN` without `NOT NULL DEFAULT` on large tables)? Is the migration reversible — can it be rolled back cleanly? Are data backfill operations batched to avoid long-running transactions?
- **Schema design**: Are columns using appropriate data types? Are there missing constraints (NOT NULL, UNIQUE, FOREIGN KEY, CHECK)? Are cascading deletes/updates intentional and safe? Are VARCHAR lengths reasonable?
- **Index strategy**: Are there missing indexes on columns used in WHERE, JOIN, ORDER BY, or GROUP BY clauses? Are there redundant or unused indexes? Are indexes selective enough to be useful? Are covering indexes used where appropriate?
- **Query patterns**: Flag `SELECT *` in production code — it breaks when schema changes and wastes I/O. Flag queries without LIMIT that could return unbounded rows. Check for inefficient JOIN order, missing JOIN conditions (cross joins), correlated subqueries that could be rewritten as JOINs.
- **Data integrity**: Are transactions used appropriately for multi-statement operations? Is the isolation level appropriate for the business logic? Are there race conditions from missing `SELECT ... FOR UPDATE` or equivalent locking?
- **Connection & pool management**: Are connections properly released back to the pool? Are there connection leaks from missing close/finally blocks? Are prepared statements reused where the driver supports it?
- **ORMs & query builders**: For ORM-heavy code, flag N+1 queries from lazy loading, missing `eager()`/`prefetch_related()` calls, bulk operations done in loops, and inefficient `save()` call patterns.

### 5. Security (security)
Apply OWASP Top 10 awareness and language-specific vulnerability patterns:
- **Injection**: SQL injection, command injection, LDAP injection, XPath injection. Check that parameterized queries are used, not string concatenation.
- **XSS**: In web contexts, check that user input is sanitized before rendering. Flag `dangerouslySetInnerHTML`, `innerHTML`, `document.write`.
- **CSRF**: Check for missing CSRF tokens on state-changing requests.
- **Authentication/Authorization**: Hardcoded credentials, weak password policies, missing rate limiting, overly permissive CORS, path traversal in file operations.
- **Sensitive data**: Secrets in code, logging of PII/tokens/passwords, missing encryption at rest, hardcoded API keys.
- **Dependencies**: Check dependency files (`package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `Cargo.toml`) for known-vulnerable version patterns or deprecated packages.

For each vulnerability found, include the CWE ID where applicable.

### 6. Overall Score and Recommendations
Calculate `overall_score` as a weighted average:
- code_quality: 20%
- test_coverage: 20%
- performance: 20%
- database: 10% (0% if no database changes present, redistributing the weight proportionally)
- security: 30%

Security always gets the largest weight because a single vulnerability can be catastrophic. If `focus_areas` is specified, weight those areas 2x and rebalance.

Generate prioritized recommendations. **Immediate** = critical or high-severity issues that block deployment. **Short-term** = should address in the next sprint. **Long-term** = architectural improvements. Include an `effort_estimate` (e.g., "2h", "1d", "1w") to help with planning.

## Output Format

Always output the result as a single JSON object matching the schema in `references/output-schema.md`. Read that file for the exact structure. The root key is `code_review_result`.

After the JSON, provide a brief human-readable summary (3-5 sentences) highlighting the most important findings — the things that actually warrant the user's attention.

## Parameters

The user may pass these optional parameters inline or as structured input:
- `language`: `"auto"` (default) or a specific language like `"python"`, `"javascript"`, `"typescript"`, `"java"`, `"go"`, `"rust"`, `"ruby"`, `"php"`, `"c"`, `"cpp"`, `"csharp"`
- `focus_areas`: Array of areas to emphasize, e.g. `["security", "performance"]`. Valid values: `"code_quality"`, `"test_coverage"`, `"performance"`, `"database"`, `"security"`
- `strictness`: `"lenient"` (relaxed, only flag clear bugs), `"normal"` (balanced, default), `"strict"` (flag everything, prefer explicit over implicit)

## Language-Specific Guidance

When reviewing code in a language you're less familiar with, or when you need specific style guide details, read `references/language-standards.md`. It contains detailed checklists for Python, JavaScript/TypeScript, Java, Go, and guidance for other languages.
