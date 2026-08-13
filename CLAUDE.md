# Oficio Bot — Asistente de gestión para trabajadores independientes

## Lo que hace este proyecto
Bot de Telegram para trabajadores de oficio (plomeros, electricistas, pintores,
profesores particulares, etc.) que permite gestionar presupuestos, registrar cobros
y enviar recordatorios automáticos de pago — sin salir de Telegram.

Flujo principal: el trabajador describe el trabajo → el bot genera un PDF de
presupuesto profesional → el trabajador acuerda una seña con el cliente →
el bot genera link de pago de la seña (Mercado Pago, fase 2) → envía
recordatorios automáticos si no pagan → registra el cobro final.

## Stack
- Lenguaje: Python 3.12
- Bot: python-telegram-bot (async, webhooks)
- PDF: WeasyPrint (HTML/CSS → PDF)
- Pagos: Mercado Pago SDK Python (fase 2, no implementar aún)
- Base de datos: SQLite (aiosqlite para async)
- Hosting: Railway (deploy automático desde GitHub)
- Variables de entorno: python-dotenv

## Estructura de carpetas — RESPETAR SIEMPRE
```
oficio-bot/
├── CLAUDE.md
├── README.md
├── .gitignore              ← nunca subir .env ni archivos de BD
├── .env.example            ← plantilla de variables sin valores reales
├── requirements.txt
├── main.py                 ← arranque del bot
├── docs/
│   ├── branch-conventions.md     ← estándar Conventional Branch v1.1.0
│   └── commit-conventions.md     ← Conventional Commits
├── handlers/
│   ├── __init__.py
│   ├── presupuesto.py      ← flujo conversacional de nuevo presupuesto
│   ├── cobro.py            ← registro de cobros y cierre de trabajos
│   ├── recordatorio.py     ← recordatorios automáticos de mora
│   ├── clientes.py         ← historial de clientes y trabajos por cliente
│   └── perfil.py           ← configuración del trabajador (nombre, logo)
├── services/
│   ├── __init__.py
│   ├── pdf_service.py      ← generación del PDF con WeasyPrint
│   └── mp_service.py       ← integración Mercado Pago (fase 2)
├── database/
│   ├── __init__.py
│   ├── db.py               ← inicialización y conexión SQLite
│   └── models.py           ← definición de tablas
├── templates/
│   └── presupuesto.html    ← diseño del PDF en HTML/CSS
└── assets/
    └── logo_default.png    ← logo genérico cuando el usuario no tiene uno
```

## Modelo de datos — tablas SQLite

### usuarios
| campo | tipo | descripción |
|---|---|---|
| telegram_id | INTEGER PK | ID único del usuario en Telegram |
| nombre | TEXT | Nombre o razón social del trabajador |
| oficio | TEXT | Plomero, electricista, etc. |
| logo_path | TEXT | Ruta local al logo subido (opcional) |
| creado_en | DATETIME | Fecha de registro |

### trabajos
| campo | tipo | descripción |
|---|---|---|
| id | INTEGER PK | ID autoincremental |
| usuario_id | INTEGER FK | Referencia a usuarios.telegram_id |
| cliente_nombre | TEXT | Nombre del cliente |
| descripcion | TEXT | Descripción del trabajo |
| monto_total | REAL | Monto total acordado |
| monto_sena | REAL | Seña acordada (puede ser 0) |
| estado | TEXT | presupuestado / sena_enviada / sena_cobrada / finalizado / cancelado |
| pdf_path | TEXT | Ruta al PDF generado |
| creado_en | DATETIME | Fecha de creación |
| cobrado_en | DATETIME | Fecha de cobro final (null si pendiente) |

### recordatorios
| campo | tipo | descripción |
|---|---|---|
| id | INTEGER PK | ID autoincremental |
| trabajo_id | INTEGER FK | Referencia a trabajos.id |
| enviado_en | DATETIME | Fecha en que se envió el recordatorio |
| respuesta | TEXT | ignorado / reenviar / marcado_pagado |

