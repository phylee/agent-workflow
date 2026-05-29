# Error Handling Reviewer

Examine how the code deals with failure — distinct from testing, this is about production robustness.

## Checks

### Error Propagation
- Are errors wrapped with context before being returned upstream? Look for `fmt.Errorf("...: %w", err)` in Go, `raise ... from e` in Python, `new Error("...", { cause: e })` in JS.
- Are errors silently swallowed? Flag `_ = err`, `catch {}` with empty body, bare `except:` in Python, discarded error returns.
- Do error messages contain enough context to debug (operation, inputs, upstream error)?

### Error Classification
- Does the code distinguish recoverable from non-recoverable errors?
- Are transient errors (network timeouts, deadlocks, 429 rate limits) retried with backoff?
- Are permanent errors (validation, auth, not found) surfaced immediately without retry?

### Retry & Resilience
- Are retries using exponential backoff with jitter (not fixed-interval)?
- Is there a maximum retry count or deadline?
- For idempotent writes, are idempotency keys used so retries are safe?

### Graceful Degradation
- Is there a fallback when a non-critical dependency is down (e.g., serve stale cache vs. error)?
- Are circuit breakers used to stop cascading failures to already-failing dependencies?

### Resource Cleanup
- Are resources (files, connections, locks, goroutines) cleaned up on all error paths, not just the happy path?
- Is `defer`/`try-finally`/context manager usage correct?
- Any leaks in early-return or exception paths?

### Language-Specific Signals
- **Python**: no compile-time checked errors. Focus on exception boundaries, bare `except:`, `except Exception` that swallows operational signals, missing `raise ... from e`, broad framework exception handlers that convert all failures to 500/200, context-manager cleanup, and async functions that hide sync failures.
- **Go**: errors are values. Focus on ignored error returns (`_ = err`, `rows, _ :=`), missing `%w` wrapping, `panic` outside init/test/main boundary, `nil, nil` returns, missing `defer rows.Close()`, missing `ctx` propagation, and errors lost inside goroutines.
- **JavaScript/TypeScript**: focus on unhandled Promise rejections, fire-and-forget promises without `.catch`, missing `await`, `try/catch` that returns partial success, lost `cause`, and Express/Nest/Koa async errors that bypass middleware.
- **Java/Kotlin**: distinguish checked vs unchecked exceptions. Focus on swallowed `catch (Exception)`, transaction rollback behavior, `CompletableFuture`/coroutine exception propagation, missing `try-with-resources`, and framework exception mappers.
- **Rust**: focus on `unwrap`/`expect` in production paths, discarded `Result`, lossy `map_err`, panics across FFI/thread boundaries, and missing context via `anyhow`/`thiserror`.
- **Ruby/PHP**: focus on broad rescue/catch blocks, framework handlers that hide validation/auth errors, missing transaction rollback, and resource cleanup in ensure/finally.

## Output

```json
{
  "score": 0,
  "issues": [
    {
      "category": "error_handling",
      "severity": "critical|high|medium|low",
      "confidence": 0.0,
      "deterministic": false,
      "source": "llm-inference",
      "file": "",
      "line": 0,
      "location": {"file": "", "start_line": 0, "end_line": 0},
      "diff_hunk": "",
      "type": "swallowed_error|missing_context|bare_except|missing_retry|resource_leak|no_fallback",
      "evidence_chain": [],
      "impact": "",
      "recommendation": "",
      "metadata": {
        "auto_fixable": false,
        "fix_command": "",
        "suggested_patch": ""
      }
    }
  ]
}
```
