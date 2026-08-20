"""Inicialización y conexión a la base de datos SQLite.

Usa aiosqlite directamente (sin ORM) — los modelos Pydantic en
models.py validan los datos antes de que lleguen acá.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aiosqlite

from database.models import EstadoTrabajo, Recordatorio, RespuestaRecordatorio, Trabajo, Usuario

DB_PATH = os.getenv("DB_PATH", "oficio_bot.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    telegram_id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    oficio TEXT NOT NULL,
    logo_path TEXT,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trabajos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(telegram_id),
    cliente_nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    monto_total REAL NOT NULL,
    monto_sena REAL NOT NULL DEFAULT 0,
    estado TEXT NOT NULL DEFAULT 'presupuestado',
    pdf_path TEXT,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cobrado_en DATETIME
);

CREATE TABLE IF NOT EXISTS recordatorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trabajo_id INTEGER NOT NULL REFERENCES trabajos(id),
    enviado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    respuesta TEXT
);
"""


async def init_db(db_path: str = DB_PATH) -> None:
    """Crea las tablas si no existen. Se llama al arrancar el bot."""
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()


@asynccontextmanager
async def get_connection(db_path: str = DB_PATH) -> AsyncIterator[aiosqlite.Connection]:
    """Provee una conexión a la BD para usar con 'async with'.

    Configura row_factory para que las filas se lean como dict-like,
    facilitando pasarlas directo a los modelos Pydantic.
    """
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def get_usuario(telegram_id: int, db_path: str = DB_PATH) -> Usuario | None:
    """Busca un usuario registrado por su telegram_id. None si no existe."""
    async with get_connection(db_path) as db:
        cursor = await db.execute(
            "SELECT * FROM usuarios WHERE telegram_id = ?", (telegram_id,)
        )
        fila = await cursor.fetchone()
        return Usuario(**dict(fila)) if fila else None


async def crear_usuario(usuario: Usuario, db_path: str = DB_PATH) -> None:
    """Inserta un usuario nuevo (nombre + oficio, sin logo)."""
    async with get_connection(db_path) as db:
        await db.execute(
            "INSERT INTO usuarios (telegram_id, nombre, oficio) VALUES (?, ?, ?)",
            (usuario.telegram_id, usuario.nombre, usuario.oficio),
        )
        await db.commit()


async def crear_trabajo(trabajo: Trabajo, db_path: str = DB_PATH) -> int:
    """Inserta un trabajo presupuestado y devuelve su id autoincremental."""
    async with get_connection(db_path) as db:
        cursor = await db.execute(
            """INSERT INTO trabajos
               (usuario_id, cliente_nombre, descripcion, monto_total, monto_sena, estado)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                trabajo.usuario_id,
                trabajo.cliente_nombre,
                trabajo.descripcion,
                trabajo.monto_total,
                trabajo.monto_sena,
                trabajo.estado.value,
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def guardar_pdf_path(trabajo_id: int, pdf_path: str, db_path: str = DB_PATH) -> None:
    """Registra la ruta del PDF generado para un trabajo ya creado."""
    async with get_connection(db_path) as db:
        await db.execute(
            "UPDATE trabajos SET pdf_path = ? WHERE id = ?", (pdf_path, trabajo_id)
        )
        await db.commit()


async def marcar_sena_enviada(trabajo_id: int, db_path: str = DB_PATH) -> None:
    """Pasa el trabajo a estado sena_enviada. Arranca el conteo de REMINDER_DAYS."""
    async with get_connection(db_path) as db:
        await db.execute(
            "UPDATE trabajos SET estado = ? WHERE id = ?",
            (EstadoTrabajo.SENA_ENVIADA.value, trabajo_id),
        )
        await db.commit()


async def get_trabajos_para_recordar(dias: int, db_path: str = DB_PATH) -> list[Trabajo]:
    """Trabajos con seña enviada hace >= `dias` días y sin recordatorio marcado como pagado."""
    async with get_connection(db_path) as db:
        cursor = await db.execute(
            """SELECT * FROM trabajos
               WHERE estado = ?
                 AND datetime(creado_en) <= datetime('now', ?)
                 AND id NOT IN (
                     SELECT trabajo_id FROM recordatorios WHERE respuesta = ?
                 )""",
            (
                EstadoTrabajo.SENA_ENVIADA.value,
                f"-{dias} days",
                RespuestaRecordatorio.MARCADO_PAGADO.value,
            ),
        )
        filas = await cursor.fetchall()
        return [Trabajo(**dict(fila)) for fila in filas]


async def crear_recordatorio(trabajo_id: int, db_path: str = DB_PATH) -> None:
    """Registra el envío de un recordatorio de pago."""
    async with get_connection(db_path) as db:
        await db.execute(
            "INSERT INTO recordatorios (trabajo_id) VALUES (?)", (trabajo_id,)
        )
        await db.commit()


async def responder_ultimo_recordatorio(
    trabajo_id: int, respuesta: RespuestaRecordatorio, db_path: str = DB_PATH
) -> None:
    """Guarda la respuesta del trabajador al recordatorio más reciente de un trabajo."""
    async with get_connection(db_path) as db:
        await db.execute(
            """UPDATE recordatorios SET respuesta = ?
               WHERE id = (SELECT id FROM recordatorios WHERE trabajo_id = ?
                           ORDER BY enviado_en DESC LIMIT 1)""",
            (respuesta.value, trabajo_id),
        )
        await db.commit()


async def get_trabajo(trabajo_id: int, db_path: str = DB_PATH) -> Trabajo | None:
    """Busca un trabajo por id. None si no existe."""
    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT * FROM trabajos WHERE id = ?", (trabajo_id,))
        fila = await cursor.fetchone()
        return Trabajo(**dict(fila)) if fila else None
