# Security Reviewer

Apply OWASP Top 10 awareness and language-specific vulnerability patterns.

## Checks

### Injection (A03)
- **SQL injection**: String concatenation/interpolation building queries — `f"SELECT ... WHERE id = {user_id}"`. Parameterized queries required.
- **Command injection**: `os.system()`, `exec.Command()`, `subprocess.call(shell=True)` with user input.
- **LDAP/XPath/XXE**: Flag dynamic LDAP filters, XPath injection, XML parsing without `resolve_entity=False`.

### XSS (A03)
- `dangerouslySetInnerHTML`, `innerHTML`, `outerHTML`, `document.write()` with user data.
- Missing output encoding in server-rendered templates.
- `eval()`, `new Function()` with dynamic input.

### CSRF (A01)
- State-changing requests (POST, PUT, DELETE, PATCH) without CSRF tokens or SameSite cookies.
- Cookie-based auth without `SameSite=Strict` or `SameSite=Lax`.

### Authentication & Authorization (A01, A07)
- Hardcoded credentials, API keys, tokens in source code.
- Weak password policies (no minimum length, no complexity).
- Missing rate limiting on login/2FA/password-reset endpoints.
- Overly permissive CORS (`Access-Control-Allow-Origin: *` with credentials).
- Path traversal: file paths built from user input without sanitization.
- Missing authorization checks — can user A access user B's data (IDOR)?

### Sensitive Data (A02, A04)
- Secrets in code, config files, or environment dumps.
- Logging PII, tokens, passwords — flag at any log level.
- Missing encryption at rest for sensitive fields.
- Hardcoded encryption keys or IVs.

### Dependencies (A06)
- Check dependency files (`package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `Cargo.toml`).
- Flag packages with known critical CVEs (use your knowledge cutoff — note that the user should verify with `npm audit`/`pip audit`/`go vulncheck`).
- Deprecated/abandoned packages — suggest alternatives.

### Transport Security
- HTTP (not HTTPS) endpoints for sensitive operations.
- `InsecureSkipVerify: true` in TLS config.
- `sslmode=disable` in database connection strings.

## Output

```json
{
  "score": 0,
  "vulnerabilities": [
    {
      "type": "",
      "severity": "critical|high|medium|low",
      "cwe_id": "",
      "location": "",
      "description": "",
      "remediation": ""
    }
  ],
  "dependency_issues": [],
  "compliance": {
    "owasp_top10": true,
    "data_privacy": true
  }
}
```

For each vulnerability, include the CWE ID. Set `owasp_top10: false` if any OWASP Top 10 category is violated. Set `data_privacy: false` if PII handling or logging issues are found.
