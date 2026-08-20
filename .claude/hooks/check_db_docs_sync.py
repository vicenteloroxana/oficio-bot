"""Hook PostToolUse: recuerda revisar CLAUDE.md al tocar el schema de la BD.

Se dispara cuando Edit/Write toca database/db.py o database/models.py.
No corrige nada solo -- solo inyecta un recordatorio para que Claude
compare contra la tabla "Modelo de datos" de CLAUDE.md y avise al
usuario si quedo desincronizada (regla de "preguntar ante ambiguedad").
"""
import json
import sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "").replace("\\", "/")

if path.endswith("database/db.py") or path.endswith("database/models.py"):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "Recordatorio: tocaste database/db.py o database/models.py. "
                "Antes de dar el cambio por terminado, compara el schema/modelo "
                "con la tabla 'Modelo de datos' de CLAUDE.md. Si esta "
                "desincronizada, avisale al usuario que la doc quedo "
                "desactualizada y preguntale si la actualizas (CLAUDE.md es la "
                "especificacion estable del proyecto, no se edita en silencio)."
            ),
        }
    }))
