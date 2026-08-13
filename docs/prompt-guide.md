# Guía de Prompting — Las 5 Reglas

> Cuando escribas un prompt para la IA, seguí estas 5 reglas. Pueden ser tediosas
> al principio; después de algunos prompts, se vuelven reflex.

## Las 5 reglas

### 1. Rol (¿Quién sos?)
Define el nivel de experiencia y especialidad que querés que asuma la IA.

**Por qué:** La IA adapta su lenguaje, profundidad y enfoque según el rol. Un "senior developer" da respuestas distintas a un "junior".

**Ejemplos:**
- ✅ "Actuá como un desarrollador backend Senior especializado en ciberseguridad"
- ✅ "Sos un arquitecto de sistemas con 15 años de experiencia en APIs REST"
- ❌ "Ayudame" ← demasiado vago

**En el contexto de oficio-bot:**
- "Sos un desarrollador Python especializado en bots de Telegram"
- "Actuá como un DevOps con experiencia en Railway y SQLite"

---

### 2. Contexto (¿Dónde estamos?)
Explica de qué trata el proyecto, tecnologías, y cuál es el problema general.

**Por qué:** La IA necesita entender el ecosistema para dar respuestas relevantes. Sin contexto, adivina.

**Estructura del contexto:**
- Descripción breve del proyecto
- Tecnologías usadas
- Cuál es el problema general o desafío
- Restricciones o estándares del proyecto

**Ejemplos:**
- ✅ "Estoy construyendo un bot de Telegram para trabajadores independientes. Stack: Python 3.12, python-telegram-bot (async), WeasyPrint para PDFs, SQLite. El bot genera presupuestos en PDF y maneja cobros."
- ❌ "Tengo un proyecto" ← demasiado vago

**En oficio-bot:**
```
Contexto: Bot de Telegram para trabajadores de oficio (plomeros, electricistas, etc).
Stack: Python 3.12, python-telegram-bot async, WeasyPrint, SQLite async, pydantic.
Problema: Los trabajadores independientes hoy manejan todo por WhatsApp y cuaderno.
Restricciones: type hints en todas las funciones, max 20 líneas por función,
async/await siempre, sin código sync en handlers.
```

---

### 3. Tarea exacta (¿Qué necesitás?)
Sé específico. En lugar de "hazme un sistema", pide algo concreto.

**Por qué:** "Hazme un sistema" genera respuestas genéricas. Específico = exacto.

**Estructura de la tarea:**
- Qué es lo que hay que hacer (en imperativo)
- Cuál es la entrada/input
- Cuál es la salida/output esperada
- Contexto de dónde encaja en el flujo

**Ejemplos:**
- ✅ "Escribi un handler que reciba el comando `/presupuesto` y pregunte conversacionalmente: cliente, descripción, monto. Devuelve un dict con esos 3 datos."
- ✅ "Generá un modelo Pydantic para validar un presupuesto: cliente_nombre (str), descripción (str), monto_total (float positivo), monto_seña (float, 0-100% del total)."
- ❌ "Haceme un presupuesto" ← demasiado vago

**En oficio-bot:**
```
Tarea: Escribir la función async que genera el PDF del presupuesto.
Input: dict con {cliente_nombre, descripción, monto_total, monto_seña, usuario_nombre}.
Output: ruta local al archivo PDF creado en /pdfs.
Restricciones: usar WeasyPrint, template HTML en templates/presupuesto.html,
máximo 30 líneas, type hints obligatorios.
```

---

### 4. Restricciones o Reglas (¿Qué límites hay?)
Indica convenciones, estándares, y límites.

**Por qué:** Sin límites, la IA puede sobre-ingeniería o ignorar tus estándares. Los límites son tu "constitution" para el código.

**Qué incluir:**
- Convenciones de código (naming, max líneas, indentación)
- Estándares del proyecto (type hints, docstrings, async/await)
- Patrones que ya usás
- Qué NO hacer
- Límites de complejidad

**Ejemplos:**
- ✅ "Restricciones: type hints en todas las funciones, máximo 20 líneas, docstrings en español, async/await siempre, Pydantic para validación. No importar librerías nuevas."
- ✅ "Sigue el árbol de decisión de commit-conventions.md. Los tipos de rama válidos son: feature, bugfix, hotfix, release, chore."
- ❌ "Hazlo bien" ← demasiado subjetivo

**En oficio-bot:**
```
Restricciones:
- Type hints en TODAS las funciones
- Máximo 20 líneas por función (extraer si supera)
- async/await obligatorio en handlers
- Pydantic para validación de inputs
- Docstrings en español para funciones de negocio
- No agregar librerías nuevas sin preguntar
- Seguir Conventional Commits (docs/commit-conventions.md)
```

---

### 5. Formato de salida (¿Cómo lo querés recibir?)
Cómo querés que te presente la información.

**Por qué:** Mismo contenido, distinto formato = distinta usabilidad. Si necesitás código ejecutable, código tirado sin explicación es mejor.

