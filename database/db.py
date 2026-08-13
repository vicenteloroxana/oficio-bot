"""Inicialización y conexión a la base de datos SQLite.

Usa aiosqlite directamente (sin ORM) — los modelos Pydantic en
models.py validan los datos antes de que lleguen acá.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import aiosqlite

from database.models import Usuario

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
