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

### 5. Error Handling (error_handling)
Examine how the code deals with failure. This is distinct from testing — it's about the robustness of the production code itself, not the tests that verify it.

- **Error propagation**: Are errors properly wrapped with context before being returned upstream (e.g., `fmt.Errorf("...: %w", err)` in Go, `raise ... from e` in Python, `throw new Error("...", { cause: e })` in JS)? Are errors silently swallowed without logging or propagation?
- **Error classification**: Does the code distinguish between recoverable and non-recoverable errors? Are transient errors (network timeouts, deadlocks) retried with backoff? Are permanent errors (validation failures, auth errors) surfaced immediately?
- **Retry & resilience**: For distributed systems, are retries using exponential backoff with jitter? Is there a maximum retry count or deadline? Are idempotency keys used for retried writes?
- **Graceful degradation**: Is there a fallback path when a non-critical dependency is unavailable (e.g., stale cache vs. error)? Are circuit breakers used to prevent cascading failures?
- **Panic/recover discipline**: In Go, is `recover()` used only in deliberate locations (top-level goroutine, middleware), not as a crutch? In Python, are bare `except:` clauses caught (already flagged in code_quality, but here the focus is on whether the recovery action is correct)?
- **Resource cleanup**: Are files, connections, locks, and goroutines cleaned up on error paths? Is `defer`/`try-finally`/`context manager` usage correct? Are there leaks in early-return or exception paths?

### 6. Concurrency Safety (concurrency_safety)
When the code uses threads, goroutines, async/await, or shared mutable state, examine correctness under concurrent execution. Skip if the code is single-threaded and stateless — set `score` to 100 and mark `applicable: false`.

- **Race conditions**: Are shared variables accessed without synchronization? Are check-then-act sequences (e.g., `if exists { delete }`) atomic? In Go, run mental data race analysis on goroutine variable captures — does the closure capture a loop variable by reference?
- **Deadlock risk**: Are multiple locks acquired in inconsistent order across code paths? Are channels closed by the sender only? Is there a cycle in the dependency graph of synchronized resources?
- **Goroutine/thread lifecycle**: Are goroutines started without a way to stop them (context cancellation, done channel)? Is there a `sync.WaitGroup` or equivalent to wait for completion? Can goroutines leak on error paths?
- **Channel/queue discipline**: In Go, are channels closed by the sender? Are unbuffered channels used where buffered would prevent deadlocks (and vice versa)? Are select statements handling the done/cancel case?
- **Async correctness**: In Python/Node, are synchronous blocking calls (file I/O, CPU-heavy work) offloaded to a thread pool or worker? Are coroutines properly awaited — no fire-and-forget without error handling? In JS, are Promise chains correctly terminated with `.catch()`?
- **Thread safety of dependencies**: Are shared caches, connection pools, and third-party objects documented as thread-safe? Are they used correctly under concurrency?

### 7. API / Interface Design (api_design)
When the change adds or modifies public functions, HTTP endpoints, RPC methods, or library interfaces, examine the contract design. Skip if the change is purely internal implementation detail — set `score` to 100 and mark `applicable: false`.

- **Consistency**: Do new functions follow the same naming, parameter order, and return type conventions as existing ones? In HTTP APIs, are URL paths consistent (plural nouns, kebab-case)? Are error response bodies following the project's standard envelope?
- **Idempotency**: Are state-changing operations idempotent where the client would reasonably retry (PUT, DELETE)? Is idempotency documented for create operations that use client-supplied IDs?
- **Backward compatibility**: Does this change break existing callers? Was a parameter added as optional (OK) or was the signature changed without an adapter (breaking)? In REST APIs, was a field removed from the response without versioning?
- **Parameter design**: Are boolean flag parameters a smell (encourage `doThing(includeDetails=true)` over `doThingWithDetails()`)? Are there too many positional parameters (>4)? Should related parameters be grouped into a struct/object?
- **Return type hygiene**: Are null/None/nil returns documented? Is the function returning an empty collection vs. null? Are errors and partial results distinguishable? In typed languages, is `Optional<T>` used instead of `@Nullable T`?
- **Naming clarity**: Does the function name clearly describe what it does (verb + noun)? Are abbreviations avoided unless they're universal domain terms? Is the behavior surprising given the name (side effects, hidden dependencies)?

### 8. Logging & Observability (logging)
Check whether the code produces useful diagnostic signals for production debugging. This dimension is about operational readiness, not code correctness.

