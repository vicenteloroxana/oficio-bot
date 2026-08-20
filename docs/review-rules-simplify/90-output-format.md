# Formato del mensaje final

Encabezado fijo, para que no se confunda con el review de correctitud/casos borde:

  ## 🧹 Calidad de código — reuso, simplificación, eficiencia y altitud

Después:

- Una línea con el resumen: cuántos hallazgos y si alguno vale la pena resolver antes de abrir
  el PR.
- Los hallazgos **agrupados por mecanismo, no por ángulo**: si dos ángulos señalan el mismo
  defecto, es UN hallazgo con dos consecuencias. Ordenados por costo real, no por severidad
  nominal.
- Cada hallazgo: **archivo:línea**, una frase de qué es, **la forma más simple que hace lo
  mismo**, y el costo concreto hoy (qué se duplica, qué se desperdicia, qué se rompe al
  cambiarlo).
- Una sección corta **«Verificado y descartado»** con lo que se miró y resultó no ser problema.
  Evita que la próxima corrida lo vuelva a levantar.
- Si el diff está limpio, decilo en una línea y no infles el informe.

Recordá: **reportás, no aplicás**. Nada de «lo corregí» — es local, la decisión de aplicar algo
queda para quien está trabajando en el diff.
