# Template: Handler de Bot

Usa este template cuando necesites crear un nuevo comando o handler conversacional.

---

## Template (copia y completa)

```
Rol: Desarrollador Python Senior especializado en bots de Telegram async.

Contexto:
Bot de Telegram para trabajadores independientes (plomeros, electricistas, etc).
Stack: Python 3.12, python-telegram-bot (async), Pydantic, SQLite async.
El bot genera presupuestos en PDF, registra cobros y envía recordatorios automáticos.

Tarea:
Escribi el handler async para el comando [COMANDO] que:
1. [Paso 1 conversacional]
2. [Paso 2 conversacional]
3. [Paso 3 conversacional]
Devuelve: [qué devuelve al completarse]
El handler va en: handlers/[nombre].py

Restricciones:
- type hints en TODAS las funciones
- máximo 20 líneas por función (extraer si supera)
- async/await obligatorio
- Pydantic para validación de inputs
- docstrings en español para funciones de negocio
- no importar librerías nuevas sin preguntar
- seguir docs/commit-conventions.md

Formato:
[código Python] → skipped: [qué], add when: [cuándo]
```

---

## Ejemplo completo: Handler `/presupuesto`

```
Rol: Desarrollador Python Senior especializado en bots de Telegram async.

Contexto:
Bot de Telegram para trabajadores independientes.
Stack: Python 3.12, python-telegram-bot (async), Pydantic, SQLite async.
Necesita generar presupuestos profesionales en PDF.

Tarea:
Escribi el handler async para /presupuesto que:
1. Pregunta "¿Para quién es el trabajo?" → guarda cliente_nombre
2. Pregunta "¿Qué trabajo vas a hacer?" → guarda descripción
3. Pregunta "¿Cuánto vas a cobrar?" → valida que sea float > 0
4. Pregunta "¿Pedís seña? Si sí, ¿cuánto?" → valida que sea <= monto_total
Devuelve: dict con {cliente_nombre, descripción, monto_total, monto_seña}
El handler va en: handlers/presupuesto.py

Restricciones:
- type hints en TODAS las funciones
- máximo 20 líneas por función
- async/await obligatorio
- Pydantic para validación
- docstrings en español
- no importar librerías nuevas
- seguir docs/commit-conventions.md

Formato:
[código Python] → skipped: [qué], add when: [cuándo]
```

---

## Checklist antes de usar el template

- [ ] ¿El comando ya existe o es nuevo?
- [ ] ¿Sabés los pasos conversacionales?
- [ ] ¿Qué datos necesitás validar y cómo?
- [ ] ¿Dónde se guardan esos datos (BD, memoria)?
- [ ] ¿Hay excepciones o flujos alternativos?
