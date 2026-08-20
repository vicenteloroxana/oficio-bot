# Convenciones de rama / commit

Prioridad #6. Verificá contra `docs/branch-conventions.md` y `docs/commit-conventions.md`:

- ¿El nombre de la rama usa un tipo válido (`feature`/`feat`, `bugfix`/`fix`, `hotfix`,
  `release`, `chore`)? Un cambio de solo docs/tests/refactor debería ser rama `chore/`, no
  `feature/`.
- ¿Los mensajes de commit siguen Conventional Commits (tipo, scope si aplica, descripción en
  imperativo, español)?
- ¿Hay commits directos sobre `main` en el historial de la rama (no debería haberlos)?

## Marcador de breaking change

Si el diff incluye un cambio que rompe compatibilidad hacia atrás, el commit debe llevar el
marcador `!` (`feat(scope)!: ...`) o un footer `BREAKING CHANGE:` — verificá que el marcador
esté cuando corresponde, y que no esté cuando no corresponde.

**Cuenta como breaking, para este bot:**
- Renombrar o quitar un valor de un enum ya persistido (`EstadoTrabajo`, `FormaPago`,
  `RespuestaRecordatorio`) — filas existentes en SQLite quedan con un valor que el código ya
  no reconoce.
- Cambiar el significado de una columna ya persistida (ej. que `monto_sena` deje de representar
  "seña acordada" y pase a significar otra cosa, sin migrar los datos existentes).
- Borrar una columna o tabla existente.
- Cambiar el formato de una fecha ya guardada, o cómo se calcula un campo derivado que otro
  código ya lee (ej. cambiar qué filtro define "pendiente" en `get_resumen_mensual` sin que el
  cambio sea aditivo — ver `docs/adr/006-pre-review-casos-borde.md` para el porqué de separar
  "cobrado" de "pendiente" por ejes de fecha distintos).

**No cuenta como breaking:**
- Agregar una tabla o columna nueva.
- Agregar un valor nuevo a un enum, sin tocar los existentes.
- Agregar un comando o handler nuevo que no cambia el comportamiento de los existentes.

Si hay un cambio breaking sin marcar → 🟠, citando el cambio y proponiendo el mensaje corregido.
Si el marcador `!` está pero nada en el diff es realmente breaking → 🟡, sugiriendo quitarlo.
