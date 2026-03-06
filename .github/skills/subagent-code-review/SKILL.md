---
name: subagent-code-review
description: Sets up multi-perspective parallel code review using subagents in GitHub Copilot for VS Code. Use this skill when the user wants to review code from multiple angles simultaneously, run security + performance + quality reviews in parallel, get independent unbiased perspectives on code, or create specialized review agents. Trigger for requests like "revisión de código con subagentes", "multi-perspective code review", "review code in parallel", "run security and quality review simultaneously", "thorough code review with agents", "parallel code analysis", "review desde múltiples perspectivas", "revisor de código especializado", or any request to perform comprehensive code review using subagents. Use this skill even when the user just wants a thorough review and hasn't explicitly mentioned subagents — parallel review is almost always better than a single pass.
---

# Multi-Perspective Parallel Code Review

This skill sets up parallel subagent-based code reviews. Each perspective runs independently — without being anchored by what other reviewers found — producing more objective and comprehensive results than a single sequential review.

## Why parallel review works better

A single reviewer anchors on the first issue found and may miss others. Parallel subagents each approach the code fresh, from a specialized lens, and their findings are then synthesized into a prioritized report.

Benefits:
- **Independent findings**: no cognitive anchoring between perspectives
- **Speed**: all perspectives run simultaneously  
- **Specialization**: each agent uses tools and focus appropriate to its job  
- **Cleaner context**: only summaries return to the orchestrator

---

## Lightweight Pattern (No Separate Agent Files)

For quick setup, define all behavior in a single coordinator agent. The orchestrator shapes each subagent's focus through the task prompt — no additional files required:

```markdown
---
name: Thorough Reviewer
tools: ['agent', 'read', 'search']
---
You review code through multiple independent perspectives. Run each as a parallel 
subagent so findings are unbiased.

When asked to review code, start these subagents simultaneously:
- **Correctness**: logic errors, edge cases, off-by-one errors, null handling, type issues
- **Code quality**: readability, naming, duplication, dead code, complexity
- **Security**: OWASP Top 10 — input validation, injection risks, data exposure, auth issues
- **Architecture**: codebase patterns, design consistency, coupling, structural alignment

After all complete, synthesize findings into a prioritized summary:
1. Critical issues (must fix before shipping)
2. Recommended improvements (should fix soon)
3. Nice-to-have (low priority refactors)
4. What the code does well

Always acknowledge strengths alongside issues.
```

---

## Full Pattern (Specialized Agent Files)

For maximum control, create a separate agent file per perspective. This lets each reviewer have its own tools, model, and detailed instructions.

### File Structure

```
.github/copilot-agents/
├── thorough-reviewer.agent.md       # Coordinator
├── correctness-reviewer.agent.md    # Worker: logic & correctness
├── quality-reviewer.agent.md        # Worker: readability & style
├── security-reviewer.agent.md       # Worker: OWASP security
└── architecture-reviewer.agent.md   # Worker: design & structure
```

### `thorough-reviewer.agent.md` — Coordinator

```markdown
---
name: Thorough Reviewer
tools: ['agent', 'read', 'search']
agents: ['Correctness Reviewer', 'Quality Reviewer', 'Security Reviewer', 'Architecture Reviewer']
---
You perform comprehensive code reviews using four independent specialized reviewers.

When asked to review code, run all four reviewer agents simultaneously (in parallel):
- Correctness Reviewer
- Quality Reviewer
- Security Reviewer
- Architecture Reviewer

After all complete, synthesize their findings into a single prioritized report:
- Critical issues (blocking)
- Recommended improvements
- Nice-to-have refactors
- What the code does well

Do not repeat the same finding from multiple reviewers — consolidate duplicates.
```

### `correctness-reviewer.agent.md`

```markdown
---
name: Correctness Reviewer
user-invocable: false
tools: ['read', 'search']
---
Review code for logical correctness. Focus on:
- Logic errors and incorrect algorithms
- Edge cases and boundary conditions
- Null/undefined handling and type mismatches
- Off-by-one errors and incorrect loop conditions
- Race conditions and concurrency issues
- Incorrect error handling or swallowed exceptions

Return a list of issues with file, line reference, description, and severity (Critical/High/Medium).
Do not modify any files.
```

### `quality-reviewer.agent.md`

```markdown
---
name: Quality Reviewer
user-invocable: false
tools: ['read', 'search']
---
Review code for quality and maintainability. Focus on:
- Readability and clarity of intent
- Naming conventions (variables, functions, classes)
- Code duplication and DRY violations
- Unnecessary complexity and over-engineering
- Dead code and unused imports
- Adherence to existing codebase conventions

Return a list of issues with file, line reference, description, and priority (High/Medium/Low).
Do not modify any files.
```

### `security-reviewer.agent.md`

```markdown
---
name: Security Reviewer
user-invocable: false
tools: ['read', 'search']
---
Review code for security vulnerabilities, focusing on OWASP Top 10:
- Injection (SQL, XSS, command injection, LDAP injection)
- Broken access control and missing authorization checks
- Cryptographic failures (weak algorithms, hardcoded secrets, insecure storage)
- Insecure design and missing security controls
- Sensitive data exposure in logs, responses, or error messages
- Server-side request forgery (SSRF)
- Insecure deserialization

Return each finding with severity (Critical/High/Medium/Low), CWE reference if applicable, and a concrete remediation suggestion.
Do not modify any files.
```

### `architecture-reviewer.agent.md`

```markdown
---
name: Architecture Reviewer
user-invocable: false
tools: ['read', 'search']
---
Review code for architectural alignment and design quality. Focus on:
- Consistency with existing codebase patterns and conventions
- Separation of concerns and single responsibility
- Inappropriate coupling between modules or layers
- Missing abstractions or premature abstractions
- Whether the approach fits the project's design philosophy

Return findings with file/module references, description, and impact level (High/Medium/Low).
Do not modify any files.
```

---

## Extending with Specialized Tools

Reviewers can use specialized tools for their domain. For example:

```markdown
---
name: Security Reviewer
user-invocable: false
tools: ['read', 'search', 'run']  # run: execute security scanners
---
... same body as above, but also run: `bandit` (Python), `semgrep`, or `npm audit`
to complement the manual review.
```

---

## Invoking the Review

Once the coordinator agent is created, invoke it naturally:

- `@Thorough Reviewer review the changes in src/auth/`
- `@Thorough Reviewer check this pull request for issues`
- `Run a thorough code review on the payment module`

The coordinator will start all four review perspectives in parallel and synthesize the results.

---

## Design Tips

- **Keep reviewers read-only**: never give `edit` or `create` tools to reviewers — findings should be recommendations, not automatic changes
- **Consolidate in the coordinator**: instruct the coordinator to deduplicate overlapping findings from different reviewers
- **Acknowledge strengths**: a good review notes what works well, not just what's broken  
- **Scope per invocation**: pass a specific file, directory, or diff — not the entire codebase — to keep subagent context focused
