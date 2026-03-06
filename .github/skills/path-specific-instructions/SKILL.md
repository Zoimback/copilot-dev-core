---
name: path-specific-instructions
description: >
  Skill especializada en crear archivos NAME.instructions.md en .github/instructions/
  para aplicar instrucciones de Copilot solo a ciertos tipos de archivo o carpetas
  mediante patrones glob (applyTo). Úsala cuando el usuario quiera reglas que apliquen
  únicamente a ficheros .ts, .tsx, .py, tests, modelos, componentes, u otras rutas
  específicas, sin afectar a todo el repositorio. Activa esta skill ante frases como
  "instructions.md", "instrucciones para archivos .ts", "instrucciones para la carpeta tests",
  "instrucciones path-specific", "applyTo", "instrucciones por tipo de archivo",
  "reglas solo para componentes" o "instrucciones específicas de ruta".
  Para instrucciones globales del repositorio usa la skill github-copilot-instructions.
  Para instrucciones del agente usa la skill agents-md.
---

# `*.instructions.md` — Instrucciones específicas por ruta

Los archivos `NAME.instructions.md` en `.github/instructions/` permiten definir instrucciones
que Copilot aplica **solo cuando trabaja con ficheros que coincidan con un patrón glob**.
Esto evita sobrecargar `copilot-instructions.md` con reglas muy específicas y mantiene
unas instrucciones más precisas y relevantes.

