"""Tests del flujo de /presupuesto (Momento 1): crear_trabajo y el handler."""
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram.ext import ConversationHandler

from database.db import crear_trabajo, crear_usuario, get_connection, get_usuario
from database.models import Trabajo, Usuario
import handlers.presupuesto as presupuesto_mod
from handlers.presupuesto import (
    ESPERANDO_CLIENTE,
    ESPERANDO_DESCRIPCION,
    ESPERANDO_MONTO,
    ESPERANDO_SENA,
    presupuesto,
    recibir_cliente,
    recibir_descripcion,
    recibir_monto,
    recibir_sena,
)


@pytest.mark.asyncio
async def test_crear_trabajo_lo_deja_recuperable(db_path: str) -> None:
    """Tras crear_trabajo, la fila queda en la tabla trabajos con estado presupuestado."""
    trabajo = Trabajo(
        usuario_id=1, cliente_nombre="Juan López", descripcion="Pintura",
        monto_total=180000, monto_sena=90000,
    )
    trabajo_id = await crear_trabajo(trabajo, db_path)

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT * FROM trabajos WHERE id = ?", (trabajo_id,))
        fila = await cursor.fetchone()

    assert fila["cliente_nombre"] == "Juan López"
    assert fila["estado"] == "presupuestado"
    assert fila["monto_sena"] == 90000


def _update_con_texto(texto: str) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = 1
    update.message.text = texto
    update.message.reply_text = AsyncMock()
    return update


def _context() -> MagicMock:
    context = MagicMock()
    context.user_data = {}
    return context


@pytest.mark.asyncio
async def test_presupuesto_sin_registro_termina_conversacion(db_path: str, monkeypatch) -> None:
    """Si el usuario no existe en la BD, /presupuesto no arranca el flujo."""
    monkeypatch.setattr(presupuesto_mod, "get_usuario", partial(get_usuario, db_path=db_path))

    update = _update_con_texto("/presupuesto")
    resultado = await presupuesto(update, _context())

    assert resultado == ConversationHandler.END
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_flujo_completo_guarda_trabajo(db_path: str, monkeypatch) -> None:
    """El flujo cliente → descripción → monto → seña termina creando el Trabajo."""
    monkeypatch.setattr(presupuesto_mod, "get_usuario", partial(get_usuario, db_path=db_path))
    monkeypatch.setattr(presupuesto_mod, "crear_trabajo", partial(crear_trabajo, db_path=db_path))
    await crear_usuario(Usuario(telegram_id=1, nombre="Carlos", oficio="pintor"), db_path)

    context = _context()

    assert await presupuesto(_update_con_texto("/presupuesto"), context) == ESPERANDO_CLIENTE
    assert await recibir_cliente(_update_con_texto("Juan López"), context) == ESPERANDO_DESCRIPCION
    assert await recibir_descripcion(_update_con_texto("Pintura de living"), context) == ESPERANDO_MONTO
    assert await recibir_monto(_update_con_texto("180000"), context) == ESPERANDO_SENA
    resultado = await recibir_sena(_update_con_texto("90000"), context)

    assert resultado == ConversationHandler.END
    assert context.user_data == {}

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT * FROM trabajos WHERE cliente_nombre = 'Juan López'")
        fila = await cursor.fetchone()
    assert fila["monto_total"] == 180000
    assert fila["monto_sena"] == 90000


@pytest.mark.asyncio
async def test_monto_invalido_repite_el_paso() -> None:
    """Un monto no numérico no avanza el flujo."""
    context = _context()
    resultado = await recibir_monto(_update_con_texto("no sé"), context)

    assert resultado == ESPERANDO_MONTO
    assert "monto_total" not in context.user_data


@pytest.mark.asyncio
async def test_sena_mayor_al_total_repite_el_paso() -> None:
    """Una seña que supera el total no avanza el flujo (invariante de negocio)."""
    context = _context()
    context.user_data["monto_total"] = 100.0

    resultado = await recibir_sena(_update_con_texto("500"), context)

    assert resultado == ESPERANDO_SENA


@pytest.mark.asyncio
async def test_sena_no_se_interpreta_monto_cero(db_path: str, monkeypatch) -> None:
    """Responder 'no' a la seña guarda el trabajo con monto_sena = 0."""
    monkeypatch.setattr(presupuesto_mod, "crear_trabajo", partial(crear_trabajo, db_path=db_path))
    await crear_usuario(Usuario(telegram_id=2, nombre="Ana", oficio="electricista"), db_path)

    context = _context()
    context.user_data = {"cliente_nombre": "María", "descripcion": "Cableado", "monto_total": 50000.0}
    update = _update_con_texto("no")
    update.effective_user.id = 2

    resultado = await recibir_sena(update, context)

    assert resultado == ConversationHandler.END
    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT * FROM trabajos WHERE cliente_nombre = 'María'")
        fila = await cursor.fetchone()
    assert fila["monto_sena"] == 0
