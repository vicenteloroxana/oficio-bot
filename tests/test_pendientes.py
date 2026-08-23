"""Tests de /pendientes (Momento 5): listado y cancelación por botón."""
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest

from database.db import (
    crear_trabajo,
    crear_usuario,
    get_connection,
    marcar_cancelado,
)
from database.models import Trabajo, Usuario
import handlers.pendientes as pendientes_mod
from handlers.pendientes import cancelar_pendiente, pendientes


def _message_update() -> MagicMock:
    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()
    return update


def _callback_update(data: str) -> MagicMock:
    update = MagicMock()
    update.callback_query.data = data
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_pendientes_sin_trabajos_avisa_vacio(db_path: str, monkeypatch) -> None:
    """Sin trabajos pendientes, responde un solo mensaje sin listar nada."""
    monkeypatch.setattr(
        pendientes_mod, "get_trabajos_pendientes", AsyncMock(return_value=[])
    )
    update = _message_update()

    await pendientes(update, MagicMock())

    update.message.reply_text.assert_called_once_with("No tenés trabajos pendientes de cobro. 🎉")


@pytest.mark.asyncio
async def test_pendientes_lista_un_mensaje_por_trabajo_con_boton(db_path: str, monkeypatch) -> None:
    """Cada trabajo pendiente llega en su propio mensaje con botón de cancelar."""
    await crear_usuario(Usuario(telegram_id=1, nombre="Carlos", oficio="pintor"), db_path)
    trabajo = Trabajo(
        usuario_id=1, cliente_nombre="Juan López", descripcion="Pintura",
        monto_total=180000, monto_sena=90000,
    )
    await crear_trabajo(trabajo, db_path)
    monkeypatch.setattr(
        pendientes_mod, "get_trabajos_pendientes", partial(_get_pendientes_real, db_path=db_path)
    )
    update = _message_update()

    await pendientes(update, MagicMock())

    # 1 mensaje de encabezado + 1 por trabajo
    assert update.message.reply_text.call_count == 2
    texto_trabajo = update.message.reply_text.call_args_list[1].args[0]
    assert "Juan López" in texto_trabajo
    boton = update.message.reply_text.call_args_list[1].kwargs["reply_markup"]
    assert boton.inline_keyboard[0][0].text == "Cliente no aceptó"


async def _get_pendientes_real(usuario_id: int, db_path: str):
    from database.db import get_trabajos_pendientes
    return await get_trabajos_pendientes(usuario_id, db_path=db_path)


@pytest.mark.asyncio
async def test_cancelar_pendiente_marca_cancelado(db_path: str, monkeypatch) -> None:
    """El botón [Cliente no aceptó] pasa el trabajo a estado cancelado."""
    await crear_usuario(Usuario(telegram_id=1, nombre="Carlos", oficio="pintor"), db_path)
    trabajo = Trabajo(
        usuario_id=1, cliente_nombre="María García", descripcion="Electricidad",
        monto_total=50000, monto_sena=0,
    )
    trabajo_id = await crear_trabajo(trabajo, db_path)
    monkeypatch.setattr(pendientes_mod, "marcar_cancelado", partial(marcar_cancelado, db_path=db_path))

    update = _callback_update(f"pendiente_cancelar:{trabajo_id}")
    await cancelar_pendiente(update, MagicMock())

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT estado FROM trabajos WHERE id = ?", (trabajo_id,))
        fila = await cursor.fetchone()
    assert fila["estado"] == "cancelado"
    update.callback_query.edit_message_text.assert_called_once_with("Ok, trabajo cancelado.")
