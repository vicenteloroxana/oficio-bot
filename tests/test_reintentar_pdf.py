"""Tests de /reintentar_pdf: regenerar el PDF de un trabajo con pdf_error=1
sin crear un Trabajo duplicado."""
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram.ext import ConversationHandler

from database.db import (
    crear_trabajo,
    crear_usuario,
    get_connection,
    get_trabajos_con_pdf_error,
    get_usuario,
    guardar_pdf_path,
    limpiar_pdf_error,
    marcar_pdf_error,
)
from database.models import Trabajo, Usuario
import handlers.reintentar_pdf as reintentar_mod
from handlers.reintentar_pdf import reintentar_pdf, recibir_trabajo


def _trabajo(usuario_id: int) -> Trabajo:
    return Trabajo(
        usuario_id=usuario_id, cliente_nombre="Pedro", descripcion="Cañería",
        monto_total=30000, monto_sena=0,
    )


def _update_con_texto(texto: str, usuario_id: int) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = usuario_id
    update.message.text = texto
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()
    return update


def _context(trabajos: list[Trabajo]) -> MagicMock:
    context = MagicMock()
    context.user_data = {"trabajos_pdf_error": trabajos}
    return context


@pytest.mark.asyncio
async def test_get_trabajos_con_pdf_error_solo_incluye_marcados(db_path: str) -> None:
    """Un trabajo sin pdf_error no aparece en la lista de reintento."""
    ok_id = await crear_trabajo(_trabajo(1), db_path)
    error_id = await crear_trabajo(_trabajo(1), db_path)
    await marcar_pdf_error(error_id, db_path)

    trabajos = await get_trabajos_con_pdf_error(1, db_path)

    assert len(trabajos) == 1
    assert trabajos[0].id == error_id
    assert ok_id not in [t.id for t in trabajos]


@pytest.mark.asyncio
async def test_reintentar_pdf_sin_pendientes_no_arranca_flujo(db_path: str, monkeypatch) -> None:
    """Sin trabajos con pdf_error, /reintentar_pdf avisa y no pide elegir."""
    monkeypatch.setattr(
        reintentar_mod, "get_trabajos_con_pdf_error",
        partial(get_trabajos_con_pdf_error, db_path=db_path),
    )
    update = _update_con_texto("/reintentar_pdf", 1)

    resultado = await reintentar_pdf(update, MagicMock(user_data={}))

    assert resultado == ConversationHandler.END
    update.message.reply_text.assert_called_once()


@pytest.mark.asyncio
async def test_recibir_trabajo_reintenta_sobre_el_mismo_id_sin_duplicar(
    db_path: str, tmp_path, monkeypatch
) -> None:
    """El caso que motivó este handler: reintentar el PDF no debe crear un
    segundo Trabajo — debe actuar sobre el trabajo_id ya existente."""
    pdf_falso = tmp_path / "presupuesto.pdf"
    pdf_falso.write_bytes(b"%PDF-1.4 fake")

    await crear_usuario(Usuario(telegram_id=5, nombre="Dani", oficio="plomero"), db_path)
    trabajo_id = await crear_trabajo(_trabajo(5), db_path)
    await marcar_pdf_error(trabajo_id, db_path)

    monkeypatch.setattr(reintentar_mod, "get_usuario", partial(get_usuario, db_path=db_path))
    monkeypatch.setattr("handlers.presupuesto.guardar_pdf_path", partial(guardar_pdf_path, db_path=db_path))
    monkeypatch.setattr("handlers.presupuesto.limpiar_pdf_error", partial(limpiar_pdf_error, db_path=db_path))
    monkeypatch.setattr("handlers.presupuesto.generar_pdf", lambda usuario, trabajo: str(pdf_falso))

    trabajo_obj = Trabajo(id=trabajo_id, usuario_id=5, cliente_nombre="Pedro", descripcion="Cañería", monto_total=30000, monto_sena=0)
    context = _context([trabajo_obj])
    update = _update_con_texto("1", 5)

    resultado = await recibir_trabajo(update, context)

    assert resultado == ConversationHandler.END
    update.message.reply_document.assert_called_once()

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT * FROM trabajos WHERE usuario_id = 5")
        filas = await cursor.fetchall()
    assert len(filas) == 1  # no se creó un segundo Trabajo
    assert filas[0]["id"] == trabajo_id
    assert filas[0]["pdf_path"] == str(pdf_falso)
    assert filas[0]["pdf_error"] == 0  # se limpió tras el éxito


@pytest.mark.asyncio
async def test_indice_invalido_repite_el_paso(db_path: str) -> None:
    """Elegir un número fuera de rango no cierra el flujo."""
    trabajo_obj = Trabajo(id=1, usuario_id=1, cliente_nombre="Pedro", descripcion="Cañería", monto_total=30000, monto_sena=0)
    context = _context([trabajo_obj])
    update = _update_con_texto("9", 1)

    resultado = await recibir_trabajo(update, context)

    assert resultado == reintentar_mod.ESPERANDO_TRABAJO