> **Fuente oficial:** [docs.github.com — Creating path-specific custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions#creating-path-specific-custom-instructions-2)

---

## Cuándo usar este tipo de instrucciones

Usa `*.instructions.md` cuando necesites reglas que solo tienen sentido para **cierto contexto**:

- Estándares de test (solo para `*.test.ts`, `*.spec.py`, etc.)
- Convenciones de componentes UI (solo para `src/components/**/*.tsx`)
- Reglas de modelos de base de datos (solo para `src/models/**`)
- Guías de accesibilidad (solo para plantillas HTML o JSX)
- Reglas de seguridad para endpoints de API (solo para `src/routes/**`)

Si las reglas aplican a todo el repositorio, usa `copilot-instructions.md` en su lugar.

---

## Estructura de archivos

```
.github/
└── instructions/
    ├── testing.instructions.md          ← reglas para tests
    ├── react-components.instructions.md ← reglas para componentes
    ├── api/
    │   └── security.instructions.md     ← reglas de seguridad para rutas
    └── database/
        └── models.instructions.md       ← reglas para modelos
```

Los subdirectorios dentro de `.github/instructions/` son opcionales y sirven para organizar.

---

## Soporte por entorno

| Entorno | Soportado |
|---|---|
| GitHub.com — Coding Agent | ✅ |
| GitHub.com — Code Review | ✅ (primeros 4.000 chars) |
| GitHub.com — Copilot Chat | ❌ |
| VS Code — Copilot Chat | ✅ |
| VS Code — Coding Agent | ✅ |
| VS Code — Code Review | ❌ |
| JetBrains — Chat & Agent & Review | ✅ |
| Visual Studio — Chat | ✅ |
| Xcode — Chat & Agent & Review | ✅ |
| Copilot CLI | ✅ |

> Cuando un archivo coincide con el patrón y también existe `copilot-instructions.md`,
> **ambas instrucciones se usan a la vez**.

---

## Estructura de un archivo `*.instructions.md`

### Frontmatter obligatorio

Cada archivo debe comenzar con un bloque YAML que define a qué archivos aplica:

```markdown
---
applyTo: "src/**/*.ts"
---

Aquí van las instrucciones en Markdown.
```

### Campo `applyTo` — patrones glob

| Patrón | Qué archivos afecta |
|---|---|
| `**` o `**/*` | Todos los archivos del repositorio |
| `**/*.ts` | Todos los `.ts` en cualquier directorio |
| `src/**/*.ts` | Todos los `.ts` bajo `src/` |
| `src/*.ts` | Solo `.ts` directamente en `src/` (no subcarpetas) |
| `**/*.ts,**/*.tsx` | Múltiples patrones separados por coma |
| `tests/**/*.py` | Todos los `.py` bajo `tests/` |
| `app/models/**/*.rb` | Modelos Ruby bajo `app/models/` a cualquier profundidad |
| `**/subdir/**/*.py` | `.py` en cualquier carpeta llamada `subdir` en cualquier nivel |

### Campo `excludeAgent` — excluir agentes (opcional)

Evita que un agente concreto use estas instrucciones:

```yaml
---
applyTo: "**"
excludeAgent: "code-review"     # Solo el coding agent usa estas instrucciones
---
```

```yaml
---
applyTo: "**"
excludeAgent: "coding-agent"    # Solo Copilot code review usa estas instrucciones
---
```

Si se omite `excludeAgent`, tanto **Copilot coding agent** como **Copilot code review** usan el archivo.

---

## Ejemplos listos para usar

### Tests con Jest / TypeScript

```markdown
---
applyTo: "**/*.test.ts,**/*.spec.ts"
---

## Testing Standards (Jest + TypeScript)

- Use `describe` blocks to group related tests by feature or method.
- Each `it` or `test` name must start with "should".
- Use `beforeEach` for shared setup; avoid repetition across tests.
- Mock all external dependencies and side effects with `jest.mock`.
- Prefer `toEqual` over `toBe` for object comparisons.
- Test both the happy path and edge cases (null, empty, boundary values).
- Keep each test under 30 lines; extract helpers if needed.
```

### Tests con pytest / Python

```markdown
---
applyTo: "tests/**/*.py"
---

## Testing Standards (pytest)

- Use pytest as the primary testing framework.
- Follow the AAA pattern: Arrange, Act, Assert — one block per test.
- Write descriptive test names that explain the behavior: `test_should_reject_invalid_email`.
- Use pytest fixtures for setup and teardown (`@pytest.fixture`).
- Mock external dependencies (databases, APIs, file I/O) with `unittest.mock.patch`.
- Use `@pytest.mark.parametrize` for testing multiple similar scenarios.
- Test edge cases and error conditions, not only happy paths.
- Never test implementation details — test observable behavior.
```

### Componentes React

```markdown
---
applyTo: "src/components/**/*.tsx"
---

## React Component Standards

- Use functional components with hooks exclusively (no class components).
- Export each component as a named export.
- Define prop types with a TypeScript interface named `[ComponentName]Props`.
- Use Tailwind CSS for styling; avoid inline styles and CSS modules.
- Keep components under 150 lines; extract sub-components or custom hooks if needed.
- Do not fetch data directly in components — use service hooks from `src/hooks/`.
- Add a JSDoc comment describing the component's purpose above the export.
```

### Modelos / Acceso a base de datos

```markdown
---
applyTo: "src/models/**,src/repositories/**"
---

## Data Layer Standards

- Always use Prisma transactions for operations that modify multiple tables.
- Never expose raw database errors to upper layers — wrap them in domain errors.
- Repository methods must return domain types, not raw Prisma models.
- Use pagination for any query that may return more than 100 rows.
- Add input validation before any write operation.
```

### Endpoints de API / Seguridad

```markdown
---
applyTo: "src/routes/**,src/controllers/**"
excludeAgent: "code-review"
---

## API Security Standards

- Validate and sanitize all request inputs with Zod schemas before processing.
- Never trust user-supplied IDs — verify ownership against the authenticated user.
- Return generic error messages to clients; log detailed errors server-side only.
- Apply rate limiting middleware on all public endpoints.
- Use parameterized queries only; never concatenate user input into SQL strings.
```

### Accesibilidad (HTML/JSX)

```markdown
---
applyTo: "**/*.tsx,**/*.html"
---

## Accessibility Standards (WCAG 2.1 AA)

- Every `<img>` must have a descriptive `alt` attribute; use `alt=""` for decorative images.
- Interactive elements (`<button>`, `<a>`) must have accessible text or `aria-label`.
- Form fields must be associated with a `<label>` via `htmlFor` / `id`.
- Do not rely on color alone to convey information — add text or icons.
- Ensure focus order matches the visual reading order.
- Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text.
```

---

## Cómo se combina con `copilot-instructions.md`

Si el archivo en el que Copilot está trabajando coincide con el `applyTo` de un
`*.instructions.md` **y** también existe `copilot-instructions.md`, ambos archivos
se inyectan en el prompt. Las instrucciones path-specific tienen **mayor prioridad**
en caso de conflicto.

Esto significa que puedes definir reglas generales en `copilot-instructions.md` y
sobrescribir o complementar solo lo que sea necesario con archivos path-specific,
sin duplicar contenido.

---

## Verificar que funciona

**VS Code:** En el panel de Copilot Chat, abre un archivo que coincida con el patrón
y haz una pregunta. En la lista "References" de la respuesta debe aparecer el archivo
`*.instructions.md` activo.

**Ajuste en VS Code:** Si no funciona, verifica que `Code Generation: Use Instruction Files`
esté activado en la configuración del editor (`Ctrl+,` → busca "instruction file").

---

## Referencia oficial

- [Adding repository custom instructions — path-specific](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions#creating-path-specific-custom-instructions-2)
- [Testing automation example — GitHub Docs](https://docs.github.com/en/copilot/tutorials/customization-library/custom-instructions/testing-automation)
- [Support for different types of custom instructions](https://docs.github.com/en/copilot/reference/custom-instructions-support)
