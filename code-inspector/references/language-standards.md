# Language-Specific Standards Reference

Use this reference to apply correct language conventions during code review.

---

## Python

**Primary standard**: PEP 8
**Supplementary**: Google Python Style Guide

### Naming
- `snake_case` for functions, variables, methods, modules
- `PascalCase` for classes, exceptions
- `UPPER_SNAKE_CASE` for constants
- `_leading_underscore` for internal/private members
- `__double_leading_underscore` for name mangling
- `__dunder__` only for Python-defined special methods

### Structure
- Max line length: 79 (PEP 8) or 100 (pragmatic)
- 4-space indentation, no tabs
- Blank line between top-level definitions
- 2 blank lines between classes and top-level functions
- Imports at top of file: stdlib → third-party → local
- Type hints recommended (PEP 484)

### Anti-patterns to flag
- Bare `except:` clauses
- Mutable default arguments
- `from module import *`
- List/dict comprehension with side effects
- Using `== True` / `== False` instead of truthiness
- `is` used for value comparison (only use `is` for `None`, `True`, `False`)
- f-strings with side-effect expressions

### Performance concerns
- `+` in loops for string building (use `"".join()`)
- `list` for membership testing (use `set`/`dict`)
- `range(len(...))` patterns
- Unnecessary object creation in hot loops
- Missing `__slots__` for classes with many instances
- Synchronous I/O in async functions

### Security concerns
- `os.system()` / `subprocess.call(shell=True)` with user input
- `eval()`, `exec()` with untrusted input
- `pickle.load()` on untrusted data
- SQL via string formatting (use parameterized queries)
- `DEBUG = True` and `SECRET_KEY` hardcoded in Django settings
- Passwords/secrets in logging output

---

## JavaScript / TypeScript

**Primary standard**: Airbnb Style Guide
**Tooling**: ESLint (recommended config)

### Naming
- `camelCase` for variables, functions, methods
- `PascalCase` for classes, React components, TypeScript interfaces/types
- `UPPER_SNAKE_CASE` for true constants (not just `const` declarations)
- No leading/trailing underscores
- Boolean variables prefixed with `is`, `has`, `should`

### Structure
- 2-space indentation
- Semicolons: be consistent (prefer always)
- Single quotes for strings (unless escaping needed)
- `const` by default, `let` only when reassignment needed, never `var`
- Arrow functions for callbacks, regular functions for methods
- Destructuring preferred over dot access for repeated property access
- Spread operator over `Object.assign`

### TypeScript-specific
- Prefer `interface` over `type` for object shapes
- Avoid `any` — use `unknown` if type is truly unknown
- Use `as` casts sparingly (they bypass type checking)
- Enable `strict` mode in tsconfig
- Use optional chaining (`?.`) and nullish coalescing (`??`)

### Anti-patterns to flag
- `console.log` left in production code
- `==` instead of `===`
- Callback hell (use async/await or Promise chains)
- Mutation of function parameters
- `eval()`, `new Function()`, `innerHTML` assignment
- Missing `key` prop in React lists
- Side effects in `useEffect` without proper dependencies
- Large bundle imports: `import * as _ from 'lodash'`

### Performance concerns
- Unnecessary re-renders in React
- Missing `useMemo`/`useCallback` for expensive computations
- Large synchronous loops blocking the event loop
- Memory leaks from unremoved event listeners or intervals
- Unoptimized images/assets

### Security concerns
- `dangerouslySetInnerHTML` in React
- `innerHTML` / `outerHTML` with user input
- `document.write()`
- `eval()` / `new Function()` with dynamic input
- Client-side storage of JWTs/tokens
- Exposed API keys in client-side code
- Missing CSP headers
- Prototype pollution via `Object.assign` or spread on user input

---

## Java

**Primary standard**: Google Java Style Guide
**Supplementary**: Oracle Code Conventions, Effective Java (Bloch)

