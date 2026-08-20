"""Tests del registro de cobro final (Momento 3): query de pendientes y handlers."""
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest

from database.db import crear_trabajo, get_connection, get_trabajos_pendientes, marcar_cobrado
from database.models import FormaPago, Trabajo
import handlers.cobro as cobro_mod
from handlers.cobro import cobrar, recibir_forma_pago, recibir_trabajo


def _trabajo(usuario_id: int = 1, monto_total: float = 180000, monto_sena: float = 90000) -> Trabajo:
    return Trabajo(
        usuario_id=usuario_id, cliente_nombre="Juan López", descripcion="Pintura living",
        monto_total=monto_total, monto_sena=monto_sena,
    )


@pytest.mark.asyncio
async def test_get_trabajos_pendientes_incluye_presupuestado(db_path: str) -> None:
    """Un trabajo recién presupuestado (sin cobrar) aparece como pendiente."""
    await crear_trabajo(_trabajo(), db_path)

    trabajos = await get_trabajos_pendientes(1, db_path)

    assert len(trabajos) == 1
    assert trabajos[0].cliente_nombre == "Juan López"


@pytest.mark.asyncio
async def test_get_trabajos_pendientes_excluye_finalizado(db_path: str) -> None:
    """Un trabajo ya cobrado no vuelve a aparecer como pendiente."""
    trabajo_id = await crear_trabajo(_trabajo(), db_path)
    await marcar_cobrado(trabajo_id, FormaPago.EFECTIVO, db_path)

    trabajos = await get_trabajos_pendientes(1, db_path)

    assert trabajos == []


@pytest.mark.asyncio
async def test_get_trabajos_pendientes_excluye_otro_usuario(db_path: str) -> None:
    """Los trabajos pendientes de otro usuario no se mezclan."""
    await crear_trabajo(_trabajo(usuario_id=2), db_path)

    trabajos = await get_trabajos_pendientes(1, db_path)

    assert trabajos == []


@pytest.mark.asyncio
async def test_marcar_cobrado_guarda_forma_pago_y_fecha(db_path: str) -> None:
    """marcar_cobrado pasa a finalizado y guarda forma_pago + cobrado_en."""
    trabajo_id = await crear_trabajo(_trabajo(), db_path)

    await marcar_cobrado(trabajo_id, FormaPago.TRANSFERENCIA, db_path)

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT * FROM trabajos WHERE id = ?", (trabajo_id,))
        fila = dict(await cursor.fetchone())
    assert fila["estado"] == "finalizado"
    assert fila["forma_pago"] == "transferencia"
    assert fila["cobrado_en"] is not None


def _text_update(texto: str) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = 1
    update.message.text = texto
    update.message.reply_text = AsyncMock()
    return update


def _callback_update(data: str) -> MagicMock:
    update = MagicMock()
    update.callback_query.data = data
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_cobrar_sin_pendientes_termina_conversacion(db_path: str, monkeypatch) -> None:
    """/cobrar sin trabajos pendientes avisa y no entra al flujo."""
    monkeypatch.setattr(cobro_mod, "get_trabajos_pendientes", partial(get_trabajos_pendientes, db_path=db_path))

    update = _text_update("")
    resultado = await cobrar(update, MagicMock())

    update.message.reply_text.assert_called_once()
    assert "no tenés" in update.message.reply_text.call_args[0][0].lower()
    from telegram.ext import ConversationHandler
    assert resultado == ConversationHandler.END


@pytest.mark.asyncio
async def test_recibir_trabajo_numero_invalido_reintenta(db_path: str) -> None:
    """Un número fuera de rango vuelve a pedir la elección."""
    context = MagicMock()
    context.user_data = {"trabajos_pendientes": [_trabajo()]}
    update = _text_update("9")

    from handlers.cobro import ESPERANDO_TRABAJO
    resultado = await recibir_trabajo(update, context)

    assert resultado == ESPERANDO_TRABAJO


@pytest.mark.asyncio
async def test_recibir_trabajo_valido_pregunta_forma_pago(db_path: str) -> None:
    """Elegir un trabajo válido pide la forma de pago y guarda el trabajo elegido."""
    context = MagicMock()
    trabajo = _trabajo()
    context.user_data = {"trabajos_pendientes": [trabajo]}
    update = _text_update("1")

    await recibir_trabajo(update, context)

    assert context.user_data["trabajo_cobrado"] is trabajo
    texto = update.message.reply_text.call_args[0][0]
    assert "$180000" in texto.replace(".", "") or "180000" in texto


@pytest.mark.asyncio
async def test_recibir_forma_pago_cierra_trabajo(db_path: str, monkeypatch) -> None:
    """Elegir una forma de pago marca el trabajo como cobrado."""
    trabajo_id = await crear_trabajo(_trabajo(), db_path)
    monkeypatch.setattr(cobro_mod, "marcar_cobrado", partial(marcar_cobrado, db_path=db_path))

    from database.db import get_trabajo as _get_trabajo
    trabajo_obj = await _get_trabajo(trabajo_id, db_path)

    context = MagicMock()
    context.user_data = {"trabajo_cobrado": trabajo_obj}
    update = _callback_update("cobro_forma:efectivo")

    await recibir_forma_pago(update, context)

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT estado, forma_pago FROM trabajos WHERE id = ?", (trabajo_id,))
        fila = dict(await cursor.fetchone())
    assert fila["estado"] == "finalizado"
    assert fila["forma_pago"] == "efectivo"
    assert "trabajo_cobrado" not in context.user_data
