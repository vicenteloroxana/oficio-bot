# Revisión local pre-PR — dos pasadas independientes

Revisá los cambios de esta rama **antes** de abrir el PR, con dos conjuntos de reglas separados
(ver `docs/adr/006-pre-review-casos-borde.md` para el porqué de este mecanismo, y
`docs/adr/007-segunda-pasada-calidad.md` para el porqué de las dos pasadas). Es un pre-check
local — no reemplaza el pipeline de CI.

## Por qué dos pasadas y no una lista más larga

En una sola pasada, mantenibilidad/simplificación es prioridad 4 de 6 — detrás de correctitud y
casos borde — y en la práctica queda tapada. Una pasada dedicada, sin nada más de qué ocuparse,
encuentra cosas que la otra no ve. Mismo motivo por el que
`Cooperativa-Union-Back-Mobile` separa `pipelines/rules/` de `pipelines/rules-simplify/`.

## Pasos

1. Juntá el contexto del diff una sola vez (se usa en ambas pasadas):
   - Determiná la rama base: la que te haya pasado el usuario como argumento, o `main` si no
     dio ninguna.
   - `git status --short` — archivos tocados.
   - `git log --oneline <base>..HEAD` — commits de la rama.
   - `git diff --stat <base>...HEAD` y `git diff <base>...HEAD` — diff commiteado contra la
     rama base.
   - `git diff` — diff sin commitear (working tree; también va a terminar en el PR).

2. **Pasada 1 — correctitud, casos borde, reglas de negocio, testing, git.** Leé, en orden,
   todos los archivos `docs/review-rules/*.md` (00 → 90). Para `20-edge-cases.md` en particular:
   si hace falta más contexto del que muestra el diff (qué tests ya existen para la función que
   se está tocando), abrí `tests/` con Read/Grep — no te quedes solo con las líneas cambiadas.
   Aplicá las reglas al diff completo (commiteado + working tree) y armá el informe en el
   formato de `docs/review-rules/90-output-format.md`.

3. **Pasada 2 — calidad (reuso, simplificación, eficiencia, altitud).** Leé, en orden, todos los
   archivos `docs/review-rules-simplify/*.md` (00 → 90). Es una pasada independiente de la 1:
   no repitas ahí bugs de correctitud ni casos borde, esta pasada es solo sobre diseño y
   duplicación. Armá el informe en el formato de `docs/review-rules-simplify/90-output-format.md`.

4. **Verificá cada hallazgo de ambas pasadas contra el repo real antes de reportarlo** (regla
   compartida por los dos `00-context.md`): abrí el archivo con Read y confirmá que el código
   dice lo que afirmás. Descartá o bajá de severidad lo que no puedas confirmar.

5. Mostrá los dos informes uno debajo del otro, cada uno con su propio encabezado (el de la
   pasada 1 según `docs/review-rules/90-output-format.md`, el de la pasada 2 con el encabezado
   fijo `## 🧹 Calidad de código...` de `docs/review-rules-simplify/90-output-format.md`). Es
   local — no se publica en ningún lado automáticamente, no hace falta línea de atribución de
   pipeline.

6. **¿Alguno de los hallazgos de arriba expone un patrón que ninguna regla actual cubre?**
   Aplicá la prueba de `docs/review-rules/20-edge-cases.md` ("Cuándo un hallazgo nuevo se
   agrega como punto nuevo acá") a cada hallazgo 🟠/🔴 de ambas pasadas: si el mismo bug, en un
   handler completamente distinto con variables completamente distintas, seguiría descrito tal
   cual por la redacción que propondrías, es candidato a regla nueva. La mayoría de las veces
   la respuesta es que ya lo cubre un punto existente — en ese caso no digas nada más, seguí de
   largo. Si encontrás un candidato genuino, proponé el texto exacto y en qué archivo iría
   (`docs/review-rules/20-edge-cases.md` si es de negocio/aplicativo,
   `docs/review-rules-simplify/*.md` si es de diseño/calidad) y esperá confirmación antes de
   escribirlo — no lo agregues solo, igual que no se toca un ADR sin mostrar antes qué se
   detectó y por qué (CLAUDE.md, regla de ADRs).
