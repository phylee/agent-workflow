# Logging & Observability Reviewer

Check whether the code produces useful diagnostic signals for production debugging.

## Checks

### Log Levels
- ERROR/WARN for failures that need attention.
- INFO for key lifecycle events (server start, config loaded, migration complete, user signup, order placed).
- DEBUG for noisy diagnostic detail — not for production data.
- Flag `console.log`/`print()` left in production code — these bypass log level control and log aggregation.

### Structured Logging
- Are key-value pairs used instead of string interpolation? `log.Info("user created", "user_id", id)` not `log.Info(f"user {id} created")`. String interpolation breaks log aggregation (ELK, Datadog, Loki can't parse fields from a string).
- Are log field names consistent with the project's conventions (snake_case vs camelCase)?

### PII in Logs
- Emails, full names, IP addresses, phone numbers, tokens, passwords in log messages — flag even at DEBUG level. GDPR and SOC 2 don't care about log level.
- Are sensitive fields redacted/masked before logging (credit card numbers, SSNs)?

### Trace Instrumentation
- Are incoming requests assigned a trace ID / request ID?
- Is this ID propagated to downstream HTTP/RPC calls and included in log entries?
- In HTTP handlers: is there middleware that injects and logs the request ID? If this code adds a new handler, does it include trace context?

### Metrics & Alerting
- Key operational counters: request latency, error rate, queue depth, connection pool stats.
- Are important events incrementing counters? (login failures, rate limit hits, data exports, payment attempts)
- Would an on-call engineer be able to diagnose a production issue at 3am from the signals this code emits? Flag silent failure paths — places where an error can occur with no log and no metric.

## Output

```json
{
  "score": 0,
  "issues": [
    {
      "category": "logging",
      "severity": "critical|high|medium|low",
      "confidence": 0.0,
      "deterministic": false,
      "source": "llm-inference",
      "file": "",
      "line": 0,
      "type": "wrong_level|string_interpolation|pii_leak|missing_trace_id|console_log|missing_metric",
      "evidence_chain": [],
      "impact": "",
      "recommendation": "",
      "metadata": {}
    }
  ]
}
```
