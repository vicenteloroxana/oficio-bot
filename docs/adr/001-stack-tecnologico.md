# ADR-001: Stack tecnológico

## Estado
Aceptado

## Contexto
Oficio Bot es un bot de Telegram para trabajadores de oficio (concurso CoderCamp IA
de Coderhouse, MVP en 10 días). Necesita: mensajería async con Telegram, generación
de PDFs de presupuesto, persistencia liviana sin infraestructura extra, y deploy
simple con CI/CD automático.

## Decisión
- **Lenguaje**: Python 3.12
- **Bot**: python-telegram-bot en modo async, con webhooks (no polling)
- **PDF**: WeasyPrint (HTML/CSS → PDF) para los presupuestos
- **Base de datos**: SQLite vía aiosqlite (async, sin servidor separado)
- **Pagos**: Mercado Pago SDK Python — diferido a fase 2, no implementado en el MVP
- **Hosting**: Railway, con deploy automático desde GitHub
- **Config**: variables de entorno vía python-dotenv, nunca hardcodeadas

## Consecuencias
- Todo el código de handlers es async/await; no se permite código sync bloqueante
  en los handlers (impacta pdf_service y mp_service, que deben exponer wrappers async).
- SQLite es suficiente para el volumen esperado de un trabajador independiente,
  pero no escala a multi-instancia con escritura concurrente alta; si Railway
  requiere múltiples réplicas, habrá que migrar a Postgres.
- WeasyPrint fija el diseño del PDF a HTML/CSS (`templates/presupuesto.html`),
  lo que facilita mantenimiento pero requiere librerías de sistema (Pango/cairo)
  disponibles en el entorno de Railway.
- Postergar Mercado Pago a fase 2 mantiene el MVP simple: fase 1 entrega
  presupuesto → PDF → registro manual de cobro → recordatorio → resumen,
  sin integración de pagos real.
