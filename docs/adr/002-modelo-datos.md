# ADR-002: Modelo de datos y ciclo de vida del trabajo

## Estado
Aceptado

## Contexto
El bot necesita registrar trabajadores, los trabajos que presupuestan/cobran, y el
historial de recordatorios de pago enviados — todo en SQLite, con un esquema simple
que un solo trabajador independiente pueda entender sin capa de administración.

## Decisión
Tres tablas (ver `database/models.py`):

- **usuarios**: `telegram_id` (PK) como identidad única, datos de perfil
  (nombre, oficio, logo opcional).
- **trabajos**: referencia a `usuarios.telegram_id`, guarda cliente, descripción,
  montos (total y seña) y un campo `estado` como máquina de estados simple:
  `presupuestado → sena_enviada → sena_cobrada → finalizado` (o `cancelado`).
- **recordatorios**: referencia a `trabajos.id`, registra cada envío automático
  y la respuesta del trabajador (`ignorado / reenviar / marcado_pagado`).

El PDF generado se referencia por ruta (`pdf_path`) en vez de guardarse en la DB.

## Consecuencias
- El campo `estado` en `trabajos` es la fuente de verdad para decidir cuándo
  disparar un recordatorio automático (`REMINDER_DAYS`) — cualquier lógica de
  recordatorio debe leer este campo, no inferir estado de otra parte.
- Cambios de esquema en `database/models.py` requieren migración manual de datos
  existentes (no hay ORM con migraciones automáticas) — por eso CLAUDE.md marca
  ese archivo como "no tocar sin preguntar".
- `pdf_path` y `logo_path` son locales al filesystem del servidor; en Railway
  esto implica almacenamiento efímero salvo volumen persistente — riesgo a
  revisar si el deploy no usa un volumen montado.
- La integración de Mercado Pago (fase 2) no está modelada aún: cuando se
  implemente, probablemente sume una tabla o campos para IDs de pago externos
  y estado de webhook, sin romper el `estado` actual de `trabajos`.
