# Crear rama siguiendo convenciones del proyecto

Lee `docs/branch-conventions.md` para la especificación completa
(Conventional Branch v1.1.0), tipos válidos y reglas de nomenclatura.
Este command define el procedimiento; el doc es la fuente de la regla.

## Pasos

1. Verificá que no haya cambios sin commitear sobre `main` (`git status`).
   Si los hay, la rama se crea igual, y esos cambios se commitean
   después en la rama nueva — nunca en `main`.
2. Preguntá (si no es obvio del pedido del usuario) qué tipo de cambio es:
   funcionalidad nueva, corrección de bug, urgente en producción, release,
   o mantenimiento (docs/tests/refactor/config → todo esto es `chore`).
3. Elegí el `<tipo>` según la tabla de `docs/branch-conventions.md`.
   Recordá: `docs`, `refactor`, `test`, `ci` son tipos de COMMIT, no de
   rama — si el cambio es de ese tipo, la rama va en `chore/`.
4. Armá la descripción: minúsculas, guiones entre palabras, solo
   `a-z0-9-.`, sin guiones bajos ni consecutivos.
5. Mostrá el nombre de rama propuesto (`<tipo>/<descripción>`) y
   esperá confirmación antes de ejecutar `git checkout -b`.

## Formato final

```
<tipo>/<descripción-en-minúsculas-con-guiones>
```

## Antes de confirmar

- [ ] ¿El tipo es uno de los 5 válidos (feature/feat, bugfix/fix,
      hotfix, release, chore)?
- [ ] Si el cambio es solo docs/tests/refactor, ¿la rama es `chore/`?
- [ ] ¿La descripción no tiene mayúsculas, guiones bajos ni caracteres
      fuera de `a-z0-9-.`?
