# Generar commit siguiendo convenciones del proyecto

Lee `docs/commit-conventions.md` para el árbol de decisión completo de
tipos, scopes válidos y ejemplos. Este command define el procedimiento;
el doc es la fuente de la regla.

## Pasos

1. Ejecutá `git status` y `git diff --staged` (si no hay nada staged,
   mostrá `git diff` y preguntá qué agregar con `git add`).
2. Aplicá el árbol de decisión de `docs/commit-conventions.md` a los
   cambios en staging. La spec de Conventional Commits es explícita:
   si el staging podría tener razonablemente más de un tipo, separalo
   en tantos commits como tipos claramente apropiados existan. Código
   y docs del mismo cambio comparten tipo (el doc lo confirma: "si el
   commit toca código Y documentación, el tipo lo define el código")
   — eso no se separa. Separá cuando el árbol de decisión, aplicado a
   los cambios mezclados, da tipos distintos (ej: un handler nuevo es
   `feat`, un typo corregido en un doc no relacionado es `docs` — dos
   tipos, dos commits). Si corresponde separar, proponé los commits
   distintos en lugar de forzar un solo tipo.
3. Elegí el `<scope>` según la tabla del doc si el cambio cae
   claramente en un módulo. Si toca varios módulos, omitilo.
4. Redactá la descripción: imperativo, minúsculas, sin punto final,
   en español.
5. Si el cambio rompe compatibilidad hacia atrás, marcalo con `!`
   después del tipo o agregá footer `BREAKING CHANGE:` (ver doc).
6. Mostrá el mensaje propuesto completo y esperá confirmación antes
   de ejecutar `git commit`.

## Formato final

```
<tipo>(<scope>): <descripción>

[cuerpo opcional — el porqué, no el qué]
```

## Antes de confirmar

- [ ] ¿El tipo elegido refleja el árbol de decisión, no una corazonada?
- [ ] ¿La descripción está en imperativo?
- [ ] ¿El staging mezcla cambios que, aplicado el árbol de decisión,
      caen en más de un tipo?
