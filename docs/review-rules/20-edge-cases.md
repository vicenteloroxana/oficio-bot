# Casos borde de negocio y aplicativos

Prioridad #2. Esta regla no da una lista cerrada de casos a buscar — la lista se queda vieja
apenas aparece una función nueva. En cambio, para **cada función de negocio nueva o tocada en
el diff** (handlers en `handlers/`, queries agregadas o de estado en `database/db.py`,
validaciones en `database/models.py`), respondé estas preguntas:

1. **¿De qué variables depende el resultado de esta función?** Pensá en el código real, no en
   lo que el mockup de CLAUDE.md describe como el camino feliz. Candidatas típicas (ninguna es
   obligatoria, ninguna lista agota las posibles):
   - Estado actual de una entidad (`EstadoTrabajo`, `RespuestaRecordatorio`) combinado con
     tiempo (`creado_en`, `cobrado_en`, `enviado_en`, `REMINDER_DAYS`) — el ejemplo que motivó
     esta regla: una query de `/resumen` que filtraba pendientes por `creado_en` del mes dejaba
     afuera un trabajo cuyo cambio de estado ocurrió en el mes siguiente a su creación.
   - Presencia/ausencia de datos opcionales (`monto_sena = 0`, `logo_path = None`,
     `pdf_path` sin generar todavía).
   - Valores límite en montos o cantidades (`monto_total` exactamente igual a `monto_sena`,
     cero trabajos para un usuario, un solo trabajo).
   - Orden de eventos (¿qué pasa si `/cobrar` corre antes de que se haya marcado `sena_enviada`?
     ¿si un recordatorio se dispara sobre un trabajo que se canceló mientras tanto?).
   - Reentrancia o repetición (¿qué pasa si el mismo botón inline se toca dos veces, o si
     `/start` corre con el usuario ya registrado?).

2. **¿Los tests del diff cruzan esas variables entre sí, o solo las prueban una por una?** Un
   test que mueve `creado_en` a otro mes y otro que separado marca `estado = sena_enviada` no
   prueba qué pasa cuando **ambas cosas ocurren en momentos distintos** — la combinación es el
   caso real que se escapa. Marcá 🟠/🔴 cuando el diff prueba los ejes aislados pero no una
   combinación no trivial de al menos dos.

3. **¿Existe una combinación de esas variables donde el dato se "pierde"** — no aparece en
   ninguna categoría, lista o resumen donde debería aparecer en alguna — **o se cuenta dos
   veces** en categorías que deberían ser mutuamente excluyentes? Esto es más grave que un
   cálculo mal hecho: el usuario ni se entera de que faltó algo.

4. **Si la función tiene una rama condicional nueva (`if`/`match`/filtro SQL nuevo), ¿hay al
   menos un test que fuerce esa rama con una combinación que no sea la más obvia?**

5. **Recurso referenciado por id que puede no existir cuando el código lo busca.** Un callback
   de botón inline (`callback_data=f"...:{trabajo_id}"`) o un handler que recibe un id llevan
   ese id como texto/número desconectado del objeto real — el trabajo pudo cancelarse,
   finalizarse o (en teoría) no existir entre que el botón se mostró y que se tocó. Si el diff
   agrega un `get_trabajo(id)` o similar que puede devolver `None`, ¿hay un test que fuerce el
   caso `None` y confirme que el handler no accede a un atributo sobre él (`trabajo.algo` sin
   chequear antes)? Precedente ya corregido en `cobro.py` (`recibir_forma_pago` chequea
   `trabajo is None` con mensaje "esta selección ya expiró"); precedente **sin** cubrir en
   `recordatorio.py` (`responder_recordatorio` hace `trabajo = await get_trabajo(trabajo_id)` y
   accede a `trabajo.cliente_nombre` sin chequear `None` — un recordatorio viejo tocado después
   de que el trabajo se borre o cambie de estado rompe con `AttributeError`).

No hace falta enumerar exhaustivamente cada combinación matemáticamente posible — el criterio
es si el diff cubre al menos una combinación no trivial (dos o más variables moviéndose juntas)
por cada función de negocio nueva, y si el caso "el dato desaparece" fue considerado
explícitamente aunque el test no lo cubra todavía.
