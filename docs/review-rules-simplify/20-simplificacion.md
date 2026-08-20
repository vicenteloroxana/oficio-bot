# Ángulo 2 — Simplificación

Complejidad innecesaria que el diff **agrega**:

- estado redundante o derivable: un campo que se calcula de otros, o dos que hay que mantener
  sincronizados a mano (ej. un total que se podría calcular en vez de guardarse aparte)
- copy-paste con variación mínima: la misma forma de validar/preguntar/responder escrita dos
  veces con diferencias chicas entre handlers
- anidamiento que una guarda o un `return`/`continue` temprano aplanan (CLAUDE.md ya limita a
  3 niveles — este ángulo va más allá del conteo mecánico: ¿se *siente* enredado aunque cumpla
  el límite?)
- código muerto que quedó atrás: import sin usar, función privada sin llamar, campo de un
  modelo Pydantic que nadie lee, rama de `if` que ya no puede dispararse
- sobre-abstracción: una clase/función para un solo caso de uso, un parámetro de configuración
  para un valor que nunca cambia, un `try/except` especulativo para algo que no puede pasar en
  este flujo
- chequeos de `None`/vacío redundantes, o condiciones siempre verdaderas dado el código que las
  rodea (ej. un `if x is None` después de un `assert x is not None`, o un ternario/`if-else`
  binario que en la práctica solo puede tomar un valor)

Nombrá **la forma más simple que hace lo mismo**.

No marques los docstrings en español por largos: CLAUDE.md pide explícitamente docstrings de
negocio en español — es intencional, no ruido.
