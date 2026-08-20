# ADR-007: Segunda pasada de pre-review dedicada a calidad de código

## Estado
Aceptado

## Contexto
ADR-006 estableció `/pre-review` como una sola pasada con 6 reglas priorizadas
(`docs/review-rules/00` a `90`), donde reuso/simplificación (`40-maintainability.md`)
es prioridad 4 de 6 — detrás de correctitud y casos borde de negocio.

Al comparar contra `pipelines/rules/` de `Cooperativa-Union-Back-Mobile` (el proyecto
del que se portó la mecánica original), se encontró que ese repo **no** resuelve el
riesgo de "una dimensión de menor prioridad queda tapada por las de arriba" agregando
más reglas a una sola pasada: corre **dos** pasadas independientes de `claude -p` en el
mismo pipeline — `pipelines/rules/*.md` (correctitud, seguridad, performance,
mantenibilidad, logging, REST, testing, versionado) y `pipelines/rules-simplify/*.md`
(reuso, simplificación, eficiencia, altitud), esta última una variante de solo-reporte
del skill `/simplify`. El motivo documentado en `pipelines/README-pr-review.md`: en la
pasada principal, mantenibilidad es prioridad 4 de 5 y en la práctica queda tapada; con
una pasada dedicada, sin nada más de qué ocuparse, aparecen hallazgos que la otra no ve
— cita como evidencia una corrida real donde la pasada principal calificó el diseño de
forma generosa mientras la pasada dedicada, sobre el mismo diff, encontró DTOs muertos,
un invariante duplicado y una query que había caído fuera de su índice filtrado.

Verificado además contra hallazgos reales de ese pipeline (capturas de PR de
`Cooperativa-Union-Back-Mobile`): de 6 hallazgos revisados, 5 salían de la pasada
principal (bugs de correctitud, duplicación, testing, versionado) y 1 — un ternario
binario que absorbe silenciosamente valores `null` o categorías futuras como si fueran
el caso más común — salía específicamente de la pasada de calidad
(`rules-simplify/20-simplificacion.md`, "condiciones siempre verdaderas dado el código
que las rodea"), no de una regla de "casos borde" como se supuso inicialmente.

## Decisión
- Se agrega `docs/review-rules-simplify/*.md`, hermana de `docs/review-rules/*.md`,
  adaptada de `pipelines/rules-simplify/` al stack de este proyecto (Python/handlers/
  aiosqlite en vez de .NET/EF Core/MediatR): reuso (`10-reuso.md`), simplificación
  (`20-simplificacion.md`), eficiencia (`30-eficiencia.md`), altitud (`40-altitud.md`),
  con su propio `00-context.md` y `90-output-format.md`.
- `/pre-review` corre ambas pasadas en la misma invocación, cada una con su propio
  conjunto de reglas y su propio informe — no se mezclan ni se re-priorizan entre sí.
  La pasada de calidad tiene la restricción explícita de no reportar bugs de
  correctitud ni casos borde (eso ya lo cubre la pasada 1); duplicarlo generaría ruido.
- A diferencia del pipeline de Back-Mobile (que corre las dos pasadas como jobs de CI
  separados, cada uno posteando su propio comentario de PR), acá ambas corren dentro
  de una sola invocación de `/pre-review` — sigue siendo un chequeo local, no un gate
  de CI (ese alcance no cambia respecto a ADR-006).

## Consecuencias
- `/pre-review` hace más trabajo por corrida (dos análisis en vez de uno), pero sigue
  siendo local y sin costo de facturación — no aplica la limitación de autenticación
  que sí bloquea el gate de CI (ver `docs/backlog.md`, "Pendiente de decidir").
- Si en el futuro se lleva `/pre-review` a CI, la pregunta de si se ejecuta como un
  solo job con las dos pasadas o como dos jobs separados (como hace Back-Mobile, para
  que una falla en la pasada de calidad no bloquee la de correctitud) queda abierta
  para cuando se retome esa decisión — no la resuelve este ADR.
- Cuando aparezca un ángulo de calidad nuevo que hoy no tiene lugar claro (ej. algo
  específico de accesibilidad o UX conversacional del bot), se agrega como archivo
  nuevo en `docs/review-rules-simplify/`, no forzado dentro de uno existente.
