"""Tests del flujo de registro (ADR-003): crear_usuario / get_usuario."""
import pytest

from database.db import crear_usuario, get_usuario
from database.models import Usuario


@pytest.mark.asyncio
async def test_usuario_no_existe_antes_de_registrarse(db_path: str) -> None:
    """Antes de crear_usuario, get_usuario debe devolver None."""
    assert await get_usuario(123, db_path) is None


@pytest.mark.asyncio
async def test_crear_usuario_lo_deja_recuperable(db_path: str) -> None:
    """Tras crear_usuario, get_usuario devuelve los mismos datos."""
    nuevo = Usuario(telegram_id=123, nombre="Carlos", oficio="electricista")
    await crear_usuario(nuevo, db_path)

    encontrado = await get_usuario(123, db_path)

    assert encontrado is not None
    assert encontrado.nombre == "Carlos"
    assert encontrado.oficio == "electricista"


@pytest.mark.asyncio
async def test_logo_path_queda_none_al_registrarse(db_path: str) -> None:
    """ADR-003: el registro inicial no pide logo, debe quedar None."""
    nuevo = Usuario(telegram_id=123, nombre="Carlos", oficio="electricista")
    await crear_usuario(nuevo, db_path)

    encontrado = await get_usuario(123, db_path)

    assert encontrado.logo_path is None
