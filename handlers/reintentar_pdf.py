"""Flujo conversacional de /reintentar_pdf: regenerar el PDF de un trabajo
que agotó los reintentos automáticos de /presupuesto (pdf_error = 1).

Mismo patrón que handlers/cobro.py: lista numerada de trabajos filtrados,
el usuario elige uno, se actúa sobre ese trabajo_id existente — nunca se
crea un Trabajo nuevo (evita el duplicado que generaría correr /presupuesto
de nuevo con los mismos datos).
"""
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from database.db import get_trabajos_con_pdf_error, get_usuario
from database.models import Trabajo
from handlers.presupuesto import _generar_y_adjuntar_pdf

ESPERANDO_TRABAJO = range(1)


def _texto_lista(trabajos: list[Trabajo]) -> str:
    """Arma la lista numerada de trabajos con PDF pendiente de regenerar."""
    lineas = [
        f"{i}. {t.cliente_nombre} — {t.descripcion}"
        for i, t in enumerate(trabajos, start=1)
    ]
    return "¿De qué trabajo reintento el PDF?\n\n" + "\n".join(lineas)


async def reintentar_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Punto de entrada de /reintentar_pdf. Lista los trabajos con pdf_error=1."""
    trabajos = await get_trabajos_con_pdf_error(update.effective_user.id)
    if not trabajos:
        await update.message.reply_text("No tenés PDFs pendientes de regenerar. 🎉")
        return ConversationHandler.END

    context.user_data["trabajos_pdf_error"] = trabajos
    await update.message.reply_text(_texto_lista(trabajos))
    return ESPERANDO_TRABAJO


async def recibir_trabajo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida el número elegido y reintenta el PDF sobre ese trabajo existente."""
    trabajos: list[Trabajo] = context.user_data.pop("trabajos_pdf_error")
    try:
        indice = int(update.message.text.strip()) - 1
        if indice < 0 or indice >= len(trabajos):
            raise ValueError
    except ValueError:
        context.user_data["trabajos_pdf_error"] = trabajos
        await update.message.reply_text(
            f"Elegí un número entre 1 y {len(trabajos)}, o /cancel para salir."
        )
        return ESPERANDO_TRABAJO

    trabajo = trabajos[indice]
    usuario = await get_usuario(update.effective_user.id)
    await _generar_y_adjuntar_pdf(update, usuario, trabajo, trabajo.id)
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela el reintento en curso."""
    context.user_data.pop("trabajos_pdf_error", None)
    await update.message.reply_text(
        "Cancelado. Escribí /reintentar_pdf para volver a intentar."
    )
    return ConversationHandler.END


reintentar_pdf_handler = ConversationHandler(
    entry_points=[CommandHandler("reintentar_pdf", reintentar_pdf)],
    states={
        ESPERANDO_TRABAJO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_trabajo)],
    },
    fallbacks=[CommandHandler("cancel", cancelar)],
)
