"""Self-check del flujo de /start (ADR-003). Correr: python -m handlers.test_registro

No usa pytest (no está en requirements.txt) — asserts simples sobre
crear_usuario/get_usuario contra una BD SQLite temporal.
"""
import asyncio
import os
import tempfile


async def main() -> None:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DB_PATH"] = path

    # importar después de fijar DB_PATH, porque db.py lo lee al importarse
    from database import db
    from database.models import Usuario

    try:
        await db.init_db()

        assert await db.get_usuario(123) is None, "usuario no debería existir todavía"

        nuevo = Usuario(telegram_id=123, nombre="Carlos", oficio="electricista")
        await db.crear_usuario(nuevo)

        encontrado = await db.get_usuario(123)
        assert encontrado is not None, "usuario debería existir tras crear_usuario"
        assert encontrado.nombre == "Carlos"
        assert encontrado.oficio == "electricista"
        assert encontrado.logo_path is None, "logo_path debe quedar None (ADR-003)"

        print("OK: flujo de registro (crear_usuario + get_usuario)")
    finally:
        os.remove(path)


if __name__ == "__main__":
    asyncio.run(main())
