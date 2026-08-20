"""Tests del flujo de perfil (Momento 6): edición de nombre, oficio y logo."""
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest

from database.db import actualizar_usuario, crear_usuario, get_connection, get_usuario
from database.models import Usuario
import handlers.perfil as perfil_mod
from handlers.perfil import (
    ESPERANDO_CAMPO,
    ESPERANDO_LOGO,
    ESPERANDO_NOMBRE,
    ESPERANDO_OFICIO,
    elegir_campo,
    perfil,
    recibir_logo,
    recibir_nombre,
    recibir_oficio,
)


def _usuario(telegram_id: int = 1) -> Usuario:
    return Usuario(telegram_id=telegram_id, nombre="Carlos Rodríguez", oficio="electricista")


def _text_update(texto: str, telegram_id: int = 1) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = telegram_id
    update.message.text = texto
    update.message.reply_text = AsyncMock()
    return update


def _callback_update(data: str, telegram_id: int = 1) -> MagicMock:
    update = MagicMock()
    update.effective_user.id = telegram_id
    update.callback_query.data = data
    update.callback_query.answer = AsyncMock()
    update.callback_query.message.reply_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_actualizar_usuario_cambia_nombre(db_path: str) -> None:
    """actualizar_usuario persiste el nombre nuevo sin tocar el oficio."""
    await crear_usuario(_usuario(), db_path)

    await actualizar_usuario(1, nombre="Carlos R.", db_path=db_path)

    usuario = await get_usuario(1, db_path)
    assert usuario.nombre == "Carlos R."
    assert usuario.oficio == "electricista"


@pytest.mark.asyncio
async def test_actualizar_usuario_cambia_oficio(db_path: str) -> None:
    """actualizar_usuario persiste el oficio nuevo sin tocar el nombre."""
    await crear_usuario(_usuario(), db_path)

    await actualizar_usuario(1, oficio="gasista", db_path=db_path)

    usuario = await get_usuario(1, db_path)
    assert usuario.oficio == "gasista"
    assert usuario.nombre == "Carlos Rodríguez"


@pytest.mark.asyncio
async def test_perfil_sin_registrar_pide_start(db_path: str, monkeypatch) -> None:
    """/perfil sin usuario registrado avisa y termina la conversación."""
    monkeypatch.setattr(perfil_mod, "get_usuario", partial(get_usuario, db_path=db_path))

    from telegram.ext import ConversationHandler
    resultado = await perfil(_text_update(""), MagicMock())

    assert resultado == ConversationHandler.END


@pytest.mark.asyncio
async def test_perfil_registrado_muestra_botones(db_path: str, monkeypatch) -> None:
    """/perfil con usuario registrado muestra su estado actual y pasa a ESPERANDO_CAMPO."""
    await crear_usuario(_usuario(), db_path)
    monkeypatch.setattr(perfil_mod, "get_usuario", partial(get_usuario, db_path=db_path))

    resultado = await perfil(_text_update(""), MagicMock())

    assert resultado == ESPERANDO_CAMPO


@pytest.mark.asyncio
async def test_elegir_campo_nombre_pide_texto() -> None:
    """Elegir [Nombre] pide el valor y pasa a ESPERANDO_NOMBRE."""
    resultado = await elegir_campo(_callback_update("perfil_editar:nombre"), MagicMock())
    assert resultado == ESPERANDO_NOMBRE


@pytest.mark.asyncio
async def test_elegir_campo_logo_pide_foto() -> None:
    """Elegir [Subir logo] pide la imagen y pasa a ESPERANDO_LOGO."""
    resultado = await elegir_campo(_callback_update("perfil_editar:logo"), MagicMock())
    assert resultado == ESPERANDO_LOGO


@pytest.mark.asyncio
async def test_recibir_nombre_vacio_reintenta(db_path: str) -> None:
    """Un nombre vacío vuelve a pedir el dato."""
    resultado = await recibir_nombre(_text_update("   "), MagicMock())
    assert resultado == ESPERANDO_NOMBRE


@pytest.mark.asyncio
async def test_recibir_oficio_guarda_y_termina(db_path: str, monkeypatch) -> None:
    """Un oficio válido se persiste y cierra la conversación."""
    await crear_usuario(_usuario(), db_path)
    monkeypatch.setattr(perfil_mod, "actualizar_usuario", partial(actualizar_usuario, db_path=db_path))

    from telegram.ext import ConversationHandler
    resultado = await recibir_oficio(_text_update("gasista"), MagicMock())

    assert resultado == ConversationHandler.END
    usuario = await get_usuario(1, db_path)
    assert usuario.oficio == "gasista"


@pytest.mark.asyncio
async def test_recibir_logo_supera_tamano_maximo_reintenta(monkeypatch) -> None:
    """Una foto que supera MAX_LOGO_SIZE_MB no se guarda y vuelve a pedir la imagen."""
    monkeypatch.setattr(perfil_mod, "MAX_LOGO_SIZE_MB", 2.0)
    update = MagicMock()
    update.effective_user.id = 1
    update.message.photo = [MagicMock(file_size=3 * 1024 * 1024)]
    update.message.reply_text = AsyncMock()

    resultado = await recibir_logo(update, MagicMock())

    assert resultado == ESPERANDO_LOGO
    update.message.reply_text.assert_called_once()
    assert "supera" in update.message.reply_text.call_args[0][0].lower()
