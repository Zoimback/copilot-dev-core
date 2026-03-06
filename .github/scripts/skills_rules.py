#!/usr/bin/env python3
"""
Valida que los archivos SKILL.md cumplen las hardrules del repositorio.

Hardrules:
  1. Frontmatter YAML válido delimitado por `---`
  2. Campo `name` presente y en kebab-case (solo minúsculas, dígitos y guiones)
  3. Campo `description` con más de 30 palabras
  4. La `description` menciona al menos una frase o caso de uso que activa la skill
  5. El body (cuerpo markdown después del frontmatter) no está vacío
  6. No contiene placeholders sin completar: `[...]`, `TODO`, `[versión]`, `[descripción]`
  7. Ninguna sección tiene únicamente su encabezado sin contenido
  8. El campo `name` coincide con el nombre del directorio padre (convención de este repositorio)

Salida:
  - Código de salida 0 si todos los archivos pasan.
  - Código de salida 1 si algún archivo falla.
  - Mensajes ERROR en stdout con el formato: ERROR [ruta]: <razón>
  - Mensaje ✅ en stdout si todos pasan.

Uso:
  python skills_rules.py ruta/SKILL.md [ruta/SKILL.md ...]
  python skills_rules.py "proyecto/.github/skills/**/SKILL.md"
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
KEBAB_RE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
ACTIVATION_KEYWORDS = [
    'úsala', 'úsalo', 'usa esta', 'usa este', 'usa cuando',
    'use this', 'use when', 'activa', 'trigger', 'cuando',
    'frases como', 'ante frases', 'invoke',
]


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
    """Parser YAML mínimo: soporta escalares, literales (`>` / `|`) y multilínea."""
    fields: dict = {}
    current_key = None
    current_lines: list[str] = []
    multiline = False

    for raw_line in frontmatter.split('\n'):
        # Nueva clave de nivel raíz
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)', raw_line)
        if m and not raw_line[0].isspace():
            if current_key is not None:
                fields[current_key] = ' '.join(current_lines).strip()
            current_key = m.group(1)
            val = m.group(2).strip()
            if val in ('>', '|', '>-', '>+', '|-', '|+'):
                current_lines = []
                multiline = True
            else:
                current_lines = [val.strip('"\'')] if val else []
                multiline = False
        elif current_key and raw_line and raw_line[0].isspace():
            current_lines.append(raw_line.strip())

    if current_key is not None:
        fields[current_key] = ' '.join(current_lines).strip()

    return fields


# ── Validación de secciones ────────────────────────────────────────────────────
def check_empty_sections(body: str) -> list[str]:
    """Devuelve lista de encabezados que no tienen contenido propio.

    Una sección se considera vacía únicamente si no hay NINGUNA línea con
    contenido (incluyendo sub-encabezados, código, etc.) entre ese encabezado
    y el siguiente encabezado del mismo nivel o superior.

    Los encabezados que aparecen dentro de bloques de código fenced (```...```)
    no se cuentan como secciones reales.
    """
    lines = body.split('\n')

    # Fase 1: detectar encabezados reales (fuera de code fences)
    sections: list[tuple[int, str, int]] = []  # (level, heading_text, line_idx)
    in_fence = False
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            in_fence = not in_fence
        if not in_fence:
            m = re.match(r'^(#{1,6})\s+(.+)$', line)
            if m:
                sections.append((len(m.group(1)), line.strip(), i))

    # Fase 2: verificar si cada sección tiene contenido (original, con código)
    empty: list[str] = []
    for idx, (level, heading, start) in enumerate(sections):
        end = len(lines)
        for next_level, _, next_start in sections[idx + 1:]:
            if next_level <= level:
                end = next_start
                break
        section_lines = lines[start + 1:end]
        has_content = any(ln.strip() for ln in section_lines)
        if not has_content:
            empty.append(heading)

    return empty


# ── Validador principal ────────────────────────────────────────────────────────
def validate_skill(file_path: str) -> list[str]:
    """Valida un archivo SKILL.md. Devuelve lista de mensajes de error."""
    errors: list[str] = []

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
        return errors  # Sin frontmatter el resto no tiene sentido

    fields = parse_yaml_fields(frontmatter)

    # ── Regla 2: Campo `name` en kebab-case ───────────────────────────────────
    name_val = fields.get('name', '').strip()
    if not name_val:
        errors.append("Regla 2: El frontmatter no contiene el campo `name`")
    elif not KEBAB_RE.match(name_val):
        errors.append(
            f"Regla 2: El campo `name` ('{name_val}') no está en kebab-case "
            "(solo minúsculas, dígitos y guiones)"
        )

    # ── Regla 3: `description` con más de 30 palabras ─────────────────────────
    desc_val = fields.get('description', '').strip()
    if not desc_val:
        errors.append("Regla 3: El frontmatter no contiene el campo `description`")
    else:
        word_count = len(desc_val.split())
        if word_count <= 30:
            errors.append(
                f"Regla 3: La `description` tiene {word_count} palabras (mínimo 31)"
            )

    # ── Regla 4: `description` menciona casos de uso ──────────────────────────
    if desc_val:
        desc_lower = desc_val.lower()
        has_activation = any(kw in desc_lower for kw in ACTIVATION_KEYWORDS)
        if not has_activation:
            errors.append(
                "Regla 4: La `description` no menciona ningún caso de uso o frase "
                "que active la skill (debe incluir palabras como 'úsala', 'usa', "
                "'activa', 'trigger', 'cuando', 'frases como', etc.)"
            )

    # ── Regla 5: Body no vacío ─────────────────────────────────────────────────
    if not body.strip():
        errors.append(
            "Regla 5: El body (cuerpo markdown después del frontmatter) está vacío"
        )

    # ── Regla 6: Sin placeholders (fuera de bloques de código) ─────────────────────
    body_no_fences = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    if PLACEHOLDER_RE.search(body_no_fences):
        errors.append(
            "Regla 6: Contiene placeholders sin completar "
            "(`[...]`, `TODO`, `[versión]`, `[descripción]`)"
        )

    # ── Regla 7: Ninguna sección solo con encabezado ──────────────────────────
    if body.strip():
        empty_sections = check_empty_sections(body)
        for heading in empty_sections:
            errors.append(
                f"Regla 7: La sección '{heading}' no tiene contenido después del encabezado"
            )

    # ── Regla 8: `name` coincide con el directorio padre ─────────────────────
    if name_val and KEBAB_RE.match(name_val):
        parent_dir = Path(file_path).parent.name
        if parent_dir and name_val != parent_dir:
            errors.append(
                f"Regla 8: El campo `name` ('{name_val}') no coincide con el nombre "
                f"del directorio padre ('{parent_dir}')"
            )

    return errors


# ── CLI ────────────────────────────────────────────────────────────────────────
def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(
            "Uso: python skills_rules.py <ruta/SKILL.md> [...]",
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
        errors = validate_skill(file_path)
        if errors:
            all_passed = False
            for msg in errors:
                print(f"ERROR [{file_path}]: {msg}")

    if all_passed:
        print("✅ Todos los archivos SKILL.md cumplen las hardrules.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()