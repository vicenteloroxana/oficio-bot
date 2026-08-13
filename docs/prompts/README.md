# Prompts Templates — Oficio Bot

Carpeta con templates pre-armados para distintos escenarios de desarrollo.

## Cómo usarlos

1. **Lee** `../prompt-guide.md` para entender las 5 reglas
2. **Elige** el template que necesites según lo que vas a hacer
3. **Copia y completa** con tus datos específicos
4. **Ejecuta** en Claude/ChatGPT/Cursor
5. **Valida** con el checklist del template

## Templates disponibles

| Template | Cuándo usarlo | Output típico |
|---|---|---|
| **bot-handler-prompt.md** | Comando nuevo, flujo conversacional | Función async, handler de Telegram |
| **db-schema-prompt.md** | Tabla nueva, modelo de datos | Clase Pydantic con validaciones |
| **service-prompt.md** | Generación de PDF, APIs externas, lógica compartida | Función async de servicio |
| **testing-prompt.md** | Tests unitarios, tests de integración | Suite de tests con pytest |

---

## Flujo recomendado

```
Necesito [X feature]
    ↓
¿Qué tipo es? → handler / BD / servicio / test
    ↓
Abrí el template correspondiente
    ↓
Completé los campos [COMANDO] o [nombre_tabla] etc
    ↓
Copié al prompt y ejecuté
    ↓
Validé el checklist
    ↓
Listo
```

---

## Ejemplos rápidos

### "Necesito un comando `/pendientes` que liste trabajos sin cobrar"
→ Usa: `bot-handler-prompt.md`

### "Necesito crear la tabla recordatorios"
→ Usa: `db-schema-prompt.md`

### "Necesito una función que envíe recordatorios automáticos"
→ Usa: `service-prompt.md`

### "Necesito tests para el validador de montos"
→ Usa: `testing-prompt.md`

---

## Restricciones siempre (oficio-bot)

En TODOS los prompts, asegúrate de incluir:

```
Restricciones:
- type hints en TODAS las funciones
- máximo 20 líneas por función
- async/await obligatorio (handlers + I/O)
- Pydantic para validación
- docstrings en español
- no importar librerías nuevas sin preguntar
- seguir docs/commit-conventions.md
```

---

## Próximo paso

Cuando tengas un prompt mejorado con estas reglas, **guardá el prompt** en un ADR o en memory para futuros usos. Los buenos prompts son reutilizables.

Ejemplo de buen prompt reutilizable:
```markdown
# Prompt: Handler de Presupuesto

[el prompt completo que funcionó bien]

Versión: 1.0
Última validación: 2026-08-13
Resultado esperado: handler `/presupuesto` que pregunta cliente, descripción, monto
```
