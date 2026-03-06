---
name: subagent-orchestrator
description: Sets up the coordinator-worker subagent orchestration pattern in GitHub Copilot for VS Code. Use this skill when the user wants to build a multi-agent workflow, create a main agent that delegates to specialized worker agents, implement a pipeline of agents that pass results between them, or control which agents a coordinator can invoke. Trigger for requests like "crear un coordinador de agentes", "orchestrate multiple agents", "set up a workflow with subagents", "main agent that delegates tasks", "pipeline of specialized agents", "feature builder with subagents", "agente coordinador", "coordinator and worker pattern", or any request to coordinate multiple agents working together. Use this skill even when the user describes a complex multi-step workflow that would clearly benefit from agent delegation.
---

# Coordinator-Worker Subagent Orchestration

This skill implements the coordinator-worker pattern: a main agent manages the overall workflow and delegates focused subtasks to specialized worker agents. Each worker runs in its own clean context and reports back a summary.

## Why this pattern?

- **Context isolation**: the coordinator's context stays focused on orchestration, not implementation details  
- **Parallel execution**: VS Code can run multiple subagents simultaneously, speeding up multi-part tasks  
- **Specialization**: each worker agent has exactly the tools and model appropriate for its job  
- **Clean results**: only the final summary returns to the coordinator — not all intermediate steps

## How the Coordinator Works in Practice

```
User → Coordinator agent
           ├── Planner subagent (read, search) → plan
           ├── Architect subagent (read, search) → validates plan
           ├── Implementer subagent (read, edit) → writes code
           └── Reviewer subagent (read, search) → finds issues
```

The coordinator waits for each subagent to finish (subagents are synchronous by default, but VS Code can run independent ones in parallel).

---

## Setting Up the Pattern

### Step 1 — Identify the workflow phases

Break the overall task into distinct phases. Each phase that benefits from:
- **Isolated context** (e.g., research that would clutter the main conversation)
- **Specialized tools** (e.g., a phase that needs `run` but others shouldn't)
- **Different model** (e.g., a fast model for simple subtasks)

...is a good subagent candidate.

### Step 2 — Create the worker agents

Worker agents are typically `user-invocable: false` so they don't clutter the chat dropdown. See the `subagent-custom-agent` skill for detailed templates.

```
.github/copilot-agents/
├── planner.agent.md         # Breaks down the task into steps
├── plan-architect.agent.md  # Validates the plan against existing codebase patterns
├── implementer.agent.md     # Writes the code
└── reviewer.agent.md        # Reviews the implementation
```

### Step 3 — Create the coordinator agent

The coordinator uses the `agent` tool to spawn subagents, and optionally restricts which agents it can use via the `agents` frontmatter property.

```markdown
---
name: Feature Builder
tools: ['agent', 'read', 'search', 'edit']
agents: ['Planner', 'Plan Architect', 'Implementer', 'Reviewer']
---
You are a feature development coordinator. For each feature request:

1. Use the Planner agent to break down the feature into tasks.
2. Use the Plan Architect agent to validate the plan against codebase patterns.
   - If the Architect finds reusable patterns or libraries, send that feedback to 
     the Planner to update the plan before proceeding.
3. Use the Implementer agent to write the code for each task.
4. Use the Reviewer agent to check the implementation.
   - If the Reviewer identifies issues, use the Implementer again to apply fixes.

Iterate between Planner/Architect and Reviewer/Implementer until each phase 
converges. Then summarize what was built.
```

---

## Full Example: Feature Builder

### `planner.agent.md`

```markdown
---
name: Planner
user-invocable: false
tools: ['read', 'search']
---
Break down feature requests into clear, ordered implementation tasks. Each task 
must be self-contained and assignable to a single implementer. Incorporate 
feedback from the Plan Architect before finalizing.
```

### `plan-architect.agent.md`

```markdown
---
name: Plan Architect
user-invocable: false
tools: ['read', 'search']
---
Validate plans against the codebase. Identify existing patterns, utilities, and 
libraries that should be reused. Flag any plan steps that duplicate existing 
functionality. Return structured feedback for the Planner.
```

### `implementer.agent.md`

```markdown
---
name: Implementer
user-invocable: false
tools: ['read', 'search', 'edit', 'create']
---
Write code to complete assigned tasks. Follow existing codebase patterns and 
conventions. Confirm what was implemented and any decisions made.
```

### `reviewer.agent.md`

```markdown
---
name: Reviewer
user-invocable: false
tools: ['read', 'search']
---
Review the implementation for correctness, edge cases, adherence to codebase 
patterns, and potential bugs. Return a prioritized list of issues. 
Do not modify files.
```

---

## Parallel Execution

To run subagents in parallel, prompt the coordinator to start multiple tasks at once:

```markdown
---
name: Parallel Analyzer
tools: ['agent', 'read', 'search']
agents: ['Security Reviewer', 'Performance Analyzer', 'Accessibility Checker']
---
When asked to analyze code, run these three agents simultaneously (in parallel):
- Security Reviewer: identify OWASP Top 10 vulnerabilities
- Performance Analyzer: identify bottlenecks and inefficiencies
- Accessibility Checker: verify WCAG compliance

After all three complete, synthesize the findings into a prioritized action list.
```

VS Code will run these concurrently and wait for all results before the coordinator continues.

---

## Restricting Subagent Access

The `agents` frontmatter property prevents the coordinator from accidentally picking the wrong agent:

```yaml
agents: ['Red', 'Green', 'Refactor']  # Only these three can be invoked
agents: '*'                            # All agents allowed (default)
agents: []                             # No subagent invocation allowed
```

> If two agents have similar names or descriptions, explicit restriction prevents the AI from picking the wrong one.

---

## Design Tips

- **Pass only what's needed**: craft the task prompt for each subagent precisely — don't dump your entire context  
- **One responsibility per agent**: avoid multi-role workers; they're harder to control and debug  
- **Include feedback loops**: instruct the coordinator to iterate (Planner → Architect → Planner again if needed)  
- **Use the fastest model for simple workers**: slow models on fast tasks wastes time and tokens
