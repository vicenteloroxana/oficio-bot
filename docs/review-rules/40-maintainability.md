# Reuso / simplificación / mantenibilidad

Prioridad #4. Buscá:

- Lógica duplicada que ya existe en `database/db.py` o en otro handler (ej. reimplementar el
  filtro de "trabajos pendientes" en vez de reusar `get_trabajos_pendientes`).
- Funciones que superan las 20 líneas o más de 3 niveles de anidación (límite explícito de
  CLAUDE.md) — señalar dónde extraer.
- Falta de type hints o de docstring en español en una función de negocio nueva.
- Complejidad innecesaria: abstracción para un solo caso de uso, config para un valor que nunca
  cambia, manejo de errores especulativo para algo que no puede pasar en este flujo.
