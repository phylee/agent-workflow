# code-inspector

全面的代码审查 Skill，对代码变更进行多维度的自动化审查，输出强结构化的 inspection 报告。

## 核心理念

**工具检测，LLM 解释。** 不让 AI 替代 linter/SAST/测试工具，而是让工具做确定性检测，AI 负责分类、合并、解释、风险判断。每条 finding 都包含 `confidence`（置信度）和 `deterministic`（是否来自工具）标记，消费方可以据此决定是自动拦截还是人工复核。

## 安装

```bash
# 克隆仓库
git clone https://github.com/phylee/agent-workflow.git

# 安装 skill
cp -r agent-workflow/code-inspector ~/.claude/skills/code-inspector
```

安装后重启 Claude Code 会话即可使用。

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
├── summary                 # risk_score, quality_score, security_score, ...
├── tool_runs[]             # 工具运行记录（tool, status, deterministic, summary）
├── limitations[]           # 上下文缺失、工具不可用等限制说明
├── review_delta            # re-review 模式下的增量对比（resolved/new/unchanged）
├── inspections[]           # 所有 finding 的扁平列表
│   ├── id                  # 唯一标识（SEC-001, PERF-003）
│   ├── category            # 维度
│   ├── severity            # critical / high / medium / low
│   ├── confidence          # 0.0-1.0（0.95+ = 工具精确匹配）
│   ├── deterministic       # true = 工具输出，false = LLM 推断
│   ├── source              # semgrep / eslint / llm-inference / ...
│   ├── location            # { file, start_line, end_line }
│   ├── evidence_chain[]    # input → dataflow → sink → impact
│   └── metadata            # { auto_fixable, fix_command, suggested_patch, ... }
├── top_findings[]          # 最重要的 1-5 条 finding 摘要
├── coverage                # test_existence, test_quality, unit_test, api_test, e2e, performance_test
├── gates                   # merge_blocked, verdict, reasons[], warnings[]
├── overall_score           # 0-100，gate 拦截时封顶 40
└── recommendations[]       # immediate / short-term / long-term
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
