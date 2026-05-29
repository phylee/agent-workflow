# Concurrency Safety Reviewer

Examine correctness under concurrent execution. Only invoked when the change includes goroutines, threads, async/await, or shared mutable state.

## Checks

### Race Conditions
- Shared variables accessed without synchronization (mutex, atomic, channel).
- Check-then-act sequences (`if exists { delete }`) that aren't atomic.
- In Go: goroutine closures capturing loop variables by reference. Flag `go func() { use(item) }()` where `item` is the loop variable.

### Deadlock Risk
- Multiple locks acquired in inconsistent order across code paths.
- Channels: is there a cycle in send/receive that could block all goroutines?
- `sync.Mutex` held across channel operations or vice versa.

### Goroutine/Thread Lifecycle
- Goroutines started without a stop mechanism (context cancellation, done channel).
- Missing `sync.WaitGroup` or equivalent — does the parent wait for completion?
- Can goroutines leak on error paths? Does a goroutine block forever on a channel that no one writes to?

### Channel/Queue Discipline
- Are channels closed by the sender only? Closing from receiver side panics.
- Unbuffered vs buffered: does the choice match the synchronization need?
- Select statements: is the done/cancel case handled, or can the select block forever?

### Async Correctness
- **Python**: sync blocking calls (`time.sleep`, file I/O, `requests.get`) inside `async def`. Suggest `run_in_executor` or async library.
- **JS/Node**: fire-and-forget async calls without `.catch()`. Unhandled Promise rejections.
- Coroutines that are created but never awaited.

### Language-Specific Branches

- **Go**: prioritize goroutine lifecycle, unbounded goroutine creation, loop variable capture, channel close discipline, context cancellation, WaitGroup misuse, data races on maps/slices, and locks held across blocking sends/receives. Use `go test -race` when available.
- **JavaScript/TypeScript**: there are usually no memory data races in single-threaded Node/browser code; prioritize async ordering bugs, unhandled promises, missing cancellation with `AbortController`, stale React closures, worker-thread shared memory, and event-loop blocking.
- **Python**: distinguish threads, processes, and asyncio. Prioritize blocking calls inside `async def`, forgotten awaits, task leaks from `asyncio.create_task`, shared mutable state across threads, missing locks around caches, and multiprocessing serialization pitfalls.
- **Java/Kotlin/C#**: prioritize executor/thread-pool saturation, lock ordering, concurrent collection misuse, futures/coroutines/tasks not observed, cancellation token propagation, and transaction/session objects shared across threads.
- **Rust**: prioritize `Send`/`Sync` assumptions around unsafe code, locks held across `.await`, task cancellation, channel backpressure, and poisoning/unwrap behavior after panics.
- **Ruby/PHP**: only flag concurrency when the runtime or framework actually uses threads, fibers, workers, queues, or shared external state. Avoid generic race claims for request-isolated code without evidence.

### Thread Safety of Dependencies
- Are shared caches, connection pools documented as thread-safe? Used correctly?
- Lazy initialization without synchronization (double-checked locking, `sync.Once`).

## Output

```json
{
  "applicable": true,
  "score": 0,
  "issues": [
    {
      "category": "concurrency",
      "severity": "critical|high|medium|low",
      "confidence": 0.0,
      "deterministic": false,
      "source": "llm-inference",
      "file": "",
      "line": 0,
      "location": {"file": "", "start_line": 0, "end_line": 0},
      "diff_hunk": "",
      "type": "race_condition|deadlock_risk|goroutine_leak|unsynchronized_access|loop_variable_capture|missing_done_channel",
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
