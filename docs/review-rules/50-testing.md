# Calidad de tests

Prioridad #5. Preguntá:

- ¿Todo handler o función con lógica no trivial (validación, estado, cálculo) tiene tests en
  el mismo diff? CLAUDE.md no permite postergarlo a un PR aparte.
- ¿Los tests afirman comportamiento real, o son padding de cobertura (asserts triviales, mockear
  tanto que no queda nada real bajo prueba)?
- ¿Cubren el happy path + al menos un caso borde no trivial (ver `20-edge-cases.md`) + una
  violación de regla de negocio (ej. número de trabajo inválido, seña mayor al total)?
- ¿Todo `try/except` nuevo o tocado en un handler (ej. `int()` sobre lo que tipeó el usuario
  en el chat) tiene un test que fuerza esa rama con una entrada inválida real, no solo el
  camino donde el `try` no dispara?
- Para invariantes numéricas o de rango en `database/models.py`
  (ej. `monto_sena <= monto_total`): ¿usa `hypothesis` como pide CLAUDE.md, en vez de listar
  casos sueltos a mano?
- ¿Las dependencias nuevas de testing quedaron en `requirements-dev.txt`, no en
  `requirements.txt`?
