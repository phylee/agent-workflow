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
- **Go**: `if err != nil { return err }` without wrapping, `_ = doSomething()`, `panic` in non-init code.
- **Python**: bare `except:`, `except Exception:` that swallows KeyboardInterrupt, missing `finally`.
- **JS/TS**: `.catch()` with empty handler, `try { await ... } catch {}`, unhandled Promise rejections.

## Output

```json
{
  "score": 0,
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "confidence": 0.0,
      "deterministic": false,
      "source": "llm-inference",
      "file": "",
      "line": 0,
      "type": "swallowed_error|missing_context|bare_except|missing_retry|resource_leak|no_fallback",
      "evidence_chain": [],
      "message": "",
      "suggestion": ""
    }
  ]
}
```
