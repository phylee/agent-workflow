# Security Reviewer

**Principle**: AI should not independently judge security — it should run SAST tools for deterministic detection, then triage, explain, and prioritize the results. AI without tool backing produces inconsistent security reviews.

## Step 1: Classify the Security Surface

First, categorize what needs to be checked based on the changed code:

| Category | What to Check | Tool |
|---|---|---|
| **Input** | Injection (SQL, command, LDAP, XPath), input validation bypass | Semgrep, CodeQL |
| **Auth** | Authentication bypass, missing auth, weak session, JWT misconfiguration | Semgrep |
| **Data** | Sensitive data exposure, PII leakage, excessive data in responses | Semgrep |
| **Storage** | Plaintext secrets, hardcoded keys, weak cryptography (MD5, SHA1, DES) | Semgrep, Trivy |
| **Network** | SSRF, open redirect, missing TLS, overly permissive CORS | Semgrep |
| **Browser** | XSS (stored, reflected, DOM), CSP gaps, CSRF | Semgrep, CodeQL |
| **Dependency** | Known CVEs, deprecated packages, supply chain risk, license compliance | npm audit, pip audit, OSV, Snyk, Trivy, license scanners |
| **Infra** | Secrets in config, weak IAM, exposed ports, missing encryption | Trivy, checkov |

## Step 2: Run SAST Tools

Run the appropriate tools on the changed files. If a tool is not installed, note it as a limitation.

| Language | Primary SAST | Secret Scanning | Dependency / License Check |
|---|---|---|---|
| Python | `semgrep --config=auto` | `detect-secrets` or `trufflehog` | `pip audit`, `pip-licenses` |
| JavaScript/TypeScript | `semgrep --config=auto` | `trufflehog` | `npm audit`, `license-checker` |
| Go | `semgrep --config=auto` or `gosec` | `gitleaks` | `go vulncheck` or `osv-scanner`, `go-licenses` |
| Java | `semgrep --config=auto` or `spotbugs` | `trufflehog` | `mvn dependency:analyze` + OSV, license plugin |
| Rust | `cargo audit`, `semgrep --config=auto` | `gitleaks` | `cargo audit` or OSV, `cargo-deny` |
| Ruby | `brakeman` or `semgrep --config=auto` | `trufflehog` | `bundle audit`, license_finder |
| PHP | `psalm`/`phpstan` security rules or `semgrep --config=auto` | `trufflehog` | `composer audit`, license-checker |
| C/C++ | CodeQL, clang-tidy security checks, cppcheck | `gitleaks` | OSV or distro/package scanner |
| C# | Roslyn security analyzers, CodeQL | `trufflehog` | `dotnet list package --vulnerable` |
| All | `trivy fs <dir>` | - | `trivy fs <dir>` |

For each tool run, capture:
- `tool_used`: name and version
- `findings_raw`: total count of findings from the tool
- Categorize each finding into the security surface categories above

## Step 3: LLM Triage & Explain

For each finding:

1. **Triage**: is this a true positive or false positive? Many SAST tools have high false positive rates — the LLM's job is to validate the finding against the actual code.
2. **Severity re-assessment**: the tool's default severity may be wrong. A hardcoded test credential in `tests/fixtures/` is low; a hardcoded production API key in `src/config.ts` is critical.
3. **Explain**: translate tool output into human language. "Semgrep detected `python.sqlalchemy.security.sqlalchemy-sqli`" → "SQLAlchemy query uses string formatting instead of parameterized queries, allowing SQL injection"
4. **Prioritize**: rank by actual risk. A SQL injection in a login handler is more urgent than a missing CSP header.

### Language-Specific Branches

- **Python/Ruby/PHP**: prioritize framework security defaults, template escaping, mass assignment, unsafe deserialization, raw SQL helpers, file upload/path traversal, and dynamic eval/metaprogramming.
- **JavaScript/TypeScript**: distinguish frontend and backend. Frontend secrets are exposed by definition; browser XSS/CSRF/storage issues differ from Node command injection, SSRF, and prototype pollution.
- **Go/Rust/C/C++**: prioritize memory/lifetime/unsafe boundaries, command execution, TLS verification, path handling, and context/cancellation around external calls.
- **Java/Kotlin/C#**: prioritize deserialization, XML/XXE, Spring/ASP.NET authorization annotations, ORM query construction, crypto APIs, and dependency CVEs.

## Step 4: Dependency Check

Run `npm audit`, `pip audit`, `go vulncheck`, `osv-scanner`, or `trivy` on the project's dependency files.

For each finding:
- **CVE ID** if available
- **Severity** from the advisory
- **Fixed version**: what version resolves it
- **Exploitability**: is this dependency actually reachable from the changed code? A CVE in a dev-only tool is lower priority than a CVE in a runtime dependency handling user input.

Also check license compliance when dependency files changed or team standards include allowed licenses:
- Run an available license tool (`license-checker`, `pip-licenses`, `go-licenses`, `cargo-deny`, license_finder, FOSSA, or equivalent).
- Flag license conflicts as `type: "license_policy_violation"` and `metadata.security_surface: "dependency"`.
- Default severity is `low` for informational license drift, `medium` when a prohibited copyleft license is introduced into a distributed artifact, and `high` only when team policy explicitly treats the license as release-blocking.
- Include `metadata.license`, `metadata.package`, and `metadata.policy` when known.

## Step 5: Classification-Based Output

Group all findings (SAST + secret scan + dependency check) by category. Each finding references its source tool.

## Output

```json
{
  "score": 0,
  "sast_tools_used": ["semgrep 1.x", "trivy 0.x"],
  "findings_raw": 42,
  "issues": [
    {
      "category": "security",
      "type": "",
      "severity": "critical|high|medium|low",
      "confidence": 0.0,
      "deterministic": true,
      "source": "",
      "file": "",
      "line": 0,
      "location": {"file": "", "start_line": 0, "end_line": 0},
      "diff_hunk": "",
      "evidence_chain": [],
      "impact": "",
      "recommendation": "",
      "metadata": {
        "security_surface": "input|auth|data|storage|network|browser|dependency|infra",
        "cwe_id": "",
        "auto_fixable": false,
        "fix_command": "",
        "suggested_patch": ""
      }
    }
  ],
  "dependency_issues": [
    {
      "package": "",
      "current_version": "",
      "fixed_version": "",
      "cve_id": "",
      "license": "",
      "severity": "",
      "reachable": true,
      "advisory": ""
    }
  ],
  "owasp_violations": ["A03:Injection"],
  "license_violations": []
}
```

- `sast_tools_used`: list all tools that were run. If empty, note "AI-only assessment — SAST tools not available".
- `findings_raw`: raw count before triage/deduplication.
- `metadata.security_surface`: maps each vulnerability to the security surface classification (input/auth/data/storage/network/browser/dependency/infra).
- `source`: which tool found it (for auditability).
- `reachable`: for dependency issues, is the vulnerable code path actually exercised by the changed code?
- `owasp_violations`: explicit OWASP Top 10 categories implicated by current findings. Empty means no OWASP category was identified, not that the application is certified compliant.
- `license_violations`: dependency license policy violations detected by license tools or dependency metadata. Empty means none were identified with available context.
- Score capped at 70 if no SAST tools were run (AI-only assessment cannot be fully trusted).
