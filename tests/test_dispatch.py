"""Test de integración de dispatch: cubre cobertura arquitectural, no lógica de negocio.

Arma la Application real con los mismos handlers que main.py y le pasa
Updates sintéticos vía process_update() (bot mockeado, sin red real).
Objetivo: detectar huecos donde ningún handler responde (origen: un
comando desconocido y un texto libre fuera de flujo quedaban en silencio
total, ver docs/backlog.md) y confirmar que el fallback global no le roba
mensajes a un ConversationHandler con un estado activo.

Se verifica vía bot.send_message (lo que reply_text llama internamente)
en vez de mockear Message.reply_text — los objetos de la librería quedan
"congelados" tras pasar por process_update y no aceptan mocks directos.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import Chat, Message, MessageEntity, Update, User
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from handlers.ayuda import ayuda, comando_no_reconocido, mensaje_no_reconocido
from handlers.presupuesto import presupuesto_handler


async def _app() -> tuple[Application, AsyncMock]:
    """Arma la misma cadena de handlers relevante de main.py, con bot mockeado."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.initialize = AsyncMock()
    app = Application.builder().bot(bot).build()
    app.add_handler(presupuesto_handler)
    app.add_handler(CommandHandler("help", ayuda))
    app.add_handler(MessageHandler(filters.COMMAND, comando_no_reconocido))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_no_reconocido))
    await app.initialize()
    return app, bot.send_message


def _update(texto: str, update_id: int, bot) -> Update:
    """Construye un Update mínimo a partir de un texto de usuario."""
    chat = Chat(id=1, type="private")
    user = User(id=1, first_name="Test", is_bot=False)
    es_comando = texto.startswith("/")
    entities = (
        [MessageEntity(type="bot_command", offset=0, length=len(texto))] if es_comando else []
    )
    message = Message(
        message_id=update_id, date=None, chat=chat, from_user=user,
        text=texto, entities=entities,
    )
    message.set_bot(bot)
    return Update(update_id=update_id, message=message)


@pytest.mark.asyncio
async def test_comando_desconocido_recibe_respuesta() -> None:
    """Un /comando sin handler propio no debe quedar en silencio (fallback catch-all)."""
    app, send_message = await _app()

    await app.process_update(_update("/xyz", 1, app.bot))

    send_message.assert_called_once()


@pytest.mark.asyncio
async def test_texto_libre_sin_flujo_activo_recibe_respuesta() -> None:
    """Texto libre fuera de cualquier ConversationHandler no debe quedar en silencio."""
    app, send_message = await _app()

    await app.process_update(_update("en que quedamos", 1, app.bot))

    send_message.assert_called_once()


@pytest.mark.asyncio
async def test_catch_all_no_intercepta_flujo_activo_de_presupuesto(monkeypatch) -> None:
    """El fallback global no debe robarle el mensaje a presupuesto_handler
    cuando hay una conversación en curso (riesgo real: orden de handlers)."""
    monkeypatch.setattr(
        "handlers.presupuesto.get_usuario", AsyncMock(return_value=MagicMock())
    )
    app, send_message = await _app()

    await app.process_update(_update("/presupuesto", 1, app.bot))
    assert "¿Para quién" in send_message.call_args.kwargs["text"]

    await app.process_update(_update("Juan López", 2, app.bot))

    assert send_message.call_count == 2
    assert "¿Qué trabajo" in send_message.call_args.kwargs["text"]