## Comandos del bot
| Comando | Función |
|---|---|
| `/start` | Bienvenida y configuración inicial del perfil |
| `/presupuesto` | Inicia flujo para crear nuevo presupuesto |
| `/cobrar` | Registra cobro de un trabajo existente |
| `/pendientes` | Lista trabajos sin cobrar |
| `/resumen` | Resumen del mes actual |
| `/clientes` | Historial de clientes y trabajos por cliente |
| `/perfil` | Ver o editar datos del trabajador (nombre, logo) |

## Flujos conversacionales — los 4 momentos del bot

### Momento 1 — Crear presupuesto (`/presupuesto`)
```
Trabajador: /presupuesto

Bot: ¿Para quién es el trabajo?

Trabajador: Juan López

Bot: ¿Qué trabajo vas a hacer?

Trabajador: Pintura de living y cocina, incluye materiales

Bot: ¿Cuánto vas a cobrar?

Trabajador: 180000

Bot: ¿Pedís seña? Si sí, ¿cuánto?

Trabajador: Sí, 50%

Bot: ✅ Listo. Generando presupuesto...

     📄 [PDF adjunto]

     Cliente: Juan López
     Trabajo: Pintura de living y cocina con materiales
     Total:   $180.000
     Seña:    $90.000
     Validez: 7 días

     ¿Querés que le mande el link de pago de la seña?

Trabajador: Sí

Bot: 🔗 Link de pago Mercado Pago:
     https://mpago.la/xxxxx

     Mandáselo a Juan y cuando pague te aviso automáticamente.
```
> Nota: el link de Mercado Pago es fase 2. En fase 1 el bot confirma
> el presupuesto y el PDF, pero no genera el link de pago.

---

### Momento 2 — Recordatorio automático (sin comando — disparo automático)
```
[N días después de emitido el presupuesto, si la seña no fue marcada como pagada]

Bot: ⏰ Juan López todavía no pagó
     la seña del trabajo de pintura.

     ¿Qué hacemos?

     [Reenviar link]  [Marcar como pagado]  [Ignorar]
```
> Los botones se implementan como InlineKeyboardButton de Telegram.
> "Reenviar link" solo disponible en fase 2 (Mercado Pago).
> En fase 1 mostrar solo [Marcar como pagado] e [Ignorar].

---

### Momento 3 — Registrar cobro final (`/cobrar`)
```
Trabajador: /cobrar

Bot: ¿Qué trabajo cerrás?

     1. Juan López — Pintura living (pendiente)
     2. María García — Electricidad (pendiente)

Trabajador: 1

Bot: El trabajo con Juan tenía seña de $90.000 pagada.
     Resta: $90.000

     ¿Cómo cobraste el resto?

     [Efectivo]  [Transferencia]  [MP]

Trabajador: Transferencia

Bot: ✅ Trabajo cerrado.
     Juan López — Pintura living
     Total cobrado: $180.000 💰
```

---

### Momento 4 — Ver resumen (`/resumen`)
```
Trabajador: /resumen

Bot: 📊 Tu resumen — Agosto 2026

     ✅ Cobrado:    $360.000 (4 trabajos)
     ⏳ Pendiente:  $180.000 (2 trabajos)
     ❌ Sin seña:   1 trabajo (López)

     Trabajos este mes: 6
```

---

### Momento 5 — Historial de clientes (`/clientes`)
```
Trabajador: /clientes

Bot: 👥 Tus clientes

     1. Juan López — 3 trabajos — $450.000 cobrado
     2. María García — 1 trabajo — pendiente de cobro
     3. Carlos Díaz — 2 trabajos — $220.000 cobrado

     ¿Querés ver el detalle de alguno?

Trabajador: 1

Bot: 📋 Juan López
     ─────────────────────
     ✅ Pintura living     $180.000  ago 2026
     ✅ Pintura habitación $150.000  jul 2026
     ⏳ Electricidad       $120.000  pendiente
     ─────────────────────
     Total cobrado: $330.000
     Total pendiente: $120.000
```

