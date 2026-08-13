# ADR-003: Registro de usuario en /start

## Estado
Aceptado

## Contexto
`trabajos.usuario_id` tiene FK a `usuarios.telegram_id` (ver ADR-002). Si un
usuario ejecuta `/presupuesto` sin haber sido registrado antes, la inserción
del trabajo fallaría por integridad referencial. `CLAUDE.md` ya designa
`/start` como "Bienvenida y configuración inicial del perfil" en la tabla de
comandos, pero no especificaba el diálogo — se definió recién (ver Momento 0
en CLAUDE.md) y queda documentado acá el cómo se implementa.

## Decisión
- `/start` registra al usuario con el mínimo indispensable para desbloquear
  `/presupuesto`: `nombre` y `oficio`. `logo_path` queda `None` y se completa
  después vía `/perfil` — no se pide en el primer contacto.
- Es un flujo conversacional de 2 pasos (nombre → oficio), implementado con
  `ConversationHandler` de python-telegram-bot (estados: `ESPERANDO_NOMBRE`,
  `ESPERANDO_OFICIO`), mismo mecanismo que van a necesitar `/presupuesto` y
  `/cobrar` para sus propios flujos multi-paso.
- Si `/start` se ejecuta con un `telegram_id` ya presente en `usuarios`, no
  repite las preguntas — responde con un saludo corto y sigue.
- `/presupuesto` NO hace auto-registro silencioso: si se ejecuta sin que el
  usuario exista en `usuarios`, responde pidiendo `/start` primero, en vez de
  crear un usuario a medias por atrás sin que el trabajador lo sepa.

## Consecuencias
- `/presupuesto`, `/cobrar` y cualquier handler que inserte en `trabajos`
  puede asumir que `usuario_id` existe — no necesitan revalidar la FK a mano,
  pero si se implementan antes de `/start` en la práctica, hay que probarlos
  con un usuario ya insertado manualmente en la BD.
- El campo `oficio` en `Usuario` es `str` libre (no enum, ver `database/models.py`),
  así que `/start` no valida contra una lista cerrada — cualquier texto no
  vacío es válido. Si en el futuro se quiere restringir a una lista, es un
  cambio de validación en el handler, no en el modelo.
- El patrón `ConversationHandler` con estados que arranca acá se replica en
  `/presupuesto` (Momento 1) — mantenerlo consistente entre handlers evita
  reinventar el manejo de estado conversacional en cada uno.
