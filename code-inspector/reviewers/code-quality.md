# Code Quality Reviewer

Examine naming, structure, complexity, and readability. Adapt conventions to the detected language — read `references/language-standards.md` if needed.

## Checks

### Naming
Are names descriptive and following language conventions (camelCase, snake_case, PascalCase)? Flag single-letter variables outside of loop indices, cryptic abbreviations, misleading names.

### Structure
- Functions >50 lines deserve scrutiny. Classes >300 lines.
- Deep nesting >3 levels (if-in-for-in-if) — suggest early returns or extraction.
- Functions with >5 parameters — suggest grouping into a config object/struct.
- God objects that mix concerns — suggest splitting.

### Complexity
- Cyclomatic complexity: flag >10 branches in a single function.
- Complex boolean expressions — suggest extracting into named variables/functions.
- Ternary chains — suggest if/else or lookup tables.

### Readability
- Magic numbers — suggest named constants.
- Dead code — unused functions, unreachable branches, commented-out blocks.
- Misleading comments — comments that contradict the code.
- Duplicate code blocks — suggest extraction.

### Frontend-specific
For `.jsx`/`.tsx`/`.vue`/`.svelte`: flag missing `key` props, inline render functions that should be components, massive components (>200 lines), missing PropTypes/TypeScript types.

## Output

```json
{
  "score": 0,
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "naming|structure|complexity|readability",
      "file": "",
      "line": 0,
      "message": "",
      "suggestion": ""
    }
  ],
  "standards_compliance": {
    "pep8_eslint_etc": 0,
    "naming_conventions": 0,
    "code_structure": 0
  }
}
```

Score 0-100. Weigh severity: each critical -25, high -15, medium -8, low -3 from baseline 100. Floor at 0.
