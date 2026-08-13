# Template: Servicio (PDF, Mercado Pago, etc)

Usa este template cuando necesites crear una función de servicio (generación de PDFs, APIs externas, lógica compartida).

---

## Template (copia y completa)

```
Rol: Desarrollador Python Senior especializado en [tecnología específica].

Contexto:
Bot de Telegram para trabajadores independientes.
Stack: Python 3.12, [librerías usadas para este servicio].
El bot genera presupuestos en PDF, maneja pagos (fase 2), y recordatorios automáticos.

Tarea:
Escribi la función async [nombre_función] que:
- Input: [parámetros con tipos]
- Output: [qué devuelve con tipo]
- Lógica: [pasos principales]
La función va en: services/[nombre_service].py

Restricciones:
- type hints en TODAS las funciones
- máximo 20 líneas por función
- async/await obligatorio si hace I/O
- docstring en español
- no importar librerías nuevas sin preguntar
- manejo de errores explícito (no silenciar excepciones)
- seguir docs/commit-conventions.md

Formato:
[código Python] → skipped: [qué], add when: [cuándo]
```

---

## Ejemplo completo: Generar PDF con WeasyPrint

```
Rol: Desarrollador Python Senior especializado en generación de PDFs con WeasyPrint.

Contexto:
Bot de Telegram para trabajadores independientes.
Stack: Python 3.12, WeasyPrint, Jinja2 o template HTML simple.
Necesita generar PDFs profesionales de presupuestos.

Tarea:
Escribi la función async generate_presupuesto_pdf que:
- Input: 
  - usuario_nombre: str
  - cliente_nombre: str
  - descripcion: str
  - monto_total: float
  - monto_seña: float
  - usuario_logo_path: str | None (ruta local opcional)
- Output: str (ruta al PDF generado en /pdfs/TIMESTAMP.pdf)
- Lógica:
  1. Carga template de templates/presupuesto.html
  2. Rellena datos (usuario, cliente, monto, seña)
  3. Renderiza con WeasyPrint
  4. Guarda en /pdfs/
  5. Devuelve la ruta

La función va en: services/pdf_service.py

Restricciones:
- type hints obligatorios
- máximo 30 líneas (es compleja pero debe ser legible)
- async para posibles future I/O
- docstring en español explicando qué hace
- manejar excepciones (archivo no encontrado, permisos, etc)
- no agregar dependencias nuevas (ya tenemos WeasyPrint)

Formato:
[código Python] → skipped: [qué no incluiste], add when: [bajo qué condición]
```

---

## Checklist antes de usar el template

- [ ] ¿Qué librería necesita (WeasyPrint, requests, etc)?
- [ ] ¿Ya está en requirements.txt?
- [ ] ¿Es async o sync? (async si hace I/O)
- [ ] ¿Cómo maneja errores?
- [ ] ¿Dónde guarda archivos (BD, filesystem)?
- [ ] ¿Type hints en todos los parámetros y return?
