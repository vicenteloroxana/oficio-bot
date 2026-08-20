# Bugs de correctitud

Prioridad #1. Buscá:

- Uso de código sync en un handler (`CLAUDE.md` exige `async/await` siempre en handlers).
- `await` faltante en una llamada async, o mezcla de `.result()`/bloqueo sync sobre una
  corrutina.
- Queries SQL mal armadas: placeholders `?` que no matchean la cantidad de parámetros, columnas
  mal nombradas, `JOIN`/`WHERE` que no filtra por `usuario_id` cuando debería (mezclar datos de
  dos trabajadores).
- Estados de `EstadoTrabajo` o `RespuestaRecordatorio` comparados como string literal en vez de
  usar el enum — un typo no lo detecta ni el linter ni, muchas veces, un test superficial.
- Cálculos de monto: `monto_sena > monto_total`, restas que pueden dar negativo
  (`monto_total - monto_sena` cuando la seña ya se contó dos veces), redondeos inconsistentes.
- Validaciones Pydantic faltantes en un modelo nuevo o campo nuevo (`Field(gt=0)`,
  `field_validator`) cuando `CLAUDE.md` ya pide ese tipo de invariante en `database/models.py`.
