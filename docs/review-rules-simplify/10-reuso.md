# Ángulo 1 — Reuso

Código nuevo que re-implementa algo que la codebase **ya tiene**.

Dónde buscar antes de concluir que algo es nuevo:

- `database/db.py` — todas las queries y funciones de acceso a datos ya existentes
  (`get_trabajo`, `get_trabajos_pendientes`, `get_resumen_mensual`, etc.)
- `database/models.py` — validaciones/invariantes que ya viven en un modelo Pydantic
- el handler hermano que resuelve un problema parecido (`cobro.py`, `presupuesto.py`,
  `recordatorio.py`, `registro.py`) — mismo patrón de `ConversationHandler`, mismo manejo de
  `context.user_data`, mismo estilo de validación de input del chat
- `services/pdf_service.py` para lo que toque generación de PDF

Para cada hallazgo, nombrá la función existente **con su ruta y línea** y confirmá que encaja:
mismo contrato, mismo tipo de retorno, misma firma async. Una función que «casi» sirve no es
reuso, es una trampa — decilo así.
