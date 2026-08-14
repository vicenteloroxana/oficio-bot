"""Flujo conversacional de /presupuesto: alta de un trabajo presupuestado.

Ver CLAUDE.md — Momento 1. 4 pasos (cliente → descripción → monto → seña),
guarda el Trabajo en estado `presupuestado`. Generación de PDF queda para
un PR aparte (services/pdf_service.py todavía no existe).
"""
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from database.db import crear_trabajo, get_usuario
from database.models import Trabajo

ESPERANDO_CLIENTE, ESPERANDO_DESCRIPCION, ESPERANDO_MONTO, ESPERANDO_SENA = range(4)


async def presupuesto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Punto de entrada de /presupuesto. Exige que el usuario ya esté registrado."""
    usuario = await get_usuario(update.effective_user.id)
    if usuario is None:
        await update.message.reply_text("Primero registrate con /start para poder presupuestar.")
        return ConversationHandler.END

    await update.message.reply_text("¿Para quién es el trabajo?")
    return ESPERANDO_CLIENTE


async def recibir_cliente(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el nombre del cliente y pide la descripción del trabajo."""
    cliente = update.message.text.strip()
    if not cliente:
        await update.message.reply_text("Necesito un nombre. ¿Para quién es el trabajo?")
        return ESPERANDO_CLIENTE

    context.user_data["cliente_nombre"] = cliente
    await update.message.reply_text("¿Qué trabajo vas a hacer?")
    return ESPERANDO_DESCRIPCION


async def recibir_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda la descripción del trabajo y pide el monto total."""
    descripcion = update.message.text.strip()
    if not descripcion:
        await update.message.reply_text("Necesito una descripción. ¿Qué trabajo vas a hacer?")
        return ESPERANDO_DESCRIPCION

    context.user_data["descripcion"] = descripcion
    await update.message.reply_text("¿Cuánto vas a cobrar en total?")
    return ESPERANDO_MONTO


async def recibir_monto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida y guarda el monto total, luego pregunta por la seña."""
    texto = update.message.text.strip().replace(".", "").replace(",", ".")
    try:
        monto = float(texto)
        if monto <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Ingresá un monto válido en números (ej: 180000).")
        return ESPERANDO_MONTO

    context.user_data["monto_total"] = monto
    await update.message.reply_text(
        "¿Pedís seña? Respondé con el monto (ej: 90000) o \"no\" si no pedís."
    )
    return ESPERANDO_SENA


async def recibir_sena(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida la seña, crea el Trabajo en la BD y cierra el flujo."""
    texto = update.message.text.strip().lower()
    monto_total = context.user_data["monto_total"]

    if texto in ("no", "0"):
        monto_sena = 0.0
    else:
        try:
            monto_sena = float(texto.replace(".", "").replace(",", "."))
        except ValueError:
            await update.message.reply_text(
                "Ingresá un monto de seña válido, o \"no\" si no pedís."
            )
            return ESPERANDO_SENA
        if monto_sena > monto_total:
            await update.message.reply_text(
                f"La seña no puede superar el total (${monto_total:.0f}). ¿Cuánto pedís de seña?"
            )
            return ESPERANDO_SENA

    trabajo = Trabajo(
        usuario_id=update.effective_user.id,
        cliente_nombre=context.user_data["cliente_nombre"],
        descripcion=context.user_data["descripcion"],
        monto_total=monto_total,
        monto_sena=monto_sena,
    )
    await crear_trabajo(trabajo)
    context.user_data.clear()

    await update.message.reply_text(
        f"✅ Presupuesto guardado.\n\n"
        f"Cliente: {trabajo.cliente_nombre}\n"
        f"Trabajo: {trabajo.descripcion}\n"
        f"Total:   ${trabajo.monto_total:.0f}\n"
        f"Seña:    ${trabajo.monto_sena:.0f}",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela el presupuesto en curso."""
    context.user_data.clear()
    await update.message.reply_text("Presupuesto cancelado. Escribí /presupuesto para empezar de nuevo.")
    return ConversationHandler.END


presupuesto_handler = ConversationHandler(
    entry_points=[CommandHandler("presupuesto", presupuesto)],
    states={
        ESPERANDO_CLIENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_cliente)],
        ESPERANDO_DESCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_descripcion)],
        ESPERANDO_MONTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_monto)],
        ESPERANDO_SENA: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_sena)],
    },
    fallbacks=[CommandHandler("cancel", cancelar)],
)
