---
name: agents-md
description: >
  Skill especializada en crear archivos AGENTS.md (y CLAUDE.md / GEMINI.md) para
  proporcionar instrucciones de flujo de trabajo al Copilot coding agent y otros agentes
  de IA. Úsala cuando el usuario quiera definir cómo debe comportarse el agente al crear
  PRs, ejecutar CI, explorar el código, o manejar situaciones específicas del flujo de
  desarrollo. Activa esta skill ante frases como "AGENTS.md", "instrucciones para el agente",
  "coding agent", "instrucciones de flujo", "instrucciones para PR", "que el agente sepa
  cómo trabajar", "CLAUDE.md", "GEMINI.md", o cualquier petición de personalizar el
  comportamiento del coding agent de Copilot, Claude o Gemini.
  Para instrucciones globales del repositorio usa la skill github-copilot-instructions.
  Para instrucciones por tipo de archivo usa la skill path-specific-instructions.
---

# `AGENTS.md` — Instrucciones para agentes de IA

Los archivos `AGENTS.md` (y sus equivalentes `CLAUDE.md` / `GEMINI.md`) contienen
instrucciones de flujo de trabajo dirigidas específicamente al **coding agent**. A diferencia
de `copilot-instructions.md`, que está enfocado en estándares de código, `AGENTS.md` le
indica al agente **cómo debe actuar** mientras trabaja: cómo explorar el repo, cómo ejecutar
CI, cómo crear pull requests, qué validaciones hacer antes de finalizar.

