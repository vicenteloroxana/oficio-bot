# Ángulo 3 — Eficiencia

Trabajo desperdiciado que el diff introduce:

- cómputo o I/O repetido: la misma fila leída dos veces (`get_trabajo` llamado más de una vez
  para el mismo id en un mismo handler), una query dentro de un loop en vez de una sola query
  agregada
- una consulta en Python filtrando/contando lo que SQLite ya podría filtrar/contar en el
  `WHERE`/`SUM(CASE...)` — ver el precedente de `get_resumen_mensual`, que agrega en SQL en vez
  de traer filas y sumar en Python
- operaciones `async` independientes esperadas en secuencia con `await` cuando podrían ir en
  paralelo con `asyncio.gather` — pero ojo: dos operaciones sobre la **misma conexión**
  `aiosqlite` no se pueden paralelizar de forma segura
- trabajo bloqueante (sync) corriendo en el event loop sin `asyncio.to_thread` — ver el
  precedente de `generar_pdf` en `presupuesto.py`, que corre WeasyPrint (sync) en un thread
  aparte a propósito
- una conexión (`get_connection`) abierta más de una vez para operaciones que podrían compartir
  una sola conexión/transacción

Cuantificá cuando puedas: por request, por fila, por corrida del `JobQueue` de recordatorios.

No marques micro-optimizaciones que no cambian nada en un bot con esta escala de uso (SQLite
local, un solo trabajador por conversación).
