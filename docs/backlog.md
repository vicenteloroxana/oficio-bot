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

- [ ] `handlers/recordatorio.py` — lógica de disparo según `REMINDER_DAYS`
- [ ] Mecanismo de scheduling (job periódico — definir cómo se dispara sin webhook)
- [ ] Botones `[Marcar como pagado]` / `[Ignorar]` (fase 1 — sin `[Reenviar link]`)
- [ ] Registrar cada envío en `recordatorios`

## Momento 3 — Registrar cobro final (`/cobrar`)

- [ ] `handlers/cobro.py` — listar trabajos pendientes, seleccionar, registrar forma de pago
- [ ] Actualizar `estado` a `finalizado` y `cobrado_en`

## Momento 4 — Ver resumen (`/resumen`)

- [ ] Query agregada por mes (cobrado / pendiente / sin seña)
- [ ] Formato de salida según mockup de `CLAUDE.md`

## Momento 5 — Historial de clientes (`/clientes`)

- [ ] `handlers/clientes.py` — listar clientes con totales
- [ ] Detalle por cliente al seleccionar uno

## Momento 6 — Configurar perfil (`/perfil`)

- [ ] Ver perfil actual (nombre, oficio, logo)
- [ ] Editar nombre / oficio
- [ ] Subir logo (validar `MAX_LOGO_SIZE_MB`, guardar local — nunca al repo)

## Pendiente de decidir (no bloquea Fase 1)

- [ ] Mecanismo de scheduling para Momento 2 (no hay definición todavía —
      afecta si corre dentro del mismo proceso o necesita un job separado)
- [ ] Migración de polling a webhooks al deployar en Railway (ver ADR-001)
- [ ] Runtime nativo de WeasyPrint (Pango/Cairo/GObject) en el entorno de
      Railway — CI (Ubuntu) ya lo instala vía `apt-get`, pero no está
      verificado en el contenedor real de deploy. Si Railway usa una imagen
      sin esas libs del sistema, `services/pdf_service.py` va a fallar en
      producción aunque los tests pasen en CI.
- [ ] `assets/logo_default.png` es un placeholder genérico (círculo + silueta,
      generado con Pillow) para no bloquear el Momento 1 — no es un diseño
      final. Revisar/reemplazar cuando se implemente `/perfil` (Momento 6).

## Fase 2 / Fase 3 (fuera de alcance del MVP)

- [ ] Integración Mercado Pago (`services/mp_service.py`, link de pago de seña)
- [ ] Soporte WhatsApp vía Meta Cloud API
