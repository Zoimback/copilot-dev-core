#!/usr/bin/env python3
"""
Valida que los archivos *.instructions.md cumplen las hardrules del repositorio.

Hardrules:
  1. Frontmatter YAML válido delimitado por `---`
  2. Campo `description` presente en el frontmatter
  3. Campo `applyTo` presente, no vacío y con glob válido
     (soporta múltiples patrones separados por coma)
  4. El body contiene al menos 3 reglas o instrucciones concretas
  5. Las instrucciones están redactadas en imperativo (comienzan con verbo),
     no en forma meramente descriptiva
  6. No contiene placeholders sin completar: `[...]`, `TODO`, `[versión]`, `[descripción]`
  7. El nombre del archivo termina en `.instructions.md` (convención oficial GitHub)
  8. Si está presente el campo `excludeAgent`, su valor debe ser
     `"code-review"` o `"coding-agent"` (valores oficiales de GitHub)

Salida:
  - Código de salida 0 si todos los archivos pasan.
  - Código de salida 1 si algún archivo falla.
  - Mensajes ERROR en stdout con el formato: ERROR [ruta]: <razón>
  - Mensaje ✅ en stdout si todos pasan.

Uso:
  python instructions_rules.py ruta/nombre.instructions.md [...]
  python instructions_rules.py "proyecto/.github/instructions/*.instructions.md"
"""

import sys
import re
import glob
from pathlib import Path

# ── Patrones compilados ────────────────────────────────────────────────────────
PLACEHOLDER_RE = re.compile(
    r'\[\.{2,3}\]'            # [...] o [...]
    r'|\bTODO\b'              # marcador TODO (mayúsculas estrictas)
    r'|\[versi[oó]n\]'        # [version] o [versión]
    r'|\[descripci[oó]n\]'   # [descripcion] o [descripción]
)
EXCLUDE_AGENT_VALID = {'code-review', 'coding-agent'}

# Verbos típicos al inicio de instrucciones en español e inglés
IMPERATIVE_RE = re.compile(
    r'^(Usa|Use|Crea|Create|Define|Asegura|Ensure|Avoid|Evita|Incluye|Include|'
    r'Añade|Add|Sigue|Follow|Mantén|Keep|Especifica|Specify|Documenta|Document|'
    r'Prefiere|Prefer|Limita|Limit|Valida|Validate|Importa|Import|Emplea|Employ|'
    r'Aplica|Apply|Configura|Configure|Escribe|Write|Declara|Declare|Nombra|Name|'
    r'Retorna|Return|Lanza|Throw|Registra|Register|Comprueba|Check|Verifica|Verify|'
    r'Proporciona|Provide|Instala|Install|Establece|Set|Genera|Generate)',
    re.IGNORECASE,
)


# ── Parseo de frontmatter ──────────────────────────────────────────────────────
def split_frontmatter(content: str):
    """Devuelve (frontmatter_str | None, body_str)."""
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        return None, content
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            return '\n'.join(lines[1:i]), '\n'.join(lines[i + 1:])
    return None, content


def parse_yaml_fields(frontmatter: str) -> dict:
    """Parser YAML mínimo: soporta escalares y bloques literales (`>` / `|`)."""
    fields: dict = {}
    current_key = None
    current_lines: list[str] = []

    for raw_line in frontmatter.split('\n'):
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)', raw_line)
        if m and not raw_line[0].isspace():
            if current_key is not None:
                fields[current_key] = ' '.join(current_lines).strip()
            current_key = m.group(1)
            val = m.group(2).strip()
            if val in ('>', '|', '>-', '>+', '|-', '|+'):
                current_lines = []
            else:
                current_lines = [val.strip('"\'')] if val else []
        elif current_key and raw_line and raw_line[0].isspace():
            current_lines.append(raw_line.strip().strip('",'))

    if current_key is not None:
        fields[current_key] = ' '.join(current_lines).strip()

    return fields


# ── Validación de globs ────────────────────────────────────────────────────────
def is_valid_glob(value: str) -> bool:
    """
    Devuelve True si todos los patrones (separados por coma) contienen
    al menos un `*` o una extensión de archivo explícita.
    Refleja los ejemplos oficiales de GitHub Copilot.
    """
    patterns = [p.strip().strip('"\'' ) for p in value.split(',')]
    for p in patterns:
        if not p:
            return False
        # Válido: contiene * (glob comodín) o tiene extensión explícita (.rb, .ts…)
        if '*' not in p and not re.search(r'\.[a-zA-Z0-9]+$', p):
            return False
    return True


# ── Conteo de instrucciones ────────────────────────────────────────────────────
def count_instructions(body: str) -> int:
    """Cuenta ítems de lista y párrafos que parecen instrucciones concretas."""
    count = 0
    for line in body.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        # Ítems de lista (- / * / + / 1.)
        if re.match(r'^[-*+]\s+\S', stripped) or re.match(r'^\d+\.\s+\S', stripped):
            count += 1
        # Párrafos que empiezan con mayúscula y tienen ≥5 palabras (excluir encabezados)
        elif (
            not re.match(r'^#{1,6}\s', stripped)
            and re.match(r'^[A-ZÁÉÍÓÚÑ]', stripped)
            and len(stripped.split()) >= 5
        ):
            count += 1
    return count


