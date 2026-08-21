"""Tests de database/db.py: helpers de fecha/hora (ahora_argentina)."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

import database.db as db_mod
from database.db import ahora_argentina, crear_trabajo, crear_usuario, get_connection
from database.models import Trabajo, Usuario

# 2026-08-21 01:00 UTC == 2026-08-20 22:00 hora Argentina (UTC-3) — el caso
# real reportado: un trabajo cargado a la noche corría de día en la BD.
_UTC_MADRUGADA_SIGUIENTE = datetime(2026, 8, 21, 1, 0, 0, tzinfo=timezone.utc)


def _simular_reloj_del_server_en_utc(monkeypatch) -> None:
    """El server puede correr con el reloj del sistema en UTC (típico en
    Railway/Docker) — se simula reemplazando datetime.now(tz) para que
    devuelva siempre el mismo instante UTC fijo, sin importar tz pedido."""
    datetime_falso = MagicMock(wraps=datetime)
    datetime_falso.now.side_effect = lambda tz=None: _UTC_MADRUGADA_SIGUIENTE.astimezone(tz)
    monkeypatch.setattr(db_mod, "datetime", datetime_falso)


def test_ahora_argentina_devuelve_datetime_naive() -> None:
    """Sin tzinfo — se guarda como string plano en SQLite, sin timezone."""
    momento = ahora_argentina()
    assert momento.tzinfo is None


def test_ahora_argentina_corrige_el_corrimiento_de_dia_utc(monkeypatch) -> None:
    """El caso real reportado: un trabajo cargado a las 22:00 hora Argentina
    (01:00 UTC del día siguiente) debe quedar fechado el día correcto,
    no el día siguiente como pasaba con CURRENT_TIMESTAMP de SQLite (UTC)."""
    _simular_reloj_del_server_en_utc(monkeypatch)

    momento = ahora_argentina()

    assert momento.day == 20
    assert momento.hour == 22


@pytest.mark.asyncio
async def test_crear_trabajo_guarda_fecha_argentina_no_utc(db_path: str, monkeypatch) -> None:
    """crear_trabajo persiste creado_en en hora Argentina, sin depender del
    CURRENT_TIMESTAMP (UTC) de SQLite."""
    _simular_reloj_del_server_en_utc(monkeypatch)

    trabajo = Trabajo(
        usuario_id=1, cliente_nombre="Juan", descripcion="Prueba",
        monto_total=1000, monto_sena=0,
    )
    trabajo_id = await crear_trabajo(trabajo, db_path)

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT creado_en FROM trabajos WHERE id = ?", (trabajo_id,))
        fila = await cursor.fetchone()

    assert fila["creado_en"].startswith("2026-08-20 22:")


@pytest.mark.asyncio
async def test_crear_usuario_guarda_fecha_argentina(db_path: str, monkeypatch) -> None:
    """Mismo fix aplicado a usuarios.creado_en."""
    _simular_reloj_del_server_en_utc(monkeypatch)

    await crear_usuario(Usuario(telegram_id=1, nombre="Ana", oficio="pintora"), db_path)

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT creado_en FROM usuarios WHERE telegram_id = 1")
        fila = await cursor.fetchone()

    assert fila["creado_en"].startswith("2026-08-20 22:")
