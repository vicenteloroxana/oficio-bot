# Revisión local pre-PR con las reglas de docs/review-rules/

Revisá los cambios de esta rama **antes** de abrir el PR, con las reglas de
`docs/review-rules/*.md` (ver `docs/adr/006-pre-review-casos-borde.md` para el porqué
de este mecanismo). Es un pre-check local — no reemplaza el pipeline de CI.

## Pasos

1. Leé, en orden, todos los archivos `docs/review-rules/*.md` (00 → 90) — son las reglas
   de esta revisión, tal como las aplicarías vos mismo.
2. Determiná la rama base: la que te haya pasado el usuario como argumento, o `main` si no
   dio ninguna.
3. Con Bash, juntá el contexto del diff:
   - `git status --short` — archivos tocados.
   - `git log --oneline <base>..HEAD` — commits de la rama.
   - `git diff --stat <base>...HEAD` y `git diff <base>...HEAD` — diff commiteado contra la
     rama base.
   - `git diff` — diff sin commitear (working tree; también va a terminar en el PR).
4. Aplicá las reglas de `docs/review-rules/*.md` a ese diff completo (commiteado + working
   tree). Para `20-edge-cases.md` en particular: si hace falta más contexto del que muestra
   el diff (por ejemplo, qué tests ya existen para la función que se está tocando), abrí
   `tests/` con Read/Grep — no te quedes solo con las líneas cambiadas.
5. **Verificá cada hallazgo contra el repo real antes de reportarlo** (regla de
   `00-context.md`): abrí el archivo con Read y confirmá que el código dice lo que afirmás.
   Descartá o bajá de severidad lo que no puedas confirmar.
6. Imprimí la revisión en el formato de `90-output-format.md`. Es local — no se publica en
   ningún lado automáticamente, no hace falta línea de atribución de pipeline.