# ── Validador principal ────────────────────────────────────────────────────────
def validate_instructions(file_path: str) -> list[str]:
    """Valida un archivo *.instructions.md. Devuelve lista de mensajes de error."""
    errors: list[str] = []

    # ── Regla 7: Nomenclatura del archivo ─────────────────────────────────────
    if not file_path.replace('\\', '/').split('/')[-1].endswith('.instructions.md'):
        errors.append(
            "Regla 7: El nombre del archivo debe terminar en `.instructions.md` "
            "(convención oficial de GitHub Copilot)"
        )

    try:
        content = Path(file_path).read_text(encoding='utf-8')
    except OSError as exc:
        return [f"No se puede leer el archivo: {exc}"]

    # ── Regla 1: Frontmatter YAML válido ──────────────────────────────────────
    frontmatter, body = split_frontmatter(content)
    if frontmatter is None:
        errors.append(
            "Regla 1: No tiene frontmatter YAML válido delimitado por `---`"
        )
        return errors

    fields = parse_yaml_fields(frontmatter)

    # ── Regla 2: Campo `description` ──────────────────────────────────────────
    if not fields.get('description', '').strip():
        errors.append("Regla 2: El frontmatter no contiene el campo `description`")

    # ── Regla 3: Campo `applyTo` con glob válido ───────────────────────────────
    # GitHub docs usan 'applyTo' (camelCase)
    apply_to = fields.get('applyTo') or fields.get('applyto', '')
    if not apply_to and 'applyTo' not in fields and 'applyto' not in fields:
        errors.append("Regla 3: El frontmatter no contiene el campo `applyTo`")
    elif not apply_to.strip():
        errors.append("Regla 3: El campo `applyTo` está vacío")
    elif not is_valid_glob(apply_to.strip()):
        errors.append(
            f"Regla 3: El valor de `applyTo` ('{apply_to}') no es un glob válido. "
            "Debe contener `*` o una extensión de archivo (ej. `**/*.ts`, `src/**`)"
        )

    # ── Regla 4: Body con al menos 3 instrucciones ────────────────────────────
    if not body.strip():
        errors.append(
            "Regla 4: El body está vacío — debe contener al menos 3 instrucciones"
        )
    else:
        n = count_instructions(body)
        if n < 3:
            errors.append(
                f"Regla 4: El body contiene {n} instrucción/es detectadas (mínimo 3)"
            )

    # ── Regla 5: Instrucciones en imperativo ──────────────────────────────────
    if body.strip():
        list_items = re.findall(
            r'^[-*+\d\.]+\s+(.+)$', body, re.MULTILINE
        )
        if list_items:
            non_imperative = [
                item for item in list_items
                if not IMPERATIVE_RE.match(item.strip())
            ]
            # Falla si más de la mitad de los ítems no comienzan con verbo
            if len(non_imperative) > len(list_items) / 2:
                examples = '; '.join(f"'{i[:40]}'" for i in non_imperative[:3])
                errors.append(
                    f"Regla 5: La mayoría de los ítems de lista no empiezan con verbo "
                    f"imperativo (ejemplos: {examples})"
                )

    # ── Regla 6: Sin placeholders (fuera de bloques de código) ─────────────────────
    body_no_fences = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    if PLACEHOLDER_RE.search(body_no_fences):
        errors.append(
            "Regla 6: Contiene placeholders sin completar "
            "(`[...]`, `TODO`, `[versión]`, `[descripción]`)"
        )

    # ── Regla 8: `excludeAgent` con valor válido (si está presente) ───────────
    exclude_agent = fields.get('excludeAgent', '').strip().strip('"\'')
    if fields.get('excludeAgent') is not None and exclude_agent not in EXCLUDE_AGENT_VALID:
        errors.append(
            f"Regla 8: El campo `excludeAgent` tiene el valor '{exclude_agent}'. "
            f"Los valores permitidos son: {sorted(EXCLUDE_AGENT_VALID)}"
        )

    return errors


# ── CLI ────────────────────────────────────────────────────────────────────────
def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(
            "Uso: python instructions_rules.py <ruta/*.instructions.md> [...]",
            file=sys.stderr,
        )
        sys.exit(1)

    files: list[str] = []
    for pattern in args:
        expanded = glob.glob(pattern, recursive=True)
        files.extend(expanded if expanded else [pattern])

    if not files:
        print("No se encontraron archivos para validar.", file=sys.stderr)
        sys.exit(1)

    all_passed = True
    for file_path in files:
        errors = validate_instructions(file_path)
        if errors:
            all_passed = False
            for msg in errors:
                print(f"ERROR [{file_path}]: {msg}")

    if all_passed:
        print("✅ Todos los archivos .instructions.md cumplen las hardrules.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
