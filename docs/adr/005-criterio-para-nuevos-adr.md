# ADR-005: Criterio para decidir si un cambio amerita ADR

## Estado
Aceptado

## Contexto
CLAUDE.md exige que, antes de crear o modificar un ADR, se muestre qué se
detectó y por qué se considera cambio de arquitectura (y no detalle de
implementación), esperando confirmación — incluso cuando la discrepancia se
detecta automáticamente vía `codebase-memory-mcp`. Pero no fija cómo
distinguir una cosa de la otra: la tool `detect_changes` de ese MCP devuelve
todos los archivos y símbolos afectados en un diff, sin clasificarlos por
relevancia arquitectónica — esa clasificación queda 100% a criterio de quien
la interpreta. Sin un criterio explícito, cada decisión se toma ad-hoc y
puede variar entre sesiones o entre quien la aplique.

## Decisión
Un cambio se considera **de arquitectura** (amerita ADR) cuando cumple al
menos una de estas condiciones:
- Contradice o reemplaza una decisión ya registrada en otro ADR.
- Afecta cómo interactúan componentes entre sí (nuevo mecanismo de disparo,
  cambio de base de datos, nuevo protocolo de comunicación) — no solo el
  comportamiento interno de un componente.
- Es una decisión que, si se revierte más adelante, obliga a reconsiderar
  otras partes del sistema — no se puede deshacer con un solo PR aislado.
- Fija un criterio de largo plazo ("hasta que se decida explícitamente lo
  contrario"), no algo que se ajusta iterando sin costo.

Se considera **detalle de implementación** (no amerita ADR) cuando:
- Es una elección dentro del espacio que un ADR existente ya delimitó.
- Se puede cambiar después sin que otra parte del sistema se entere.
- Es el "cómo" de algo cuyo "qué/por qué" ya está decidido.

Este criterio se aplica igual sea la detección manual o vía
`codebase-memory-mcp` (`detect_changes`, que no filtra por relevancia
arquitectónica — devuelve el diff completo sin clasificar). En cualquier
caso, mostrar qué se detectó y por qué se lo considera arquitectura, y
esperar confirmación antes de tocar `docs/adr/`, sigue siendo obligatorio
según CLAUDE.md — este ADR no reemplaza ese paso, solo documenta el criterio
usado para llegar a la conclusión que se muestra.

## Consecuencias
- Casos límite (ej: cambiar el mensaje de un recordatorio vs. cambiar su
  mecanismo de disparo) se resuelven consistentemente citando este ADR, en
  vez de re-derivar el criterio en cada sesión.
- Si el criterio cambia, se reemplaza este ADR por uno nuevo (no se edita),
  siguiendo la misma regla que aplica a cualquier otro ADR del repo.
