# code-inspector

全面的代码审查 Skill，对代码变更进行多维度的自动化审查，输出强结构化的 inspection 报告。

## 核心理念

**工具检测，LLM 解释。** 不让 AI 替代 linter/SAST/测试工具，而是让工具做确定性检测，AI 负责分类、合并、解释、风险判断。每条 finding 都包含 `confidence`（置信度）和 `deterministic`（是否来自工具）标记，消费方可以据此决定是自动拦截还是人工复核。

## 审查维度（9 个）

| 维度 | 触发方式 | 核心工具 |
|------|---------|---------|
| Code Quality | 始终运行 | Ruff / ESLint / golangci-lint |
| Test Coverage | 始终运行 | mutmut / Stryker（mutation testing） |
| Performance | 始终运行 | LLM evidence-based 检测 |
| Error Handling | 始终运行 | LLM 检测 |
| Logging | 始终运行 | LLM 检测 |
| Security | 始终运行 | Semgrep / CodeQL / Trivy / npm audit |
| Database | 有 SQL/迁移/ORM 变更时 | LLM 检测 |
| Concurrency | 有多线程/异步代码时 | LLM 检测 |
| API Design | 有接口/协议变更时 | OpenAPI diff / buf breaking |

## 使用方式

### 在 Claude Code 中调用

Skill 会通过关键词自动触发，也可以直接使用：

```
/code-inspector
```

也可直接自然语言触发，Skill 会自动匹配关键词：

```
帮我 review 一下这段代码
审查 src/api/ 目录
Review this PR: https://github.com/org/repo/pull/123
检查这次 commit 有没有安全问题
```

### 结构化输入（推荐）

```json
{
  "language": "typescript",
  "framework": "nestjs",
  "change_type": "feature",
  "service_type": "api",
  "git_diff": "...",
  "changed_files": ["src/auth/login.ts"],
  "dependency_changes": [],
  "test_files": ["src/auth/login.test.ts"],
  "api_contract_changes": [],
  "risk_level": "medium"
}
```

### PR 链接

```
Review this PR: https://github.com/org/repo/pull/123
```

Skill 会自动通过 `gh pr view` 和 `gh pr diff` 提取代码变更。

### 原始 Git Diff

直接粘贴 `git diff` 输出，或提供文件/目录路径。

### 可选参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `language` | string | 编程语言，默认 `auto` 自动检测 |
| `service_type` | string | 服务类型，覆盖自动检测：`api` / `frontend` / `worker` / `database` / `infra` / `library` / `cli` |
| `focus_areas` | string[] | 重点领域，2x 权重：`code_quality` / `test_coverage` / `performance` / `database` / `error_handling` / `concurrency` / `api_design` / `logging` / `security` |
| `strictness` | string | 严格度：`lenient` / `normal` / `strict` |

## 输出格式

强结构化 JSON，根键 `code_inspector_result`：

```
code_inspector_result
├── summary              # risk_score, quality_score, security_score, ...
├── inspections[]        # 所有 finding 的扁平列表
│   ├── category         # 维度
│   ├── severity         # critical / high / medium / low
│   ├── confidence       # 0.0-1.0（0.95+ = 工具精确匹配）
│   ├── deterministic    # true = 工具输出，false = LLM 推断
│   ├── source           # semgrep / eslint / llm-inference / ...
│   └── evidence_chain[] # input → dataflow → sink → impact
├── coverage             # assertion_density, mutation_score, journey coverage
├── gates                # merge_blocked + reasons + warnings
├── overall_score
└── recommendations[]
```

每条 finding 都包含可审计的 `evidence_chain`，从输入追踪到影响：

```json
{
  "type": "sql_injection",
  "severity": "critical",
  "confidence": 0.95,
  "deterministic": true,
  "source": "semgrep",
  "evidence_chain": [
    "user input from query param 'search'",
    "passed to fmt.Sprintf without sanitization",
    "executed as raw SQL via db.Query()",
    "allows attacker to read/modify/delete all user data"
  ],
  "recommendation": "Use parameterized query: db.Query('SELECT ... WHERE name LIKE $1', '%'+search+'%')"
}
```

## 文件结构

```
code-inspector/
├── SKILL.md                         # 编排器：分类 → 分发 → 聚合
├── README.md
├── reviewers/                       # 专业 reviewer（按需加载）
│   ├── code-quality.md
│   ├── test-coverage.md
│   ├── performance.md
│   ├── database.md
│   ├── error-handling.md
│   ├── concurrency.md
│   ├── api-design.md
│   ├── logging.md
│   └── security.md
└── references/                      # 参考文档
    ├── output-schema.md             # 输出 JSON schema 定义
    ├── classification-guide.md      # 服务类型分类策略
    └── language-standards.md        # 各语言编码规范
```

## 架构设计

```
输入（结构化 JSON / PR 链接 / git diff）
  ↓
Step 1: 解析输入 → 提取结构化信息
  ↓
Step 2: 收集上下文 → 完整函数体、caller、callee、依赖
  ↓
Step 3: 分类 → 确定 service_type → 激活相关 reviewer
  ↓
Step 4: 分发 → 只加载激活的 reviewer → 运行工具 → LLM 解释
  ↓
Step 5: 聚合 → 映射到 inspections[] → 填充 gates → 计算分数
  ↓
Step 6: 输出 → JSON + gate verdict + 摘要
```

Token 消耗与变更复杂度成正比：简单前端 PR 只加载 6 个 baseline reviewer，复杂后端 PR 才加载全部。
