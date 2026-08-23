"""Tests de /clientes (Momento 6): agregado por cliente, detalle, selección."""
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest

from database.db import (
    crear_trabajo,
    crear_usuario,
    get_clientes_resumen,
    get_trabajos_de_cliente,
    marcar_cancelado,
    marcar_cobrado,
)
from database.models import FormaPago, Trabajo, Usuario
import handlers.clientes as clientes_mod
from handlers.clientes import _texto_lista, clientes, recibir_cliente
from database.models import ClienteResumen


def _trabajo(cliente: str, usuario_id: int = 1, monto_total: float = 180000, monto_sena: float = 0) -> Trabajo:
    return Trabajo(
        usuario_id=usuario_id, cliente_nombre=cliente, descripcion="Pintura",
        monto_total=monto_total, monto_sena=monto_sena,
    )


def _text_update(texto: str) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = 1
    update.message.text = texto
    update.message.reply_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_get_clientes_resumen_agrega_por_cliente(db_path: str) -> None:
    """Dos trabajos del mismo cliente se agregan en una sola fila."""
    id1 = await crear_trabajo(_trabajo("Juan López", monto_total=180000), db_path)
    await marcar_cobrado(id1, FormaPago.EFECTIVO, db_path)
    await crear_trabajo(_trabajo("Juan López", monto_total=120000), db_path)

    resumen = await get_clientes_resumen(1, db_path)

    assert len(resumen) == 1
    assert resumen[0].cliente_nombre == "Juan López"
    assert resumen[0].cantidad_trabajos == 2
    assert resumen[0].monto_cobrado == 180000
    assert resumen[0].tiene_pendiente is True


@pytest.mark.asyncio
async def test_get_clientes_resumen_excluye_cliente_solo_cancelado(db_path: str) -> None:
    """Un cliente cuyo único trabajo fue cancelado no aparece en la lista principal."""
    id1 = await crear_trabajo(_trabajo("María García"), db_path)
    await marcar_cancelado(id1, db_path)

    resumen = await get_clientes_resumen(1, db_path)

    assert resumen == []


@pytest.mark.asyncio
async def test_get_clientes_resumen_no_mezcla_otro_usuario(db_path: str) -> None:
    """Los clientes de otro usuario no se mezclan."""
    await crear_trabajo(_trabajo("Juan López", usuario_id=2), db_path)

    resumen = await get_clientes_resumen(1, db_path)

    assert resumen == []


@pytest.mark.asyncio
async def test_get_trabajos_de_cliente_incluye_cancelados(db_path: str) -> None:
    """El detalle de un cliente incluye trabajos cancelados, a diferencia de la lista principal."""
    id1 = await crear_trabajo(_trabajo("Juan López"), db_path)
    await marcar_cancelado(id1, db_path)
    await crear_trabajo(_trabajo("Juan López"), db_path)

    trabajos = await get_trabajos_de_cliente(1, "Juan López", db_path)

    assert len(trabajos) == 2


def test_texto_lista_muestra_cobrado_y_pendiente_juntos() -> None:
    """Un cliente con algo ya cobrado Y algo todavía pendiente muestra ambas cosas,
    no solo la primera — son categorías que pueden coexistir, no excluyentes."""
    cliente = ClienteResumen(
        cliente_nombre="Juan López", cantidad_trabajos=2, monto_cobrado=180000, tiene_pendiente=True
    )

    texto = _texto_lista([cliente])

    assert "180000 cobrado" in texto.replace(".", "")
    assert "pendiente de cobro" in texto


def test_texto_lista_solo_cobrado_no_menciona_pendiente() -> None:
    """Sin nada pendiente, no aparece la frase 'pendiente de cobro'."""
    cliente = ClienteResumen(
        cliente_nombre="Carlos Díaz", cantidad_trabajos=1, monto_cobrado=220000, tiene_pendiente=False
    )

    texto = _texto_lista([cliente])

    assert "pendiente de cobro" not in texto


@pytest.mark.asyncio
async def test_clientes_sin_historial_avisa_vacio(db_path: str, monkeypatch) -> None:
    """Sin clientes, /clientes avisa y no entra al flujo de selección."""
    monkeypatch.setattr(clientes_mod, "get_clientes_resumen", partial(get_clientes_resumen, db_path=db_path))
    update = _text_update("")

    resultado = await clientes(update, MagicMock())

    update.message.reply_text.assert_called_once()
    assert "todavía no tenés clientes" in update.message.reply_text.call_args[0][0].lower()
    from telegram.ext import ConversationHandler
    assert resultado == ConversationHandler.END


@pytest.mark.asyncio
async def test_recibir_cliente_numero_invalido_reintenta(db_path: str) -> None:
    """Un número fuera de rango vuelve a pedir la elección."""
    context = MagicMock()
    context.user_data = {"clientes_lista": [MagicMock(cliente_nombre="Juan López")]}
    update = _text_update("9")

    from handlers.clientes import ESPERANDO_CLIENTE
    resultado = await recibir_cliente(update, context)

    assert resultado == ESPERANDO_CLIENTE


@pytest.mark.asyncio
async def test_recibir_cliente_valido_muestra_detalle(db_path: str, monkeypatch) -> None:
    """Elegir un cliente válido muestra su detalle de trabajos."""
    await crear_usuario(Usuario(telegram_id=1, nombre="Carlos", oficio="pintor"), db_path)
    await crear_trabajo(_trabajo("Juan López", monto_total=180000), db_path)
    monkeypatch.setattr(
        clientes_mod, "get_trabajos_de_cliente", partial(get_trabajos_de_cliente, db_path=db_path)
    )
    resumen = await get_clientes_resumen(1, db_path)

    context = MagicMock()
    context.user_data = {"clientes_lista": resumen}
    update = _text_update("1")

    await recibir_cliente(update, context)

    texto = update.message.reply_text.call_args[0][0]
    assert "Juan López" in texto
    assert "180000" in texto.replace(".", "").replace(",", "")