> **Fuente oficial:** [docs.github.com — Creating custom instructions (Agent instructions)](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions#creating-custom-instructions)
> **Especificación AGENTS.md:** [github.com/openai/agents.md](https://github.com/openai/agents.md)

---

## Diferencia con `copilot-instructions.md`

| | `copilot-instructions.md` | `AGENTS.md` |
|---|---|---|
| **Propósito** | Estándares de código y conocimiento del proyecto | Flujo de trabajo del agente |
| **Audiencia** | Copilot Chat + Coding Agent + Code Review | Principalmente Coding Agent |
| **Contenido típico** | Stack, estructura de carpetas, convenciones | Cómo crear PRs, cuándo ejecutar tests, cómo explorar |
| **Prioridad** | Mayor | Menor (se usa cuando no hay conflicto) |
| **Soporte en Chat** | ✅ Todos los entornos | ❌ Solo coding agent |

Usa `AGENTS.md` para instrucciones de **comportamiento del agente** que no tienen sentido
en una conversación de chat normal. Si la información es relevante tanto para el chat como
para el agente, ponla en `copilot-instructions.md`.

---

## Archivos soportados

| Archivo | Usado por |
|---|---|
| `AGENTS.md` | Copilot coding agent, Copilot CLI |
| `CLAUDE.md` | Claude (Anthropic) coding agent |
| `GEMINI.md` | Gemini (Google) coding agent |

Puedes tener los tres archivos a la vez si usas múltiples agentes. Para Copilot, usa `AGENTS.md`.

---

## Placement: precedencia por proximidad

Los archivos `AGENTS.md` se pueden colocar en **cualquier directorio** del repositorio.
El agente usa el archivo más cercano al contexto en el que está trabajando:

```
repo-root/
├── AGENTS.md                  ← instrucciones globales (toda la raíz)
├── src/
│   ├── AGENTS.md              ← sobrescribe/complementa para src/
│   └── backend/
│       └── AGENTS.md          ← más específico para src/backend/
└── tests/
    └── AGENTS.md              ← instrucciones específicas para tests/
```

El archivo más cercano en el árbol de directorios **tiene precedencia** sobre los de nivel
superior. Las instrucciones más genéricas van en la raíz; las más específicas, en subcarpetas.

> **VS Code:** El soporte de `AGENTS.md` fuera de la raíz del workspace está desactivado
> por defecto. Para activarlo, consulta la documentación de VS Code sobre custom instructions.

---

## Soporte por entorno

| Entorno | Soportado |
|---|---|
| GitHub.com — Coding Agent | ✅ |
| GitHub.com — Code Review | ❌ |
| GitHub.com — Copilot Chat | ❌ |
| VS Code — Coding Agent | ✅ |
| VS Code — Copilot Chat | ✅ (AGENTS.md en raíz) |
| VS Code — Code Review | ❌ |
| JetBrains — Coding Agent | ✅ |
| JetBrains — Copilot Chat | ❌ |
| Copilot CLI | ✅ |
| Eclipse — Coding Agent | ✅ |
| Xcode — Coding Agent | ✅ |

---

## Qué incluir en un `AGENTS.md`

Un buen `AGENTS.md` contiene instrucciones sobre el **proceso de trabajo**, no sobre
estándares de código. Piensa en él como el "manual de incorporación" del agente:

### 1. Cómo explorar el repositorio
Indica al agente qué archivos leer primero, dónde está la configuración, cómo está
organizado el código para que no pierda tiempo buscando.

### 2. Cómo ejecutar builds y tests
Documenta el orden exacto de comandos, las versiones de herramientas requeridas, los
errores conocidos y sus remedios. El agente ejecutará estos comandos — necesita instrucciones
precisas y verificadas.

### 3. Cómo crear Pull Requests
Indica el formato del título y descripción del PR, a quién asignar para revisión, qué
checks de CI deben pasar antes de solicitar review, si hay template de PR a usar.

### 4. Validaciones antes de finalizar
Qué pasos debe completar el agente antes de considerar su trabajo terminado: lint, tests,
build, revisión de seguridad, etc.

### 5. Información de arquitectura crítica
Dependencias no obvias entre módulos, ficheros que deben sincronizarse, patrones de error
que el agente debe respetar.

---

## Plantilla de `AGENTS.md`

```markdown
# Agent Instructions

## Repository Overview

[Descripción breve de qué hace este repositorio y su arquitectura principal.]

## Getting Started

Before making changes, read these files to understand the codebase:
- `README.md` — project overview and setup
- `[ruta a fichero de configuración principal]` — application config
- `[ruta a fichero de arquitectura o ADR]` — architectural decisions

## Build & Validation

Always run these commands in this exact order before submitting:

1. Install dependencies: `[comando]`
2. Build: `[comando]`
3. Run tests: `[comando]`
4. Lint: `[comando]`

All commands must pass without errors. If a test fails, fix the issue — do not skip.

## Creating Pull Requests

- Title format: `[type]: [short description]` (types: feat, fix, docs, refactor, test)
- Description must include: what changed, why it changed, and how to test it.
- Assign `[team or user]` as reviewer.
- The `[CI workflow name]` GitHub Actions workflow must pass before requesting review.

## Important Architecture Notes

- [Dependencia crítica entre módulos A y B]
- [Ficheros que deben mantenerse sincronizados]
- [Patrón de errores que debe respetarse]
- [Cualquier workaround conocido a un problema del entorno]

## Constraints

- Do not modify `[ficheros protegidos]` without explicit user instruction.
- Do not upgrade dependencies unless specifically asked.
- Always trust these instructions; only search if the information here is incomplete or outdated.
```

---

## Ejemplo completo — API Node.js

```markdown
# Agent Instructions

## Repository Overview

REST API for task management built with Node.js 20, Express 4, TypeScript, and PostgreSQL.
The Prisma ORM handles all database access. Tests run with Jest + Supertest.

## Getting Started

Read these files before making changes:
- `README.md` for project overview
- `prisma/schema.prisma` for the database schema
- `src/middleware/` to understand authentication and validation layers

## Build & Validation

Run in this order every time:

1. `npm install` — install dependencies
2. `npm run build` — compile TypeScript (must succeed with 0 errors)
3. `npm test` — all tests must pass
4. `npm run lint` — no lint errors allowed

If `npm run build` fails due to a missing type, check if there is a `@types/` package
to install. Do not use `// @ts-ignore` to bypass errors.

## Creating Pull Requests

- Title format: `feat:`, `fix:`, `refactor:`, `test:`, or `docs:` prefix required.
- PR description must include a "Testing" section explaining how to verify the change.
- The "CI / build-and-test" GitHub Actions check must be green before requesting review.
- Assign the `backend-team` group as reviewer.

## Architecture Notes

- Route handlers must only call service functions — never access the database directly.
- All database queries go through `src/repositories/`. Never import Prisma client
  outside of repository files.
- Environment variables are validated on startup in `src/config/env.ts`. Add new
  variables there before using them elsewhere.
- The `src/middleware/auth.ts` middleware must be applied to all non-public routes.

## Constraints

- Do not modify `prisma/migrations/` manually — use `npx prisma migrate dev` instead.
- Do not upgrade `prisma` or `@prisma/client` unless asked — there is a known
  breaking change in version 6.x under investigation.
```

---

## Ejemplo completo — Monorepo con subdirectorios

Cuando tienes un monorepo, puedes tener instrucciones generales en la raíz y específicas
en cada paquete:

**`/AGENTS.md`** (raíz):
```markdown
# Agent Instructions — Monorepo Root

This monorepo contains three packages: `packages/api`, `packages/web`, and `packages/shared`.

## Global Commands

- Install all dependencies: `npm install` (run from root — uses workspaces)
- Build all packages: `npm run build --workspaces`
- Run all tests: `npm test --workspaces`

## Making Changes

Always determine which package(s) are affected before making changes. Read the
relevant package-level AGENTS.md for specific instructions.
```

**`/packages/api/AGENTS.md`** (específico del paquete api):
```markdown
# Agent Instructions — API Package

## Build & Test

- Build: `npm run build` (from packages/api/)
- Test: `npm test` (from packages/api/)

## Database Changes

Always run `npx prisma generate` after modifying `prisma/schema.prisma`.
Run `npx prisma migrate dev --name [description]` to create a new migration.
Never edit migration files manually.
```

---

## Buenas prácticas

### Sí ✅
- Documentar comandos verificados con el orden exacto y precondiciones
- Mencionar errores conocidos y sus remedios
- Indicar archivos críticos que el agente debe leer primero
- Especificar el formato de PR y qué checks deben pasar
- Usar "Always", "Never", "Must" para instrucciones obligatorias
- Indicar explícitamente al agente que confíe en estas instrucciones y solo busque si están incompletas

### No ❌
- Duplicar reglas de código que ya están en `copilot-instructions.md`
- Instrucciones vagas: `Be careful with the database` — mejor: `Never write raw SQL; always use Prisma client methods`
- Comandos que no has verificado que funcionen — el agente los ejecutará tal cual
- Dejar `AGENTS.md` vacío o sin actualizar cuando el proceso de build cambia

---

## Referencia oficial

- [Adding repository custom instructions — Agent instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions#creating-custom-instructions)
- [Support for different types of custom instructions](https://docs.github.com/en/copilot/reference/custom-instructions-support)
- [openai/agents.md — AGENTS.md specification](https://github.com/openai/agents.md)
- [About agentic memory for GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/copilot-memory)
