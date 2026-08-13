# Generar commit siguiendo convenciones del proyecto

Lee `docs/commit-conventions.md` para el árbol de decisión completo de
tipos, scopes válidos y ejemplos. Este command define el procedimiento;
el doc es la fuente de la regla.

## Pasos

1. Ejecutá `git status` y `git diff --staged` (si no hay nada staged,
   mostrá `git diff` y preguntá qué agregar con `git add`).
2. Si hay cambios de naturaleza distinta mezclados en el staging
   (ej: código + docs no relacionados), sugerí separarlos en commits
   distintos en lugar de forzar un solo tipo.
3. Aplicá el árbol de decisión de `docs/commit-conventions.md` para
   elegir el `<tipo>`.
4. Elegí el `<scope>` según la tabla del doc si el cambio cae
   claramente en un módulo. Si toca varios módulos, omitilo.
5. Redactá la descripción: imperativo, minúsculas, sin punto final,
   en español.
6. Si el cambio rompe compatibilidad hacia atrás, marcalo con `!`
   después del tipo o agregá footer `BREAKING CHANGE:` (ver doc).
7. Mostrá el mensaje propuesto completo y esperá confirmación antes
   de ejecutar `git commit`.

## Formato final

```
<tipo>(<scope>): <descripción>

[cuerpo opcional — el porqué, no el qué]
```

## Antes de confirmar

- [ ] ¿El tipo elegido refleja el árbol de decisión, no una corazonada?
- [ ] ¿La descripción está en imperativo?
- [ ] ¿Se mezclaron cambios que deberían ir en commits separados?
