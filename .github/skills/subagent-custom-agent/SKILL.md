---
name: subagent-custom-agent
description: Creates custom agent files (.agent.md) for use as subagents in GitHub Copilot for VS Code. Use this skill when the user wants to define a specialized agent, build a worker agent, configure a subagent with specific tools/models/instructions, or control how agents can be invoked. Trigger for requests like "crea un agente personalizado", "create a subagent for X", "make a worker agent", "define a specialized agent", "I need an agent that only does Y", "configure agent invocation", "create a reusable agent component", "agente subagente", or any request to build a custom AI agent component for delegation. Use this skill even when the user just mentions creating agents with restricted tools or specific roles.
---

# Custom Agent Creator for Subagents

Custom agents are `.agent.md` files that define specialized behavior for use as subagents in GitHub Copilot. Each agent runs in its own context window with specific tools, model, and instructions.

## File Location

Custom agents live in `.github/copilot-agents/` as `.agent.md` files:

```
.github/copilot-agents/
├── planner.agent.md
├── implementer.agent.md
├── security-reviewer.agent.md
└── research-analyst.agent.md
```

## Frontmatter Reference

```yaml
---
name: Agent Name                      # Required: display name in Copilot UI
description: What this agent does     # Recommended: helps AI select the right agent
tools: ['read', 'search', 'edit']     # Tools available to this agent
model: gpt-4o                         # Optional: override the default model
user-invocable: true                  # Default true; set false for subagent-only agents
disable-model-invocation: false       # Default false; set true to prevent AI from using this as subagent
agents: ['Agent1', 'Agent2']          # Restrict which subagents this agent can invoke (* = all, [] = none)
---
```

### Available Tools

| Tool | Purpose |
|------|---------|
| `read` | Read files from the workspace |
| `search` | Search in the codebase |
| `edit` | Modify existing files |
| `create` | Create new files |
| `delete` | Delete files |
| `run` | Execute terminal commands |
| `agent` | Spawn subagents from this agent |
| `fetch` | Fetch external URLs |

**Principle of least privilege**: assign only the tools required for the agent's job. Read-only roles (planners, reviewers, researchers) should never have `edit`, `create`, or `run`.

### Invocation Control

| Property | Value | Effect |
|----------|-------|--------|
| `user-invocable` | `false` | Hidden from the chat dropdown; only usable as a subagent |
| `disable-model-invocation` | `true` | Only the user can start this agent, never an AI orchestrator |
| `agents` | `['A', 'B']` | Restricts which subagents this agent can invoke |
| `agents` | `*` | Allows all available subagents (default) |
| `agents` | `[]` | Prevents this agent from invoking any subagent |

> Note: explicitly listing an agent in the coordinator's `agents` array overrides `disable-model-invocation: true` on that worker agent.

## Writing the Agent Body

The markdown body is the system prompt. Structure it as:

1. **Role statement** — what the agent is and what it does
2. **Scope definition** — what it should and shouldn't handle  
3. **Output format** — what it returns to the main agent (keep it concise)
4. **Constraints** — any safety, scope, or performance limits

The body should be concise. Subagents receive only the task prompt — they don't inherit main agent context or instructions.

---

## Ready-to-Use Templates

### Read-Only Research Agent

```markdown
---
name: Research Analyst
user-invocable: false
tools: ['read', 'search']
---
You are a research analyst. Given a topic or question, search the codebase and 
documentation for relevant context. Return a concise, structured summary of your 
findings — focus only on what is directly relevant. Do not modify any files.
```

### Code Implementer

```markdown
---
name: Implementer
user-invocable: false
tools: ['read', 'search', 'edit', 'create']
---
You are a code implementer. You receive a specific task with clear requirements. 
Write clean, idiomatic code that follows the patterns in the existing codebase. 
Confirm what you implemented and any decisions made.
```

### Security Reviewer

```markdown
---
name: Security Reviewer
user-invocable: false
tools: ['read', 'search']
---
You are a security-focused code reviewer specializing in OWASP Top 10 vulnerabilities.
Review the provided code for: injection risks (SQL, XSS, command injection), broken 
access control, cryptographic failures, insecure deserialization, and sensitive data 
exposure. Return a prioritized list of issues with severity (Critical/High/Medium/Low) 
and a suggested fix for each.
```

### Planner (Read-Only)

```markdown
---
name: Planner
user-invocable: false
tools: ['read', 'search']
---
Break down complex feature requests into clear, ordered implementation tasks. 
Each task must be self-contained and assignable to a single implementer. 
Incorporate any architectural feedback before finalizing the plan.
```

---

## Design Principles

- **Narrow scope = better results**: agents with a single, clear responsibility outperform generalist ones
- **Stateless by design**: each invocation gets a clean context; don't rely on state from previous subagent calls
- **Concise output matters**: instruct agents to return summaries, not full transcripts, to keep the main agent's context lean
- **Match tools to role**: mismatched tools (e.g., `edit` on a reviewer) introduce risk and noise
