"""Flujo conversacional de /cobrar: registrar el cobro final de un trabajo.

Ver CLAUDE.md — Momento 3. 2 pasos: elegir el trabajo pendiente de una lista
numerada, luego elegir la forma de pago con botones. Cierra el trabajo en
estado `finalizado` con `cobrado_en` y `forma_pago`.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from database.db import get_trabajos_pendientes, marcar_cobrado
from database.models import FormaPago, Trabajo

ESPERANDO_TRABAJO = range(1)

_ETIQUETAS_FORMA_PAGO = {
    FormaPago.EFECTIVO: "Efectivo",
    FormaPago.TRANSFERENCIA: "Transferencia",
    FormaPago.MP: "MP",
}


def _resto_a_cobrar(trabajo: Trabajo) -> float:
    """Lo que falta cobrar: si ya se cobró la seña, el saldo; si no, el total."""
    if trabajo.estado == "sena_cobrada":
        return trabajo.monto_total - trabajo.monto_sena
    return trabajo.monto_total


def _texto_lista(trabajos: list[Trabajo]) -> str:
    """Arma la lista numerada de trabajos pendientes para mostrar en el chat."""
    lineas = [
        f"{i}. {t.cliente_nombre} — {t.descripcion} (pendiente)"
        for i, t in enumerate(trabajos, start=1)
    ]
    return "¿Qué trabajo cerrás?\n\n" + "\n".join(lineas)


async def cobrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Punto de entrada de /cobrar. Lista los trabajos pendientes del usuario."""
    trabajos = await get_trabajos_pendientes(update.effective_user.id)
    if not trabajos:
        await update.message.reply_text("No tenés trabajos pendientes de cobro. 🎉")
        return ConversationHandler.END

    context.user_data["trabajos_pendientes"] = trabajos
    await update.message.reply_text(_texto_lista(trabajos))
    return ESPERANDO_TRABAJO


async def recibir_trabajo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida el número elegido y pregunta la forma de pago del resto a cobrar."""
    trabajos: list[Trabajo] = context.user_data["trabajos_pendientes"]
    try:
        indice = int(update.message.text.strip()) - 1
        if indice < 0 or indice >= len(trabajos):
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            f"Elegí un número entre 1 y {len(trabajos)}, o /cancel para salir."
        )
        return ESPERANDO_TRABAJO

    trabajo = trabajos[indice]
    context.user_data["trabajo_cobrado"] = trabajo
    resto = _resto_a_cobrar(trabajo)

    if trabajo.monto_sena > 0 and trabajo.estado == "sena_cobrada":
        aviso = f"El trabajo con {trabajo.cliente_nombre} tenía seña de ${trabajo.monto_sena:.0f} pagada.\n"
    else:
        aviso = ""

    await update.message.reply_text(
        f"{aviso}Resta: ${resto:.0f}\n\n¿Cómo cobraste?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(etiqueta, callback_data=f"cobro_forma:{forma.value}")
                    for forma, etiqueta in _ETIQUETAS_FORMA_PAGO.items()
                ]
            ]
        ),
    )
    return ConversationHandler.END


async def recibir_forma_pago(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback de los botones de forma de pago: cierra el trabajo."""
    query = update.callback_query
    await query.answer()
    _, forma_pago = query.data.split(":")

    trabajo: Trabajo = context.user_data.pop("trabajo_cobrado", None)
    if trabajo is None:
        await query.edit_message_text("Esta selección ya expiró. Usá /cobrar de nuevo.")
        return

    await marcar_cobrado(trabajo.id, FormaPago(forma_pago))
    await query.edit_message_text(
        f"✅ Trabajo cerrado.\n"
        f"{trabajo.cliente_nombre} — {trabajo.descripcion}\n"
        f"Total cobrado: ${trabajo.monto_total:.0f} 💰"
    )


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela el cobro en curso."""
    context.user_data.pop("trabajos_pendientes", None)
    await update.message.reply_text("Cobro cancelado. Escribí /cobrar para empezar de nuevo.")
    return ConversationHandler.END


cobro_handler = ConversationHandler(
    entry_points=[CommandHandler("cobrar", cobrar)],
    states={
        ESPERANDO_TRABAJO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_trabajo)],
    },
    fallbacks=[CommandHandler("cancel", cancelar)],
)

cobro_callback_handler = CallbackQueryHandler(recibir_forma_pago, pattern=r"^cobro_forma:")
