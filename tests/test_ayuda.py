"""Tests de handlers/ayuda.py: /help y los fallbacks de comando/mensaje no reconocido."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from handlers.ayuda import ayuda, comando_no_reconocido, mensaje_no_reconocido


def _update() -> MagicMock:
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_ayuda_lista_los_comandos() -> None:
    update = _update()
    await ayuda(update, MagicMock())

    texto = update.message.reply_text.call_args.args[0]
    for comando in (
        "/presupuesto", "/cobrar", "/resumen", "/perfil",
        "/reintentar_pdf", "/confirmar_envio", "/cancel", "/help",
    ):
        assert comando in texto


@pytest.mark.asyncio
async def test_comando_no_reconocido_sugiere_help() -> None:
    update = _update()
    await comando_no_reconocido(update, MagicMock())

    assert "/help" in update.message.reply_text.call_args.args[0]


@pytest.mark.asyncio
async def test_mensaje_no_reconocido_sugiere_help() -> None:
    update = _update()
    await mensaje_no_reconocido(update, MagicMock())

    assert "/help" in update.message.reply_text.call_args.args[0]
