---
name: github-copilot-instructions
description: >
  Skill especializada en crear y editar el archivo .github/copilot-instructions.md
  (instrucciones globales de repositorio para GitHub Copilot). Úsala cuando se
  quiera definir estándares de código globales, documentar el stack del proyecto, describir
  la arquitectura, configurar convenciones de nombres o añadir comandos de build/test que
  Copilot deba conocer siempre. Activa esta skill ante frases como "copilot-instructions.md",
  "instrucciones globales", "instrucciones de repositorio", "que Copilot conozca mi proyecto",
  "estándares de código para Copilot" o "instrucciones para todo el repositorio".
  Para instrucciones por tipo de archivo usa la skill path-specific-instructions.
  Para instrucciones de agente usa la skill agents-md.
---

# `copilot-instructions.md` — Instrucciones globales de repositorio

El archivo `.github/copilot-instructions.md` proporciona a Copilot contexto permanente
sobre el repositorio. Se inyecta automáticamente en **cada petición** dentro del repositorio,
sin necesidad de mencionarlo en el chat.

> **Fuente oficial:** [docs.github.com — Adding repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)

---

## Cuándo usar este archivo

Usa `copilot-instructions.md` para información que es **siempre relevante** en cualquier
conversación del repositorio:

- Descripción del proyecto, propósito y goals
- Stack tecnológico (frameworks, librerías, versiones)
- Estructura de carpetas y ubicación de los módulos principales
- Convenciones de código globales (nombres, formato, patrones)
- Comandos de build, test y lint
- Notas de arquitectura que reducen la exploración del agente

> Para reglas específicas por tipo de archivo, usa la **skill `path-specific-instructions`**.
> Para instrucciones del flujo de trabajo del agente, usa la **skill `agents-md`**.

---

## Cómo crearlo

1. Crea `.github/` en la raíz del repositorio si no existe.
2. Crea el archivo `copilot-instructions.md` dentro.
3. Escribe en Markdown, en lenguaje natural. El espaciado entre líneas se ignora.
4. Guarda — las instrucciones se activan **de inmediato**.

```
.github/
└── copilot-instructions.md   ← este archivo
```

---

## Soporte por entorno

| Entorno | Soportado |
|---|---|
| GitHub.com — Copilot Chat | ✅ |
| GitHub.com — Coding Agent | ✅ |
| GitHub.com — Code Review | ✅ (solo primeros 4.000 chars) |
| VS Code — Copilot Chat | ✅ |
| VS Code — Coding Agent | ✅ |
| VS Code — Code Review | ✅ |
| JetBrains — Chat & Agent | ✅ |
| Visual Studio — Chat | ✅ |
| Copilot CLI | ✅ |

> **Límite importante:** Copilot code review solo procesa los **primeros 4.000 caracteres**
> del archivo. Coloca la información más crítica al principio.

---

## Precedencia entre tipos de instrucciones

Cuando varios tipos de instrucciones aplican a la vez, todas se usan, pero en este orden
de prioridad (mayor → menor):

1. Instrucciones personales del usuario
2. Path-specific (`.github/instructions/**/*.instructions.md`)
3. **Repository-wide (`.github/copilot-instructions.md`)** ← este archivo
4. Agent instructions (`AGENTS.md`)
5. Instrucciones de organización

---

## Plantilla de referencia

```markdown
# [Nombre del proyecto]

[Descripción breve del repositorio en 1-2 frases.]

## Stack

- [Framework principal] [versión]
- [Base de datos] [versión]
- [Testing] [versión]

## Folder Structure

- `/src`: [descripción]
- `/src/routes`: [descripción]
- `/src/services`: [descripción]
- `/tests`: [descripción]

## Coding Standards

- [Regla de estilo 1. Usa imperativo: "Use early returns."]
- [Regla de estilo 2]
- [Convención de nombres]

## Build & Validation

- Install: `[comando]`
- Build: `[comando]`
- Test: `[comando]`
- Lint: `[comando]`

## Architecture Notes

[Información sobre decisiones de arquitectura, dependencias no obvias,
patrones importantes. Reduce la exploración manual del agente.]
```

---

## Ejemplo completo (Node.js + TypeScript)

```markdown
# Task Manager API

REST API for managing user tasks and to-do lists. Built with Node.js, Express,
and TypeScript. Uses PostgreSQL via Prisma and Jest for testing.

## Folder Structure

- `/src/routes`: Express route handlers
- `/src/services`: Business logic layer
- `/src/models`: Prisma schema and generated types
- `/tests`: Unit and integration tests (mirrors `/src` structure)

## Coding Standards

- Use TypeScript strict mode. Never use `any`.
- Use early returns to avoid deep nesting.
- Use camelCase for variables/functions, PascalCase for classes/types/interfaces.
- Use single quotes for strings. Always add semicolons.
- Validate all inputs at route level with Zod schemas.

## Libraries and Frameworks

- Express 4.x for routing.
- Prisma ORM for database access (schema in `/prisma/schema.prisma`).
- Zod for input validation.
- Jest + Supertest for testing.

## Build & Test

- Install: `npm install`
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`
- Always run `npm run lint` before committing.
```

---

## Buenas prácticas

### Sí ✅
- Frases cortas e imperativas: "Use early returns." — una idea por línea
- Incluir versiones exactas de frameworks: `React 18`, `Python 3.12`
- Documentar comandos de build/test verificados y el orden correcto
- Indicar dependencias no obvias entre módulos o ficheros que deben sincronizarse
- Poner la información más importante al inicio (límite de 4.000 chars para code review)

### No ❌
- Referenciar ficheros externos: `Follow styleguide.md` — Copilot puede no acceder a él
- Instrucciones subjetivas de estilo conversacional: `Be a friendly colleague`
- Restricciones de longitud de respuesta — resultados inconsistentes
- Instrucciones contradictorias con las path-specific o de organización

---

## Verificar que funciona

**VS Code:** En el panel de Copilot Chat, expande "References" en cualquier respuesta.
El archivo `.github/copilot-instructions.md` debe aparecer como referencia activa.

**GitHub.com:** Adjunta el repositorio a la conversación de Copilot Chat; las instrucciones
se listan como referencia en la parte superior de cada respuesta.

**Ajuste en VS Code:** Si no funciona, verifica que la opción
`Code Generation: Use Instruction Files` esté activada en la configuración.

---

## Referencia oficial

- #tool:web/fetch [Adding repository custom instructions — GitHub Docs](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- #tool:web/fetch  [About customizing GitHub Copilot responses](https://docs.github.com/en/copilot/concepts/prompting/response-customization)
- #tool:web/fetch  [Custom instructions examples library](https://docs.github.com/en/copilot/tutorials/customization-library/custom-instructions)
