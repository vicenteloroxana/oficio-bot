"""Flujo conversacional de /confirmar_envio: avisar que un presupuesto con
seña finalmente se le mandó al cliente, tras haber respondido "Todavía no"
en el momento de generarlo.

Sin esto, un trabajo quedaba trabado en estado 'presupuestado' para
siempre — el botón [Sí]/[Todavía no] de /presupuesto solo aparece una vez,
y tocar "Todavía no" no dejaba ningún rastro del trabajo_id para retomar
la confirmación más tarde. Mismo patrón que handlers/cobro.py y
handlers/reintentar_pdf.py: lista numerada de trabajos filtrados, el
usuario elige uno, se actúa sobre ese trabajo_id existente.
"""
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from database.db import get_trabajos_sin_confirmar_envio, marcar_sena_enviada
from database.models import Trabajo

ESPERANDO_TRABAJO = range(1)


def _texto_lista(trabajos: list[Trabajo]) -> str:
    """Arma la lista numerada de presupuestos con seña sin confirmar envío."""
    lineas = [
        f"{i}. {t.cliente_nombre} — {t.descripcion}"
        for i, t in enumerate(trabajos, start=1)
    ]
    return "¿Qué presupuesto le mandaste al cliente?\n\n" + "\n".join(lineas)


async def confirmar_envio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Punto de entrada de /confirmar_envio. Lista los presupuestos sin confirmar."""
    trabajos = await get_trabajos_sin_confirmar_envio(update.effective_user.id)
    if not trabajos:
        await update.message.reply_text("No tenés presupuestos pendientes de confirmar. 🎉")
        return ConversationHandler.END

    context.user_data["trabajos_sin_confirmar"] = trabajos
    await update.message.reply_text(_texto_lista(trabajos))
    return ESPERANDO_TRABAJO


async def recibir_trabajo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida el número elegido y marca ese trabajo como seña enviada."""
    trabajos: list[Trabajo] = context.user_data.pop("trabajos_sin_confirmar")
    try:
        indice = int(update.message.text.strip()) - 1
        if indice < 0 or indice >= len(trabajos):
            raise ValueError
    except ValueError:
        context.user_data["trabajos_sin_confirmar"] = trabajos
        await update.message.reply_text(
            f"Elegí un número entre 1 y {len(trabajos)}, o /cancel para salir."
        )
        return ESPERANDO_TRABAJO

    trabajo = trabajos[indice]
    await marcar_sena_enviada(trabajo.id)
    await update.message.reply_text(
        f"✅ Listo, {trabajo.cliente_nombre} — te aviso si no llega el pago a tiempo."
    )
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la confirmación en curso."""
    context.user_data.pop("trabajos_sin_confirmar", None)
    await update.message.reply_text(
        "Cancelado. Escribí /confirmar_envio para volver a intentar."
    )
    return ConversationHandler.END


confirmar_envio_handler = ConversationHandler(
    entry_points=[CommandHandler("confirmar_envio", confirmar_envio)],
    states={
        ESPERANDO_TRABAJO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_trabajo)],
    },
    fallbacks=[CommandHandler("cancel", cancelar)],
)
