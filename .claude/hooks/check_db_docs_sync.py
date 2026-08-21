"""Hook PostToolUse: recuerda revisar CLAUDE.md al tocar BD o comandos/handlers.

Se dispara cuando Edit/Write toca:
- database/db.py o database/models.py -> tabla "Modelo de datos"
- handlers/*.py o main.py            -> tabla "Comandos del bot" y "Momentos"

No corrige nada solo -- solo inyecta un recordatorio para que Claude
compare contra CLAUDE.md y avise al usuario si quedo desincronizada
(regla de "preguntar ante ambiguedad").
"""
import json
import sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "").replace("\\", "/")

if path.endswith("database/db.py") or path.endswith("database/models.py"):
    mensaje = (
        "Recordatorio: tocaste database/db.py o database/models.py. "
        "Antes de dar el cambio por terminado, compara el schema/modelo "
        "con la tabla 'Modelo de datos' de CLAUDE.md. Si esta "
        "desincronizada, avisale al usuario que la doc quedo "
        "desactualizada y preguntale si la actualizas (CLAUDE.md es la "
        "especificacion estable del proyecto, no se edita en silencio)."
    )
elif path.endswith("main.py") or ("/handlers/" in f"/{path}" and path.endswith(".py")):
    mensaje = (
        "Recordatorio: tocaste un handler o main.py. Si agregaste/cambiaste "
        "un comando nuevo o un paso de un flujo conversacional, compara contra "
        "las tablas 'Comandos del bot' y los diálogos de 'Flujos "
        "conversacionales' de CLAUDE.md. Si esta desincronizada, avisale al "
        "usuario que la doc quedo desactualizada y preguntale si la "
        "actualizas (CLAUDE.md es la especificacion estable del proyecto, "
        "no se edita en silencio)."
    )
else:
    mensaje = None

if mensaje:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": mensaje,
        }
    }))
