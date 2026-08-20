# Formato del mensaje final

- Un encabezado corto con el veredicto general.
- Lista de hallazgos con emoji de severidad: 🔴 Crítico/Alta, 🟠 Media, 🟡 Baja, más una nota
  corta de lo que está bien.
- Cada hallazgo: **severidad**, **archivo:línea (aprox) o símbolo**, una frase de descripción,
  la corrección concreta, y una cita del código ofensor en bloque de código.
- Los hallazgos de `20-edge-cases.md` (casos borde) van marcados con la categoría
  **[caso borde]** además del emoji de severidad, para diferenciarlos de bugs directos.
- Si no hay hallazgos, decilo explícitamente — no inventes uno para tener algo que mostrar.
- Es un pre-check local, no un comentario de PR: no hace falta línea de atribución de pipeline.
