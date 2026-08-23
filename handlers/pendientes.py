"""Handler de /pendientes: trabajos sin cobrar del todo (Momento 5).

Ver CLAUDE.md — Momento 5. Comando directo, sin ConversationHandler:
lista y ofrece cancelar por botón, reusando get_trabajos_pendientes
(ya usada por /cobrar) y marcar_cancelado (compartida con el
recordatorio automático, Momento 2).
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from database.db import get_trabajos_pendientes, marcar_cancelado


def _teclado(trabajo_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Cliente no aceptó", callback_data=f"pendiente_cancelar:{trabajo_id}")]]
    )


async def pendientes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Punto de entrada de /pendientes. Un mensaje por trabajo, con botón de cancelar."""
    trabajos = await get_trabajos_pendientes(update.effective_user.id)
    if not trabajos:
        await update.message.reply_text("No tenés trabajos pendientes de cobro. 🎉")
        return

    await update.message.reply_text("📋 Pendientes:")
    for trabajo in trabajos:
        await update.message.reply_text(
            f"{trabajo.cliente_nombre} — {trabajo.descripcion} ({trabajo.estado.value})",
            reply_markup=_teclado(trabajo.id),
        )


async def cancelar_pendiente(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback de [Cliente no aceptó] en la lista de /pendientes."""
    query = update.callback_query
    await query.answer()
    _, trabajo_id = query.data.split(":")

    await marcar_cancelado(int(trabajo_id))
    await query.edit_message_text("Ok, trabajo cancelado.")


pendientes_callback_handler = CallbackQueryHandler(cancelar_pendiente, pattern=r"^pendiente_cancelar:")
