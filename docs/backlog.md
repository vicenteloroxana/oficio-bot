# Backlog — Oficio Bot

Estado de avance del MVP (Fase 1). Complementa `CLAUDE.md`: ahí está el
*qué* (comandos, diálogos, modelo de datos); acá el *estado* (hecho /
pendiente) y el orden de construcción.

Convención: `[x]` hecho y mergeado en `main`, `[ ]` pendiente. Al terminar
un ítem, marcalo en el mismo PR que lo implementa — no en un commit aparte.

---

## Base técnica

- [x] Estructura de carpetas (`handlers/`, `services/`, `database/`, `templates/`, `assets/`)
- [x] `requirements.txt`
- [x] `database/models.py` — modelos Pydantic (Usuario, Trabajo, Recordatorio)
- [x] `database/db.py` — schema SQLite + conexión async
- [x] `main.py` — arranque en polling, `post_init` corre `init_db()`
- [x] `.env.example`
- [x] ADRs (001 stack, 002 modelo de datos, 003 registro de usuario)
- [x] CI (`.github/workflows/tests.yml`) — pytest en cada PR contra `main`, bloquea merge si falla
- [x] `tests/` — pytest + pytest-asyncio (unitarios) y hypothesis (property-based
      para invariantes numéricas, ej. `monto_sena <= monto_total`)
- [x] `tests/test_dispatch.py` — test de integración sobre `Application` real
      (bot mockeado, sin red) para cobertura arquitectural: detecta comandos/
      mensajes sin ningún handler que los atienda, y que el fallback global no
      le robe mensajes a un `ConversationHandler` con estado activo. Los tests
      unitarios existentes (por función de handler) no pueden detectar la
      *ausencia* de un handler ni el orden de dispatch — origen: un comando
      desconocido y un texto libre fuera de flujo quedaban en silencio total
      sin que ningún test lo marcara.

## Momento 0 — Primer contacto (`/start`)

- [x] Diálogo documentado (`CLAUDE.md`)
- [x] Decisión técnica documentada (ADR-003: `ConversationHandler`, registro mínimo)
- [x] `handlers/registro.py` — `ConversationHandler` de 2 pasos (nombre → oficio),
      persiste en `usuarios`, registrado en `main.py`
- [x] Manejar el caso "usuario ya registrado" sin repetir preguntas
- [x] `/cancel` como fallback del `ConversationHandler`
- [x] Tests (`tests/test_registro.py`)

## Momento 1 — Crear presupuesto (`/presupuesto`)

- [x] `handlers/presupuesto.py` — flujo conversacional (cliente → descripción → monto → seña)
- [x] Validar que el usuario exista en `usuarios` (pedir `/start` si no — ver ADR-003)
- [x] Insertar el `Trabajo` en la BD con estado `presupuestado`
- [x] `templates/presupuesto.html` — diseño del PDF (⚠️ no tocar sin preguntar, CLAUDE.md)
- [x] `services/pdf_service.py` — generación del PDF con WeasyPrint
- [x] Enviar el PDF generado al chat
- [x] Confirmar alcance de fase 1 vs. fase 2 (sin link de Mercado Pago todavía — CLAUDE.md ya lo documenta, no se implementó)

## Momento 2 — Recordatorio automático (sin comando)

- [x] `handlers/recordatorio.py` — lógica de disparo según `REMINDER_DAYS`
- [x] Mecanismo de scheduling (`JobQueue` de python-telegram-bot, `run_repeating`
      cada 1h — ver "Pendiente de decidir" abajo)
- [x] Botones `[Marcar como pagado]` / `[Ignorar]` (fase 1 — sin `[Reenviar link]`)
- [x] Registrar cada envío en `recordatorios`
- [x] Paso nuevo en `/presupuesto` (Momento 1): con seña > 0, tras mandar el PDF
      pregunta "¿Ya le mandaste este presupuesto a {cliente}?" — recién ahí el
      trabajo pasa a `sena_enviada` y arranca a contar `REMINDER_DAYS`. Sin esta
      confirmación no hay disparo (decisión explícita: no basta con crear el
      trabajo, fase 1 no tiene Mercado Pago que confirme el envío solo).

