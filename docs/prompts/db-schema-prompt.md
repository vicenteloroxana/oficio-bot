# Template: Modelo de Base de Datos

Usa este template cuando necesites crear o modificar tablas, modelos Pydantic o queries.

---

## Template (copia y completa)

```
Rol: Arquitecto de bases de datos con experiencia en SQLite async.

Contexto:
Bot de Telegram que gestiona trabajos, clientes y cobros.
Stack: SQLite, aio-sqlite para async, Python 3.12, Pydantic para validación.
Restricción: no usar migraciones complejas, evolucionar el esquema manualmente.

Tarea:
Define el modelo Pydantic para [nombre_tabla].
Campos a incluir: [campo1 (tipo, validación)], [campo2 (tipo, validación)], ...
El modelo va en: database/models.py
Devuelve: clase Pydantic con type hints, validaciones y docstring.

Restricciones:
- type hints en TODAS las funciones
- Validaciones de negocio en el modelo (montos > 0, estados válidos, etc)
- docstrings en español
- no usar relaciones complejas, solo FK simples
- seguir docs/commit-conventions.md

Formato:
[código Pydantic] → explicación breve de validaciones
```

---

## Ejemplo completo: Tabla `trabajos`

```
Rol: Arquitecto de bases de datos con experiencia en SQLite async.

Contexto:
Bot de Telegram que gestiona trabajos de trabajadores independientes.
Stack: SQLite, aio-sqlite, Python 3.12.
Necesita almacenar: trabajos, clientes, presupuestos, cobros.

Tarea:
Define el modelo Pydantic para la tabla trabajos.
Campos:
- id: autoincremental
- usuario_id: FK a usuarios.telegram_id
- cliente_nombre: string
- descripcion: texto
- monto_total: float, debe ser > 0
- monto_seña: float, debe ser >= 0 y <= monto_total
- estado: enum de 5 valores válidos (presupuestado, sena_enviada, sena_cobrada, finalizado, cancelado)
- pdf_path: string opcional (ruta al PDF)
- creado_en: datetime
- cobrado_en: datetime nullable

El modelo va en: database/models.py

Restricciones:
- type hints obligatorios
- Validaciones de negocio en el modelo (monto_seña <= monto_total)
- docstring en español
- usar datetime.datetime para fechas
- no usar relaciones ORM complejas

Formato:
[código Pydantic completo]
Validaciones incluidas: [lista de validaciones]
```

---

## Checklist antes de usar el template

- [ ] ¿Qué campos necesita la tabla?
- [ ] ¿Cuáles son FK y cuáles constraints?
- [ ] ¿Qué validaciones de negocio tiene (montos, rangos, enums)?
- [ ] ¿Nullable o not null? (decidir por campo)
- [ ] ¿Hay índices o búsquedas frecuentes en esa tabla?