- **Log levels**: Are errors logged at ERROR/WARN level? Is DEBUG used for noisy diagnostic detail? Is INFO used for key lifecycle events (server start, config loaded, migration complete)? Are there `console.log`/`print()` calls that should use a proper logger?
- **Structured logging**: Are key-value pairs used instead of string interpolation in log messages? This is critical for log aggregation tools (ELK, Datadog, Loki) — `log.Info("user created", "user_id", id)` not `log.Info(f"user {id} created")`.
- **PII in logs**: Is personally identifiable information (emails, names, IPs, tokens, passwords) being logged? Even at DEBUG level, PII in logs is a compliance risk under GDPR, SOC 2, etc.
- **Trace instrumentation**: Are incoming requests assigned a trace ID / request ID? Is this ID propagated to downstream calls and included in log entries? In HTTP handlers, is there middleware that injects and logs the request ID?
- **Metric coverage**: Are key operational metrics exposed — request latency, error rate, queue depth, connection pool utilization? Is the code incrementing counters for important events (login failures, rate limit hits, data export)?
- **Alertable conditions**: Would an on-call engineer be able to diagnose a production issue from the signals this code emits? Are there gaps where a failure would be silent (no log, no metric) until users report it?

### 9. Security (security)
Apply OWASP Top 10 awareness and language-specific vulnerability patterns:
- **Injection**: SQL injection, command injection, LDAP injection, XPath injection. Check that parameterized queries are used, not string concatenation.
- **XSS**: In web contexts, check that user input is sanitized before rendering. Flag `dangerouslySetInnerHTML`, `innerHTML`, `document.write`.
- **CSRF**: Check for missing CSRF tokens on state-changing requests.
- **Authentication/Authorization**: Hardcoded credentials, weak password policies, missing rate limiting, overly permissive CORS, path traversal in file operations.
- **Sensitive data**: Secrets in code, logging of PII/tokens/passwords, missing encryption at rest, hardcoded API keys.
- **Dependencies**: Check dependency files (`package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `Cargo.toml`) for known-vulnerable version patterns or deprecated packages.

For each vulnerability found, include the CWE ID where applicable.

### 10. Overall Score and Recommendations
Calculate `overall_score` as a weighted average:
- code_quality: 15%
- test_coverage: 15%
- performance: 10%
- database: 10% (0% if no database changes present, redistributing the weight proportionally)
- error_handling: 15%
- concurrency_safety: 10% (0% if no concurrent code present, redistributing the weight proportionally)
- api_design: 4% (0% if no API surface changes, redistributing the weight proportionally)
- logging: 5%
- security: 16%

The conditional dimensions (database, concurrency_safety, api_design) auto-detect applicability. When one is skipped, its weight is distributed proportionally among the remaining active dimensions. Security always gets the highest single weight because a single vulnerability can be catastrophic. If `focus_areas` is specified, weight those areas 2x and rebalance.

Generate prioritized recommendations. **Immediate** = critical or high-severity issues that block deployment. **Short-term** = should address in the next sprint. **Long-term** = architectural improvements. Include an `effort_estimate` (e.g., "2h", "1d", "1w") to help with planning.

## Output Format

Always output the result as a single JSON object matching the schema in `references/output-schema.md`. Read that file for the exact structure. The root key is `code_review_result`.

After the JSON, provide a brief human-readable summary (3-5 sentences) highlighting the most important findings — the things that actually warrant the user's attention.

## Parameters

The user may pass these optional parameters inline or as structured input:
- `language`: `"auto"` (default) or a specific language like `"python"`, `"javascript"`, `"typescript"`, `"java"`, `"go"`, `"rust"`, `"ruby"`, `"php"`, `"c"`, `"cpp"`, `"csharp"`
- `focus_areas`: Array of areas to emphasize, e.g. `["security", "performance"]`. Valid values: `"code_quality"`, `"test_coverage"`, `"performance"`, `"database"`, `"error_handling"`, `"concurrency_safety"`, `"api_design"`, `"logging"`, `"security"`
- `strictness`: `"lenient"` (relaxed, only flag clear bugs), `"normal"` (balanced, default), `"strict"` (flag everything, prefer explicit over implicit)

## Language-Specific Guidance

When reviewing code in a language you're less familiar with, or when you need specific style guide details, read `references/language-standards.md`. It contains detailed checklists for Python, JavaScript/TypeScript, Java, Go, and guidance for other languages.