## Momento 3 — Registrar cobro final (`/cobrar`)

- [x] `handlers/cobro.py` — listar trabajos pendientes, seleccionar, registrar forma de pago
- [x] Actualizar `estado` a `finalizado` y `cobrado_en`
- [x] Columna `forma_pago` en `trabajos` (no existía en el schema original — agregada
      para persistir el botón elegido, ver "Pendiente de decidir" abajo)

## Momento 4 — Ver resumen (`/resumen`)

- [x] `handlers/resumen.py` — comando directo, sin flujo conversacional
- [x] `database.get_resumen_mensual` — query agregada por mes (cobrado / pendiente / sin seña)
- [x] Formato de salida según mockup de `CLAUDE.md`

## Estado `cancelado` — presupuesto rechazado por el cliente

- [x] `RespuestaRecordatorio.CLIENTE_NO_ACEPTO` (`database/models.py`) y
      `marcar_cancelado` (`database/db.py`), compartida por los dos puntos
      de entrada de abajo — pasa el trabajo a `estado = cancelado`
- [x] Botón `[Cliente no aceptó]` en el recordatorio automático (Momento 2)
- [x] `/pendientes`: mismo botón por cada trabajo listado, para cancelar
      antes de que dispare el recordatorio automático
- [x] `/resumen` y `/clientes` excluyen `cancelado` de sus agregados
      (visible en el detalle de `/clientes`, sin sumar a los totales)
- [x] Tests (`tests/test_recordatorio.py`, `tests/test_pendientes.py`)

## Momento 5 — Trabajos pendientes de cobro (`/pendientes`)

- [x] `handlers/pendientes.py` — lista trabajos sin cobrar del todo,
      reusa `get_trabajos_pendientes` (ya usada por `/cobrar`)
- [x] Botón `[Cliente no aceptó]` por trabajo (ver sección de arriba)
- [x] Tests (`tests/test_pendientes.py`)

## Momento 6 — Historial de clientes (`/clientes`)

- [x] `handlers/clientes.py` — listar clientes con agregado (cantidad de
      trabajos, monto cobrado, si tiene algo pendiente)
- [x] Detalle por cliente al seleccionar uno (`get_trabajos_de_cliente`,
      incluye cancelados sin sumarlos a los totales)
- [x] `get_clientes_resumen` excluye de la lista principal los clientes
      cuyo único trabajo fue cancelado
- [x] Tests (`tests/test_clientes.py`)

## Momento 7 — Configurar perfil (`/perfil`)

- [x] Ver perfil actual (nombre, oficio, logo) — `handlers/perfil.py`
- [x] Editar nombre / oficio — `database.actualizar_usuario`
- [x] Subir logo (validar `MAX_LOGO_SIZE_MB`, guardar en `assets/logos/`,
      nunca al repo — ya estaba en `.gitignore`) — `database.guardar_logo_path`
- [x] Tests (`tests/test_perfil.py`)

## Pendiente de decidir (no bloquea Fase 1)

- [ ] Gate de CI para `/pre-review` (ADR-006, `docs/review-rules/*.md`) —
      decidido el alcance (solo `20-edge-cases.md`, bloqueante si hay 🔴),
      pero bloqueado por **autenticación**: correr `claude -p` en un runner
      de GitHub Actions necesita `ANTHROPIC_API_KEY` (API de pago por uso,
      cuenta de facturación separada de la suscripción de Claude Code) o el
      `claude-code-action` oficial con OAuth de la suscripción (si el plan
      lo soporta — no confirmado). La suscripción de Claude Code sola NO
      alcanza para invocación no interactiva en CI. Retomar cuando esté
      resuelto el tema de costo/acceso. Hasta entonces, `/pre-review` sigue
      siendo chequeo local manual (gratis, corre en la sesión de Claude
      Code), no bloquea Fase 1.
