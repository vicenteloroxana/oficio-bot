# Reglas de negocio de CLAUDE.md

Prioridad #3. `CLAUDE.md` es la especificación estable del proyecto — no una sugerencia.
Verificá que el diff no la contradiga:

- ¿El diálogo implementado coincide con el mockup del Momento correspondiente (mensajes,
  orden de las preguntas, botones)? Si el diff se aparta del mockup a propósito, debería
  haber una nota explicando por qué (igual que las notas `>` que ya acompañan cada mockup en
  CLAUDE.md).
- ¿Se tocó `database/models.py`, `templates/presupuesto.html`, o algún archivo de configuración
  de Railway sin haber preguntado antes? CLAUDE.md los marca explícitamente como "NO tocar sin
  preguntar".
- ¿Hay algo de fase 2/3 (Mercado Pago, WhatsApp) implementado antes de tiempo?
- ¿El diff deja algo pendiente de una decisión futura (config que solo se valida en Railway
  real, placeholder para un Momento no implementado) sin anotarlo en
  `docs/backlog.md` → "Pendiente de decidir"? Si no queda en el backlog, se pierde.
- ¿El diff cambia el esquema de `trabajos`/`usuarios`/`recordatorios` sin que la tabla
  "Modelo de datos" de CLAUDE.md se haya actualizado en el mismo diff?
