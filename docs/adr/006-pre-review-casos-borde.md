# ADR-006: Reglas versionadas de pre-review para detectar casos borde de negocio

## Estado
Aceptado

## Contexto
Al implementar `/resumen` (Momento 4), la query agregada filtraba pendiente
y sin-seña por `creado_en` del mes consultado. Eso dejaba un caso sin
cubrir: un trabajo presupuestado en un mes cuya seña se envía recién al mes
siguiente desaparecía de *ambos* resúmenes — ni contaba como pendiente en el
mes de creación (ya había cambiado de estado) ni en el mes de la transición
(filtrado por `creado_en`, no por cuándo cambió el estado). El caso surgió
de una pregunta de mientras se revisaba manualmente el diseño, no de un
review estructurado ni de un test que lo hubiera atrapado antes.

El equipo no tenía, hasta ahora, ningún mecanismo — automático o de
checklist — para preguntarse sistemáticamente "¿qué combinaciones de estado,
tiempo, datos opcionales u orden de eventos puede tomar esta función, y las
cubren los tests?" antes de dar un Momento por terminado. Sin eso, la
detección de casos borde depende de que a alguien se le ocurra preguntarlo
en esa sesión puntual — no escala ni es repetible.

Un proyecto hermano (`Cooperativa-Union-Back-Mobile`) ya resuelve un
problema relacionado — review de PR consistente — con reglas de revisión
versionadas en `pipelines/rules/*.md`, concatenadas en orden y pasadas como
prompt fijo a `claude -p`. La mecánica (reglas por archivo, una dimensión de
revisión cada una, un comando que las aplica sobre un diff) es reusable; el
contenido no lo es — está armado para IDOR/EF Core/MediatR de un backend
.NET, no para los "Momentos" de negocio de este bot.

## Decisión
- Se adopta la misma mecánica: reglas de revisión en archivos markdown
  versionados dentro del repo (`docs/review-rules/*.md`, prefijo numérico
  para orden de concatenación), y un comando (`/pre-review`) que las junta
  y las aplica sobre el diff de la rama actual contra `main` — un pre-check
  local antes de abrir el PR, no un gate de CI (ver "Consecuencias").
- Entre esas reglas se agrega una explícitamente dedicada a **detección de
  casos borde de negocio y aplicativos**, deliberadamente genérica: no
  enumera una lista fija de ejes ("estado × fecha" es un ejemplo, no la
  regla completa). Le pide al revisor identificar, para cada función de
  negocio tocada en el diff, de qué variables depende su resultado
  (estado actual, orden de eventos en el tiempo, presencia/ausencia de
  datos opcionales, valores límite en montos o cantidades, concurrencia) y
  verificar si los tests cruzan esas variables entre sí — no solo cada una
  aislada. Se prefiere esto a una lista fija de casos porque una lista
  memoriza los ejes que ya conocemos (como estado × fecha, descubierto
  recién); una función de negocio nueva puede depender de ejes que hoy no
  existen en el bot.
- Las demás reglas portadas (`10-correctness.md`, `40-testing.md`,
  `99-output-format.md` del repo hermano) se adaptan al stack de este
  proyecto (Python/async/pytest/Pydantic en vez de .NET/EF/MediatR) y se
  recortan las que no aplican (IDOR de cuentas bancarias, convenciones REST
  — este bot no expone una API HTTP).

## Consecuencias
- `/pre-review` es un chequeo local, no bloqueante: lo corre quien abre el
  PR, antes de abrirlo. No reemplaza el pipeline de CI (`pytest`, con
  branch protection real) ni lo complementa automáticamente — si más
  adelante se decide que corra también en CI, es una decisión nueva
  (posible ADR de seguimiento o extensión de este), no algo que este ADR
  ya habilita.
- La regla de casos borde depende de que quien la aplique (hoy, Claude vía
  `/pre-review`) razone caso por caso — no hay lista cerrada que
  "garantice" cobertura. Es una mejora de proceso, no una prueba formal.
- Cuando se agregue una regla nueva (ej. una dimensión de seguridad si el
  bot alguna vez expone webhooks públicos — ver ADR-001), se agrega como
  archivo nuevo en `docs/review-rules/`, no editando uno existente para que
  cubra algo distinto de lo que su nombre indica.