---

### Momento 6 — Configurar perfil (`/perfil`)
```
Trabajador: /perfil

Bot: 👤 Tu perfil actual:
     Nombre: Carlos Rodríguez
     Oficio: Electricista
     Logo:   No configurado (se usará tu nombre en el PDF)

     ¿Qué querés cambiar?

     [Nombre]  [Oficio]  [Subir logo]

Trabajador: [Subir logo]

Bot: Enviame la imagen de tu logo
     (PNG o JPG, máximo 2MB)

Trabajador: [imagen adjunta]

Bot: ✅ Logo guardado. Aparecerá en
     todos tus próximos presupuestos.
```

## Reglas de desarrollo — SIEMPRE respetar

### Antes de escribir código
- Si el requerimiento es ambiguo o tiene más de una interpretación: PREGUNTAR antes de actuar
- Nunca asumir en silencio — informar el supuesto si hay un default obvio

### Git
- Nunca commitear directo a `main`
- Todo cambio va por rama + PR
- Antes de escribir el primer archivo de un cambio: crear la rama, según
  `docs/branch-conventions.md` (estándar Conventional Branch v1.1.0).
  Formato `<tipo>/<descripción-en-minúsculas-con-guiones>`.
  Tipos de rama válidos (conjunto cerrado): `feature`/`feat`,
  `bugfix`/`fix`, `hotfix`, `release`, `chore`.
  OJO: `docs`, `refactor`, `test`, `ci` son tipos de COMMIT pero NO de
  rama — esos cambios van en `chore/`. Ej: rama `chore/adr-iniciales`
  con commits `docs(constitution): ...`.
- Flujo: crear rama → commitear → push de la rama → abrir PR → merge.
  Con 0 aprobaciones requeridas, el PR se puede mergear sin esperar a
  nadie, pero el PR es obligatorio: es el registro de qué entró y por qué.
- Mensajes de commit según `docs/commit-conventions.md`
  (Conventional Commits).
- Si por error ya hay cambios sin commitear sobre `main`: crear la rama
  primero y commitear ahí — nunca commitear en `main` "y después mover".

### Python
- Type hints en todas las funciones
- Pydantic para validación de inputs del bot
- `async/await` siempre — nunca código sync en handlers
- Docstrings en español para funciones de negocio
- Máximo 20 líneas por función — extraer si supera
- No más de 3 niveles de anidación

### Seguridad
- API keys y tokens NUNCA en código — siempre desde variables de entorno
- El archivo `.env` NUNCA se sube al repo (ya está en `.gitignore`)
- CUIT/CUIL de usuarios se guarda solo si el usuario lo ingresa voluntariamente
- Logos subidos por usuarios se guardan localmente, nunca en el repo

### NO tocar sin preguntar
- `database/models.py` — cambios en el esquema afectan datos existentes
- `templates/presupuesto.html` — cambios afectan todos los PDFs generados
- Cualquier archivo de configuración de Railway

## Variables de entorno necesarias
```
# Bot
TELEGRAM_BOT_TOKEN=        # Token del bot — BotFather de Telegram

# Mercado Pago (fase 2 — no implementar aún)
# MP_ACCESS_TOKEN=

# Configuración
REMINDER_DAYS=3            # Días antes de enviar recordatorio automático
MAX_LOGO_SIZE_MB=2         # Tamaño máximo de logo en MB
```

## Fases del proyecto
- **Fase 1 (MVP — 10 días):** presupuesto → PDF → registro de cobro → recordatorio → resumen mensual
- **Fase 2 (post-concurso):** integración Mercado Pago para link de pago de seña
- **Fase 3 (post-concurso):** soporte WhatsApp vía Meta Cloud API

## Contexto del proyecto
Este bot fue diseñado para el concurso CoderCamp IA de Coderhouse.
El criterio de evaluación prioriza impacto real sobre complejidad técnica.
El público objetivo son trabajadores informales argentinos que hoy gestionan
todo por WhatsApp y cuaderno — sin herramientas digitales de gestión.