### Naming
- `camelCase` for methods, variables, parameters
- `PascalCase` for classes, interfaces, enums
- `UPPER_SNAKE_CASE` for `static final` constants
- Package names all lowercase, reverse domain
- Interface names: no `I` prefix; use `-able` or `-ible` suffix where natural

### Structure
- 2 or 4-space indentation (consistent within file)
- Max line length: 100 (Google) or 120 (common)
- One class per file (except inner classes)
- Members order: static fields → instance fields → constructors → methods
- Braces: opening brace on same line (K&R style)

### Anti-patterns to flag
- `catch (Exception e)` without specific handling
- Returning `null` instead of `Optional<T>`
- Raw types (use generics)
- `new Thread()` instead of ExecutorService
- `System.out.println` for logging (use SLF4J/Log4j)
- `String` concatenation in loops (use `StringBuilder`)
- `==` for String comparison
- Resource leaks: unclosed streams, connections (use try-with-resources)

### Performance concerns
- `+` in loops for String building
- Eager initialization of expensive resources
- Unnecessary boxing/unboxing
- Large object graphs held in static fields
- Missing connection pooling for database access
- Unindexed JPA/Hibernate queries

### Security concerns
- SQL/JPQL concatenation (use `PreparedStatement` / parameterized queries)
- XXE in XML parsers
- Insecure deserialization (`ObjectInputStream` on untrusted data)
- Hardcoded credentials in properties files
- Path traversal in file operations
- Weak cryptography (MD5, SHA-1, DES)
- Missing access modifiers on sensitive methods

---

## Go

**Primary standard**: Effective Go
**Supplementary**: Go Code Review Comments

### Naming
- `MixedCaps` or `mixedCaps` (not underscores)
- Exported names start with capital letter
- Unexported names start with lowercase
- Short, concise names; longer for greater scope distance
- Interface names: single method interfaces end in `-er` (Reader, Writer, Closer)
- Avoid `Get` prefix for getters; use direct field-like names
- Package names: lowercase, single word, no underscores

### Structure
- `gofmt` / `goimports` formatting is canonical — no debate
- Tabs for indentation (go fmt standard)
- Group imports: stdlib → external → internal, each group separated by blank line
- Early returns: handle errors first, then proceed with happy path
- Avoid `else` when `if` block ends with `return` (keep the happy path at low indentation)

### Anti-patterns to flag
- Ignoring errors: `_ = doSomething()` or `val, _ := doSomething()`
- `panic` in library code (return errors instead)
- Naked `return` in long functions (confusing)
- Passing around `interface{}` when generics or specific types work
- Goroutine leaks — starting a goroutine without a way to stop it
- Mutex copies (pass by pointer)
- `defer` in loops (resource accumulation)

### Performance concerns
- Unbounded goroutine creation
- Channel misuse (unbuffered where buffered needed, or vice versa)
- Large allocations in hot loops (use `sync.Pool`)
- `string` to `[]byte` conversion in tight loops
- Missing buffer/connection pooling
- Reflection in performance-critical paths

### Security concerns
- `os/exec.Command` with unsanitized input
- `template.HTML()` with user-controlled content
- Hardcoded secrets in source
- Missing TLS verification (`InsecureSkipVerify: true`)
- Path traversal in file serving (`http.Dir`)
- SQL injection via `fmt.Sprintf` for query building

---

## Other Languages (General Guidance)

When reviewing languages not listed above, apply these universal principles:

1. **Be consistent**: Whatever conventions the codebase uses, apply them uniformly
2. **Follow the ecosystem**: Prefer the dominant style guide for that language
3. **Read existing code first**: Before flagging "issues", check if the code follows project conventions
4. **Flag only clear problems**: When you're less sure about language-specific norms, focus on universal issues:
   - Dead code and unreachable paths
   - Obviously wrong logic
   - Security vulnerabilities (SQL injection, XSS, command injection are language-agnostic)
   - Performance anti-patterns (N+1 queries, memory leaks)
   - Missing error handling