- [x] Mecanismo de scheduling para Momento 2 — resuelto: `JobQueue` de
      python-telegram-bot (extra `job-queue`, corre dentro del mismo proceso
      del bot, sin job separado). Revisar si escala mal al migrar a webhooks
      en Railway (ver ítem siguiente) o si Railway reinicia el proceso seguido
      — `run_repeating` no persiste su estado entre reinicios, así que un
      reinicio no duplica recordatorios (se re-arma desde `recordatorios` en
      BD) pero sí puede demorar el próximo chequeo hasta `first=10s` después
      del arranque.
- [x] Migración de polling a webhooks al deployar en Railway (ver ADR-001):
      `main.py` elige el modo solo según `RAILWAY_PUBLIC_DOMAIN`
      (inyectada por Railway al generar dominio público) — sin variable
      manual que setear. También condicionaba Mercado Pago en Fase 2
      (ver abajo), que sigue sin implementar.
- [x] Runtime nativo de WeasyPrint (Pango/Cairo/GObject) en el entorno de
      Railway, para Momento 1 (`services/pdf_service.py`): confirmado en
      producción que Nixpacks (builder por default de Railway) no expone
      esas libs en runtime aunque se declaren como `nixPkgs` explícitos
      (`OSError: cannot load library 'libgobject-2.0-0'` persistía).
      Resuelto migrando el build a un `Dockerfile` propio con
      `apt-get install` de las libs, siguiendo la guía oficial de
      instalación de WeasyPrint para Debian/Ubuntu — mismo enfoque que
      ya usaba CI (Ubuntu) para instalarlas, ahora también en producción.
- [ ] `assets/logo_default.png` quedó huérfano en el repo: se decidió que
      si el usuario no tiene logo, el PDF simplemente no muestra imagen en
      el header (en vez del placeholder genérico círculo + silueta que
      mostraba antes). El archivo sigue en `assets/` por si se retoma un
      logo por defecto más adelante — evaluar si borrarlo o darle uso real.
- [x] Reintento automático de PDF cuando falla en `/presupuesto`: si
      `generar_pdf` explota (ver ítem de WeasyPrint/Railway arriba), se
      reintenta hasta `MAX_INTENTOS_PDF` (3) veces con una espera corta
      entre intentos. El `Trabajo` ya está guardado antes del PDF, así que
      nunca se pierde. Si se agotan los intentos, se marca `pdf_error = 1`
      en el trabajo (columna nueva, ver CLAUDE.md) y se avisa al usuario.
- [x] Regeneración manual del PDF para un trabajo con `pdf_error = 1`:
      resuelto con `/reintentar_pdf` (`handlers/reintentar_pdf.py`) — lista
      los trabajos con `pdf_error = 1` del usuario, reintenta sobre el
      `trabajo_id` existente (reusa `_generar_y_adjuntar_pdf` de
      `presupuesto.py`) y limpia la marca si tiene éxito. No crea un
      `Trabajo` nuevo — evita el duplicado que generaría correr
      `/presupuesto` de nuevo con los mismos datos.

## Fase 2 / Fase 3 (fuera de alcance del MVP)

- [ ] Integración Mercado Pago (`services/mp_service.py`, link de pago de seña).
      Requisitos a resolver cuando se aborde:
      - SDK gratuito (`mercadopago` en PyPI); el costo real es la comisión
        por transacción que cobra Mercado Pago, no la API en sí — confirmar
        % vigente en Argentina antes de presupuestar esto en la propuesta.
      - Cuenta de Mercado Pago (definir si es la del trabajador o una
        cuenta recaudadora central — decisión de producto, no técnica).
      - `MP_ACCESS_TOKEN` (ya placeholder en `.env.example`) + credenciales
        de sandbox para probar antes de producción.
      - Notificación de pago vía webhook/IPN de Mercado Pago requiere un
        endpoint HTTP público — depende de resolver primero la migración
        de polling a webhooks (ver "Pendiente de decidir" arriba).
- [ ] Soporte WhatsApp vía Meta Cloud API
