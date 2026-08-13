# Template: Tests

Usa este template cuando necesites escribir tests unitarios o de integración.

---

## Template (copia y completa)

```
Rol: Desarrollador Python Senior especializado en testing (pytest).

Contexto:
Bot de Telegram para trabajadores independientes.
Stack: Python 3.12, pytest, async/await en handlers, SQLite.
Necesita tests para funciones críticas (validación, generación de PDF, cobros).

Tarea:
Escribi tests para [función_a_testear].
Casos a cubrir:
- [caso 1]: [input] → [output esperado]
- [caso 2]: [input] → [output esperado]
- [caso 3 error]: [input inválido] → [excepción esperada]

Los tests van en: tests/test_[módulo].py

Restricciones:
- type hints en todas las funciones
- usar pytest fixtures para setup/teardown
- docstring en español para cada test
- tests sin frameworks pesados (solo pytest)
- no crear BD real, usar mocks/fixtures
- seguir docs/commit-conventions.md

Formato:
[código Python de tests] → skipped: [qué], add when: [cuándo]
```

---

## Ejemplo completo: Tests para validación de monto

```
Rol: Desarrollador Python Senior especializado en testing con pytest.

Contexto:
Bot de Telegram, validación de montos (presupuestos, señas).
Stack: Python 3.12, pytest, Pydantic.

Tarea:
Escribi tests para la función validar_monto(monto: float) que:
- Devuelve True si monto > 0
- Levanta ValueError si monto <= 0
- Levanta ValueError si monto es None

Casos a cubrir:
- caso 1: validar_monto(100.5) → True
- caso 2: validar_monto(0) → ValueError
- caso 3: validar_monto(-50) → ValueError
- caso 4: validar_monto(None) → ValueError

Los tests van en: tests/test_validations.py

Restricciones:
- type hints en todas las funciones
- usar pytest.raises() para excepciones
- docstring en español
- no crear BD real
- un assert por test (claridad)

Formato:
[código de tests]
Casos cubiertos: [lista]
```

---

## Ejemplo: Tests para handler async

```
Rol: Desarrollador Python Senior especializado en testing de bots async.

Contexto:
Bot de Telegram async, handlers que usan python-telegram-bot.
Stack: Python 3.12, pytest-asyncio, pytest.

Tarea:
Escribi tests para el handler presupuesto_handler que:
- Recibe un update de Telegram
- Pregunta cliente, descripción, monto
- Devuelve dict validado

Casos a cubrir:
- caso 1: usuario responde correctamente → devuelve dict
- caso 2: usuario ingresa monto inválido → pide nuevamente
- caso 3: usuario cancela (/cancel) → retorna None

Los tests van en: tests/test_handlers.py

Restricciones:
- type hints obligatorios
- usar @pytest.mark.asyncio para tests async
- mockear la conexión a Telegram (no hacer request real)
- mockear BD (no usar DB real)
- docstring en español

Formato:
[código de tests async]
Mocks usados: [lista]
```

---

## Checklist antes de usar el template

- [ ] ¿Qué casos de uso válidos hay?
- [ ] ¿Qué errores pueden ocurrir?
- [ ] ¿Necesita async o es sync?
- [ ] ¿Qué fixtures necesita (BD, archivos, mocks)?
- [ ] ¿Hay dependencias externas a mockear?
