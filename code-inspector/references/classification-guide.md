# Classification Guide

**Weight adjustment rules**: All +/- adjustments apply to the base weight from the output-schema.md weight table. When a conditional dimension (database, concurrency, api_design) has 0% weight because no relevant code is present, its adjustment is moot — adjustments only take effect when the dimension is active (weight > 0%). When weight is redistributed from an inactive dimension, the active dimensions receive proportionally more weight, and their adjustments apply to the increased base.

## Service Type Detection

Detect `service_type` from these signals (check changed files, directory structure, and code patterns):

| Service Type | Detection Signals |
|---|---|
| `api` | HTTP route handlers, controllers, middleware, `@Get`/`@Post` decorators, `app.get(`/`app.post(`, request/response types |
| `frontend` | `.jsx`/`.tsx`/`.vue`/`.svelte` files, `useState`/`useEffect`, `styled-components`, CSS-in-JS, component files |
| `worker` | Queue consumers, job processors, `bull`/`sidekiq`/`celery` patterns, cron/scheduler, event handlers, message consumers |
| `database` | `.sql` files, migration directories, ORM model files, `CREATE TABLE`, `ALTER TABLE`, `db.migrate` |
| `infra` | `Dockerfile`, `docker-compose`, `.tf`/Terraform, `.yaml` K8s manifests, CI/CD config, IAM policies, `nginx.conf` |
| `library` | Package published to registry (`package.json` with exports, `setup.py`/`pyproject.toml`, `go.mod` as dependency), no server entrypoint |
| `cli` | `main()` entrypoint, `argparse`/`cobra`/`commander`/`click`, `os.Exit`/`process.exit`, stdout/stderr writes |

If multiple signals match, pick the dominant one. A NestJS project with DB migrations is `api` (DB is a supporting layer).

## Review Strategy by Service Type

Each service type adjusts which reviewers get primary emphasis and what extra checks apply on top of the base reviewer instructions.

### API
- **Primary reviewers**: security, api_design, error_handling
- **Extra checks**:
  - Input validation: are all request fields validated (type, range, length, format)?
  - Auth: is every endpoint behind authentication? Are there anonymous endpoints that should be protected?
  - Rate limiting: are login/signup/sensitive endpoints rate-limited?
  - Error responses: do error responses leak stack traces or internal state?
  - Content-Type handling: does the handler check Accept/Content-Type headers?
- **Weight adjustment**: security +5%, api_design +5%, offset from code_quality -5%, performance -5%

### Frontend
- **Primary reviewers**: code_quality, performance, security
- **Extra checks**:
  - XSS: `dangerouslySetInnerHTML`, `innerHTML`, `document.write`, unescaped template vars
  - State management: stale closures, missing deps in useEffect/useMemo, setState after unmount
  - Render performance: missing `key`, unnecessary re-renders, large component trees, missing virtualization
  - Accessibility: missing `aria-*` attributes, non-semantic HTML, missing alt text, keyboard navigation
  - Bundle: large dependencies, dead imports, unoptimized images, missing lazy loading
- **Weight adjustment**: code_quality +5%, performance +5%, offset from database -5%, concurrency -5%

### Worker
- **Primary reviewers**: error_handling, concurrency, performance, logging
- **Extra checks**:
  - Retry: is there a retry policy with backoff? Max retries? Dead letter queue?
  - Idempotency: can the same message be processed twice without side effects? Is there an idempotency key?
  - Graceful shutdown: does the worker drain in-flight jobs before exiting? SIGTERM handling?
  - Backpressure: is there a concurrency limit? What happens when the queue is full?
  - Observability: job duration metrics, success/failure counters, queue depth gauge
- **Weight adjustment**: error_handling +5%, concurrency +5%, offset from api_design -5%, test_coverage -5%

### Database
- **Primary reviewers**: database, performance
- **Extra checks**:
  - Locking: will this migration block writes? Is it batched for large tables?
  - Rollback: is there a tested down migration? Can it be rolled back after deployment?
  - Data integrity: are foreign keys enforced? Are there orphaned rows after deletion?
  - Connection pooling: is the pool size appropriate? Are connections released?
- **Weight adjustment**: database +10%, performance +5%, offset from api_design -5%, concurrency -5%, code_quality -5%

### Infra
- **Primary reviewers**: security, logging
- **Extra checks**:
  - Secrets: are there hardcoded secrets in config files? Are secrets mounted from a secret manager?
  - Network: overly permissive ingress/egress rules (0.0.0.0/0), missing TLS, exposed ports
  - Least privilege: does the IAM role/service account have more permissions than needed?
  - Resource limits: are CPU/memory limits set? Are there liveness/readiness probes?
  - Audit: are infrastructure changes logged? Is there an approval process?
- **Weight adjustment**: security +10%, offset from test_coverage -5%, api_design -5%

### Library
- **Primary reviewers**: api_design, test_coverage, code_quality
- **Extra checks**:
  - Public API stability: is the exported surface minimal and intentional? Are internal details leaked?
  - Documentation: are public functions documented? Is there a usage example?
  - Versioning: is this a breaking change? Does it follow semver?
  - Tree-shaking: can consumers import only what they need (named exports, side-effect-free)?
- **Weight adjustment**: api_design +10%, test_coverage +5%, offset from database -5%, concurrency -5%, performance -5%

### CLI
- **Primary reviewers**: error_handling, code_quality
- **Extra checks**:
  - Exit codes: non-zero on error, 0 on success. Are exit codes documented?
  - Output: stdout for data, stderr for diagnostics. Is `--quiet`/`--verbose` supported?
  - Args: are required args validated? Is `--help` generated? Are there conflicting flags?
  - Signals: SIGINT/SIGTERM handled for clean exit? Temp files cleaned up?
  - Config: is there a config file fallback? Are env vars supported as overrides?
- **Weight adjustment**: error_handling +5%, code_quality +5%, offset from api_design -5%, concurrency -5%
