# Ángulo 4 — Altitud

¿Cada cambio está hecho a la **profundidad** correcta, o es un parche frágil?

- un caso especial agregado directo en un handler, donde generalizarlo en `database/db.py`
  hubiera sido más limpio (ej. un `WHERE` extra hardcodeado en un handler en vez de un parámetro
  de la función de acceso a datos)
- lógica de negocio metida en un handler cuando debería vivir en `database/db.py` o en un
  validador de `database/models.py` (ej. una cuenta de monto o una comparación de fechas hecha
  a mano en el handler en vez de en la query o en un `field_validator`)
- un arreglo puesto en el llamador que corresponde a la función compartida, o al revés — ej.
  normalizar un resultado de SQLite (`NULL` → `0`) repetido en cada handler en vez de una vez
  en `database/db.py`
- conocimiento duplicado entre capas: el mismo valor de enum, el mismo formato de fecha
  (`strftime('%Y-%m', ...)`), el mismo texto de mensaje al usuario expresado en más de un lugar
- un archivo nuevo en una carpeta que no sigue la estructura que fija CLAUDE.md
  (`handlers/`, `services/`, `database/`, `templates/`, `assets/`)

Si la altitud está bien, decilo. No inventes opiniones de arquitectura para llenar la lista.