**Opciones comunes:**
- Solo código, sin explicación
- Código + comentarios inline
- Código + explicación después
- Estructura paso a paso
- Checklist o tabla
- Resumen ejecutivo + detalles

**Ejemplos:**
- ✅ "Devuélveme solo el bloque de código, sin explicaciones previas ni introducciones."
- ✅ "Quiero: [código] → explicación breve de qué skipeaste → cuándo agregarlo después."
- ✅ "Formato: tabla con funciones a crear, sus inputs, outputs, y por qué van en ese módulo."
- ❌ "Explicame todo" ← demasiado genérico

**En oficio-bot:**
```
Formato: 
[código Python limpio]
→ skipped: [qué no incluiste]
→ add when: [bajo qué condiciones lo incluirías]
```

---

## Checklist antes de usar un prompt

Antes de pegarlo en la IA, validá:

- [ ] **Rol:** ¿definiste nivel y especialidad?
- [ ] **Contexto:** ¿la IA entiende el proyecto y el problema?
- [ ] **Tarea:** ¿es específica o hay que adivinar?
- [ ] **Restricciones:** ¿le dijiste qué NO hacer y qué límites hay?
- [ ] **Formato:** ¿sabe cómo devolverte la respuesta?

Si falta alguno de estos 5 → el prompt va a fallar.

---

## Ejemplos completos

### Ejemplo 1 — Handler de presupuesto
```
Rol: Sos un desarrollador Python Senior especializado en bots de Telegram.

Contexto: 
Bot de Telegram para trabajadores de oficio. Stack: Python 3.12, 
python-telegram-bot (async), Pydantic para validación.
Problema: generar presupuestos profesionales desde Telegram.

Tarea:
Escribi el handler async para /presupuesto que:
1. Pregunta conversacionalmente al usuario: cliente, descripción, monto
2. Valida los datos (monto debe ser float > 0)
3. Devuelve un dict con esos 3 datos validados
El handler va en handlers/presupuesto.py

Restricciones:
- type hints en todas las funciones
- máximo 20 líneas por función
- Pydantic para validación
- async/await obligatorio
- Docstring en español

Formato:
[código] → skipped: [qué], add when: [cuándo]
```

### Ejemplo 2 — Modelo de datos
```
Rol: Sos un arquitecto de bases de datos con experiencia en SQLite.

Contexto:
Bot de Telegram que gestiona trabajos, clientes y cobros.
Stack: SQLite, aio-sqlite para async, Python 3.12.
La BD guarda usuarios, trabajos, recordatorios de pago.

Tarea:
Define el modelo Pydantic para la tabla "trabajos".
Campos: id, usuario_id, cliente_nombre, descripcion, monto_total, 
monto_seña, estado, pdf_path, creado_en, cobrado_en.
Devuelve: clase Pydantic con validaciones apropiadas.

Restricciones:
- Type hints obligatorios
- Validar: monto_total > 0, monto_seña <= monto_total
- Estados válidos solo: presupuestado, sena_enviada, sena_cobrada, 
  finalizado, cancelado
- Usar datetime.datetime para fechas

Formato:
[código Pydantic limpio] → explicación breve
```

---

## Antipatrones — qué evitar

### ❌ Prompt vago
```
"Haceme un bot que cobre trabajos"
```
→ Resultado: código genérico, inútil.

### ❌ Prompt sin contexto
```
"¿Cómo valido un monto?"
```
→ Resultado: respuesta teórica, no adaptada a tu proyecto.

### ❌ Prompt sin restricciones
```
"Escribi un PDF con los datos de un trabajo"
```
→ Resultado: código que ignora tus estándares (type hints, max líneas, async).

### ❌ Prompt sin formato claro
```
"Ayudame a mejorar esta función"
```
→ Resultado: párrafos de explicación cuando necesitás código.

### ✅ Lo que SÍ funciona
```
Rol: Senior Python developer.
Contexto: Telegram bot, WeasyPrint PDFs, trabajadores independientes.
Tarea: Función async para generar PDF de presupuesto desde template HTML.
Input: {cliente, descripción, monto}. Output: ruta al PDF.
Restricciones: type hints, max 20 líneas, async/await, no librerías nuevas.
Formato: [código] → skipped: [X], add when: [Y].
```

---

## Cuándo usar esta guía

Cada vez que escribas un prompt para cualquier herramienta de IA:
- Claude
- ChatGPT
- Copilot
- Cursor
- Cualquier LLM

Copia el template de abajo y adaptalo:

```markdown
Rol: [especialidad + nivel de experiencia]

Contexto: 
[descripción del proyecto]
[stack/tecnologías]
[problema que resuelve]

Tarea:
[qué hay que hacer, específico]
[entrada/output esperado]

Restricciones:
[convenciones de código]
[estándares del proyecto]
[límites de complejidad]
[qué NO hacer]

Formato:
[cómo querés recibir la respuesta]
```

Los prompts bien estructurados no solo ahorran tiempo — dan mejores respuestas.
