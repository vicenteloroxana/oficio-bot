# ADR-004: Disparo del recordatorio automático (Momento 2)

## Estado
Aceptado

## Contexto
ADR-002 define `estado` en `trabajos` como la fuente de verdad para decidir
cuándo disparar un recordatorio automático, con la máquina de estados
`presupuestado → sena_enviada → sena_cobrada → finalizado`. Pero no
especifica cómo un trabajo llega a `sena_enviada` en fase 1: no hay Mercado
Pago (fase 2) que confirme el envío del link de pago de forma automática, y
`handlers/presupuesto.py` (Momento 1) dejaba todo trabajo en `presupuestado`
al crearlo, aunque tuviera seña. Sin definir esto, el recordatorio nunca
tenía nada que disparar.

También faltaba decidir el mecanismo de scheduling en sí — CLAUDE.md
describe Momento 2 como "sin comando — disparo automático" pero fase 1 corre
en polling, dentro de un solo proceso, sin infraestructura de jobs externa
(ver ADR-001).

## Decisión
- **Transición a `sena_enviada` es manual, no automática al crear el
  trabajo.** Cuando `/presupuesto` termina con `monto_sena > 0`, tras enviar
  el PDF el bot pregunta "¿Ya le mandaste este presupuesto a {cliente}?" con
  botones `[Sí]` / `[Todavía no]`. Solo con `[Sí]` el trabajo pasa a
  `sena_enviada` y arranca a contar `REMINDER_DAYS`. Si la seña es `0`, no se
  pregunta nada y el trabajo nunca dispara recordatorio.
  Se prefirió esto a marcar `sena_enviada` automáticamente al crear el
  trabajo porque en fase 1 "mandar el presupuesto" es un paso manual del
  trabajador (WhatsApp, en persona) que el bot no puede confirmar por sí
  solo — automatizarlo sin confirmación generaría recordatorios sobre
  presupuestos que el cliente ni recibió todavía.
- **Primer uso de botones inline en el repo.** Se implementa con
  `InlineKeyboardButton` + `CallbackQueryHandler` de python-telegram-bot
  (`handlers/recordatorio.py`), tal como ya anticipaba el mockup de Momento
  2 en CLAUDE.md. Este mismo mecanismo se reutiliza para los botones
  `[Marcar como pagado]` / `[Ignorar]` del propio recordatorio.
- **Scheduling con `JobQueue`** (extra `python-telegram-bot[job-queue]`,
  usa APScheduler internamente). Un job periódico (`run_repeating`, cada 1h)
  revisa trabajos en `sena_enviada` con `creado_en` a más de `REMINDER_DAYS`
  días y sin un `Recordatorio` con `respuesta = marcado_pagado`, y les manda
  el aviso. Corre dentro del mismo proceso del bot — no hay job separado ni
  infraestructura de colas.
- El botón `[Ignorar]` no silencia el trabajo: solo excluye por
  `marcado_pagado`, así que un trabajo ignorado vuelve a aparecer en el
  próximo ciclo. Es la lectura literal del mockup de Momento 2
  (los tres botones son una respuesta puntual, no una configuración
  persistente de "no molestar").

## Consecuencias
- `handlers/presupuesto.py` gana un paso conversacional adicional al final
  del flujo (solo si `monto_sena > 0`), documentado en el mockup de Momento
  1 en CLAUDE.md.
- El `JobQueue` corre en el mismo proceso que el polling — si Railway
  reinicia el proceso, el próximo chequeo se retrasa hasta `first=10s`
  después del arranque, pero no se pierden ni duplican recordatorios: el
  estado vive en la tabla `recordatorios`, no en memoria (ver
  `docs/backlog.md`, sección "Pendiente de decidir", para el riesgo abierto
  de reinicios frecuentes).
- Al migrar de polling a webhooks en Railway (ver ADR-001), `JobQueue` sigue
  funcionando igual — no depende del modo de recepción de updates, solo
  necesita que el proceso del bot esté vivo.
- Cuando se implemente Mercado Pago (fase 2), la confirmación manual
  `[Sí]`/`[Todavía no]` probablemente se reemplace por la transición
  automática a `sena_enviada` al generar el link de pago — este ADR queda
  reemplazado en ese momento, no editado.
