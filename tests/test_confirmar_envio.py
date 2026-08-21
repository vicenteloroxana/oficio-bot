"""Tests de /confirmar_envio: marcar sena_enviada sobre un trabajo existente
cuando el trabajador respondió "Todavía no" en el momento de /presupuesto."""
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram.ext import ConversationHandler

from database.db import (
    crear_trabajo,
    get_connection,
    get_trabajos_sin_confirmar_envio,
    marcar_cobrado,
    marcar_sena_enviada,
)
from database.models import EstadoTrabajo, FormaPago, Trabajo
import handlers.confirmar_envio as confirmar_mod
from handlers.confirmar_envio import confirmar_envio, recibir_trabajo


def _trabajo(usuario_id: int, monto_sena: float = 500) -> Trabajo:
    return Trabajo(
        usuario_id=usuario_id, cliente_nombre="Carlos", descripcion="Auto",
        monto_total=10000, monto_sena=monto_sena,
    )


def _update_con_texto(texto: str, usuario_id: int) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = usuario_id
    update.message.text = texto
    update.message.reply_text = AsyncMock()
    return update


def _context(trabajos: list[Trabajo]) -> MagicMock:
    context = MagicMock()
    context.user_data = {"trabajos_sin_confirmar": trabajos}
    return context


@pytest.mark.asyncio
async def test_get_trabajos_sin_confirmar_envio_excluye_sin_sena(db_path: str) -> None:
    """Sin seña pedida, no hay envío que confirmar — no debe aparecer en la lista."""
    con_sena_id = await crear_trabajo(_trabajo(1, monto_sena=500), db_path)
    sin_sena_id = await crear_trabajo(_trabajo(1, monto_sena=0), db_path)

    trabajos = await get_trabajos_sin_confirmar_envio(1, db_path)

    assert [t.id for t in trabajos] == [con_sena_id]
    assert sin_sena_id not in [t.id for t in trabajos]


@pytest.mark.asyncio
async def test_get_trabajos_sin_confirmar_envio_excluye_ya_enviados(db_path: str) -> None:
    """Un trabajo que ya pasó a sena_enviada no debe volver a aparecer."""
    trabajo_id = await crear_trabajo(_trabajo(1), db_path)
    await marcar_cobrado(trabajo_id, FormaPago.EFECTIVO, db_path)  # cambia el estado

    trabajos = await get_trabajos_sin_confirmar_envio(1, db_path)

    assert trabajos == []


@pytest.mark.asyncio
async def test_confirmar_envio_sin_pendientes_no_arranca_flujo(db_path: str, monkeypatch) -> None:
    """Sin trabajos pendientes de confirmar, avisa y no pide elegir."""
    monkeypatch.setattr(
        confirmar_mod, "get_trabajos_sin_confirmar_envio",
        partial(get_trabajos_sin_confirmar_envio, db_path=db_path),
    )
    update = _update_con_texto("/confirmar_envio", 1)

    resultado = await confirmar_envio(update, MagicMock(user_data={}))

    assert resultado == ConversationHandler.END
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_recibir_trabajo_marca_sena_enviada_sobre_el_mismo_id(
    db_path: str, monkeypatch
) -> None:
    """El caso real que motivó este handler: el trabajo que quedó trabado en
    'presupuestado' tras responder 'Todavía no' pasa a sena_enviada."""
    trabajo_id = await crear_trabajo(_trabajo(1), db_path)
    monkeypatch.setattr(
        confirmar_mod, "marcar_sena_enviada", partial(marcar_sena_enviada, db_path=db_path)
    )

    trabajo_obj = Trabajo(
        id=trabajo_id, usuario_id=1, cliente_nombre="Carlos", descripcion="Auto",
        monto_total=10000, monto_sena=500,
    )
    context = _context([trabajo_obj])
    update = _update_con_texto("1", 1)

    resultado = await recibir_trabajo(update, context)

    assert resultado == ConversationHandler.END
    update.message.reply_text.assert_called_once()
    assert "Carlos" in update.message.reply_text.call_args.args[0]

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT * FROM trabajos WHERE id = ?", (trabajo_id,))
        fila = await cursor.fetchone()
    assert fila["estado"] == EstadoTrabajo.SENA_ENVIADA.value


@pytest.mark.asyncio
async def test_indice_invalido_repite_el_paso(db_path: str) -> None:
    """Elegir un número fuera de rango no cierra el flujo."""
    trabajo_obj = Trabajo(
        id=1, usuario_id=1, cliente_nombre="Carlos", descripcion="Auto",
        monto_total=10000, monto_sena=500,
    )
    context = _context([trabajo_obj])
    update = _update_con_texto("9", 1)

    resultado = await recibir_trabajo(update, context)

    assert resultado == confirmar_mod.ESPERANDO_TRABAJO
