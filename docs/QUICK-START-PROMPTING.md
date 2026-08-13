# Quick Start — Prompting en Oficio Bot

## En 30 segundos

**Cuando necesites un prompt — 2 formas:**

**Forma 1 — Automática (hook):**
1. Mencioná "prompt", "mejorar" o "reglas" en tu mensaje
2. Hook se dispara automáticamente 🚀
3. Yo te hago 5 preguntas interactivas (Rol, Contexto, Tarea, Restricciones, Formato)
4. Genero el prompt mejorado

**Forma 2 — Templates (rápido, sin preguntas):**
1. Abrís `docs/prompts/` → elegís template
2. Completás placeholders → copias → pegas

**Duración:** 2-3 minutos (Forma 1) | 1-2 minutos (Forma 2).

---

## Los 2 caminos

### Camino 1: Hook automático (recomendado)
```
Paso 1: Mencionás "prompt", "mejorar" o "reglas" en tu mensaje
           ↓
Paso 2: Hook detecta automáticamente (sin que hagas nada)
           ↓
Paso 3: Yo te hago 5 preguntas interactivas
           ↓
Paso 4: Obtenés prompt mejorado listo para usar
```
No necesitás hacer nada — solo mencionar la palabra clave. ⚡

### Camino 2: Template (rápido si sabés qué necesitás)
```
1. Abrís docs/prompts/ y elegís:
   - bot-handler-prompt.md → Handler conversacional
   - db-schema-prompt.md → Modelo de BD
   - service-prompt.md → Función de servicio
   - testing-prompt.md → Tests

2. Completás placeholders
3. Copias y pegás
```

### Bonus: Guía completa (si querés aprender)
```
Leo docs/prompt-guide.md
→ entiendo las 5 reglas en detalle
→ puedo armar prompts sin asistencia
```

---

## Las 5 reglas (TL;DR)

| Regla | Qué preguntar | Ejemplo |
|---|---|---|
| **1. Rol** | ¿Quién sos? | "Developer Python Senior especializado en Telegram" |
| **2. Contexto** | ¿Dónde estamos? | "Bot de Telegram, Python 3.12, SQLite, WeasyPrint" |
| **3. Tarea** | ¿Qué necesitás? | "Handler /presupuesto que pregunta cliente, descripción, monto" |
| **4. Restricciones** | ¿Qué límites hay? | "type hints, max 20 líneas, async, Pydantic, español" |
| **5. Formato** | ¿Cómo lo querés? | "[código] → skipped/add when" |

---

## Ejemplo rápido

### Necesitás: Handler `/pendientes`

**Opción 1 — Hook automático (más fácil):**
```
Escribís: "Necesito mejorar el prompt del handler de pendientes"
           ↓
Hook detecta "mejorar" (automático, sin que hagas nada)
           ↓
🚀 Yo te hago las 5 preguntas interactivas
           ↓
Genero el prompt mejorado automáticamente
```

**Opción 2 — Template (rápido):**
```
1. Abrís docs/prompts/bot-handler-prompt.md
2. Completás [COMANDO] = "/pendientes"
3. Completás los steps conversacionales
4. Copias y pegás en Claude
```

**Resultado en ambos casos:** mismo prompt excelente, distinto camino.

### Cuál elegir

| Situación | Elegí |
|---|---|
| "Tengo un prompt vago y menciono 'mejorar'" | Opción 1 (hook automático) |
| "Sé exactamente qué necesito, no quiero preguntas" | Opción 2 (template) |
| "Quiero entender las reglas en detalle" | Leo `prompt-guide.md` |

---

## Checklist antes de usar un prompt

- [ ] ¿Rol es específico o es genérico?
- [ ] ¿Contexto incluye stack y problema?
- [ ] ¿Tarea es específica o hay que adivinar?
- [ ] ¿Incluye restricciones de oficio-bot?
- [ ] ¿Formato es claro?

Si algo falta → el prompt no va a funcionar bien.

---

## Restricciones siempre (copiar/pegar)

```
Restricciones:
- type hints en TODAS las funciones
- máximo 20 líneas por función
- async/await obligatorio
- Pydantic para validación
- docstrings en español
- no importar librerías nuevas
- seguir docs/commit-conventions.md
```

---

## Después de usar el prompt

1. ✅ Validá que el código sigue las restricciones
2. 💾 Si el prompt funcionó bien, guardalo (es reutilizable)
3. 🚀 Commitea siguiendo Conventional Commits
4. 🔀 Abre PR (si necesitás feedback)

---

## Antipatrones — qué evitar

❌ **Prompt vago:**
```
"Haceme un presupuesto"
```

✅ **Prompt específico:**
```
Handler async /presupuesto que pregunta cliente, descripción, monto.
Devuelve dict validado. Va en handlers/presupuesto.py
```

---

## Más info

- `docs/prompt-guide.md` — Guía completa con ejemplos
- `docs/prompts/README.md` — Índice de templates
- `docs/branch-conventions.md` — Cómo nombrar ramas
- `docs/commit-conventions.md` — Cómo escribir commits

---

## El atajo mental

Cada vez que escribas un prompt, pregúntate:

> **¿Mi prompt tiene los 5 elementos?**
> 1. Rol ✅?
> 2. Contexto ✅?
> 3. Tarea ✅?
> 4. Restricciones ✅?
> 5. Formato ✅?

Si falta uno → agregalo.

Si todos están → pegá y ejecutá.

---

## Dudas frecuentes

### P: ¿Siempre necesito los 5 elementos?
**R:** Sí. Son requisitos, no opcionales.

### P: ¿Puedo saltarme el Formato?
**R:** No. Formato ambiguo = respuesta ambigua.

### P: ¿Dónde guardo los prompts que funcionan?
**R:** En un ADR o en memory. Son reutilizables.

### P: ¿Qué pasa si mi prompt falla?
**R:** Probablemente falta un elemento o es muy vago. Revisá el checklist.

### P: ¿Puedo personalizar las restricciones?
**R:** Sí, pero nunca quites: type hints, async, Pydantic, español.

### P: ¿El hook se activa automáticamente o tengo que hacer algo?
**R:** Automático. Solo mencioná "prompt", "mejorar" o "reglas" en tu mensaje y el hook se dispara sin que hagas nada.

### P: ¿Qué pasa cuando se dispara el hook?
**R:** El hook me sugiere que se activó Prompt Builder. Yo automáticamente te hago las 5 preguntas interactivas. No necesitás hacer nada más.

### P: ¿Puedo desactivar el hook?
**R:** Sí, en `.claude/settings.json` (proyecto). Pero está pensado para ayudarte, generalmente no molesta.

### P: ¿Qué pasa si no quiero que se dispare el hook?
**R:** Usá directamente un template de `docs/prompts/` sin mencionar las palabras clave.
