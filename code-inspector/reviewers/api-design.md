# API / Interface Design Reviewer

**Principle**: Don't guess whether an API change is breaking — diff the contract. Use schema diff tools for deterministic detection, then LLM explains the impact and suggests migration paths.

## Step 1: Detect Contract Type

Identify the API contract format from changed files:

| Signal | Contract Type | Diff Tool |
|---|---|---|
| `openapi.yaml`, `swagger.json`, `schema.yml` | OpenAPI / Swagger | `npx openapi-diff <old> <new>` or `npx swagger-diff` |
| `schema.graphql`, `*.graphql` | GraphQL | Compare SDL: removed fields, changed types, new required args |
| `*.proto` | Protobuf | `buf breaking --against <old>` |
| No schema file, but route handlers changed | Implicit REST | Manual contract inference from handler code |

## Step 2: Detect Breaking Changes

Run the diff tool if available. If no tool, infer from code changes. Check:

### Input Contract
- **New required field** without default → breaking. Existing callers don't send it.
- **Field type changed** (string → integer) → breaking. Clients sending `"123"` now get 400.
- **Enum value removed** → breaking. Clients using that value break.
- **Validation tightened** (max length 100 → 50) → breaking. Existing valid data now rejected.
- **Nullable field made non-nullable** → breaking. Existing null values now fail validation.

### Output Contract
- **Field removed from response** → breaking. Clients relying on that field crash or misbehave.
- **Field type changed** (integer → string) → breaking. Client parsing breaks.
- **Field meaning changed** (price was in cents, now in dollars) → silently breaking. This is the most dangerous — no type error, just wrong behavior.
- **New sensitive field added** (email, phone, PII added to public response) → data leakage risk.

### Transport
- **Auth requirement added** (public → authenticated) → breaking for anonymous clients.
- **Rate limit introduced or tightened** → breaking for high-traffic clients.
- **URL path changed** → breaking. Even `/users/{id}` to `/users/id/{id}` breaks all clients.

### Pagination & Performance
- **Pagination removed or default limit increased** → risk of overwhelming clients.
- **Pagination format changed** (offset-based → cursor-based) → breaking for clients iterating pages.

## Step 3: LLM Assessment

For each breaking change detected:

1. **Severity**: critical (will crash clients) vs. high (clients get errors) vs. medium (degraded experience)
2. **Impact scope**: how many callers are affected? (grep for usage if possible)
3. **Migration path**: can clients migrate gradually? Is there a deprecation window? Suggest:
   - Add the new field/behavior as optional first, deprecate old in next version
   - Dual-write to both old and new formats during transition
   - Version the API (`/v2/`) if the change is fundamental

## Step 4: Input/Output Quality Check

Beyond breaking changes, check API design quality:

- **Input validation**: are all fields validated (type, range, length, format, enum)? Are error messages specific enough for clients to fix their requests?
- **Nullability**: are nullable fields intentional? Is there a distinction between "absent" and "null"?
- **Auth**: is every endpoint behind the appropriate auth level? Are there admin endpoints accidentally public?
- **Rate limiting**: login/signup/password-reset should be rate-limited. Bulk endpoints should have stricter limits.
- **Sensitive field leakage**: do any responses include password hashes, internal IDs, tokens, PII that shouldn't be exposed?
- **Schema consistency**: do all endpoints follow the same error envelope, pagination format, date format, field naming?

## Output

```json
{
  "applicable": true,
  "score": 0,
  "contract_type": "openapi|graphql|protobuf|implicit",
  "contract_diff": {
    "tool_used": "",
    "breaking_changes": 0,
    "warnings": 0
  },
  "issues": [
    {
      "category": "api_design",
      "severity": "critical|high|medium|low",
      "confidence": 0.0,
      "deterministic": true,
      "source": "",
      "file": "",
      "line": 0,
      "type": "breaking_change|inconsistent_signature|missing_idempotency|poor_naming|bool_parameter_smell|too_many_params|sensitive_field_leak|missing_validation|missing_pagination|missing_rate_limit",
      "evidence_chain": [],
      "impact": "",
      "recommendation": "",
      "metadata": {
        "contract_type": "openapi|graphql|protobuf|implicit",
        "migration_path": ""
      }
    }
  ]
}
```

`migration_path`: if the change is breaking, provide a concrete deprecation/migration strategy.
