"""Flujo conversacional de /start: registro inicial del trabajador.

Ver docs/adr/003-registro-usuario-start.md — 2 pasos (nombre → oficio),
mínimo indispensable para desbloquear /presupuesto. logo_path queda
en None y se completa después vía /perfil.
"""
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from database.db import crear_usuario, get_usuario
from database.models import Usuario

ESPERANDO_NOMBRE, ESPERANDO_OFICIO = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Punto de entrada de /start. Si el usuario ya existe, saluda y no repite el alta."""
    usuario = await get_usuario(update.effective_user.id)
    if usuario is not None:
        await update.message.reply_text(f"👋 ¡Hola de nuevo, {usuario.nombre}!")
        return ConversationHandler.END

    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente de gestión.\n\n¿Cómo te llamás o cuál es tu razón social?"
    )
    return ESPERANDO_NOMBRE


async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el nombre ingresado y pide el oficio."""
    nombre = update.message.text.strip()
    if not nombre:
        await update.message.reply_text("Necesito un nombre para continuar. ¿Cómo te llamás?")
        return ESPERANDO_NOMBRE

    context.user_data["nombre"] = nombre
    await update.message.reply_text("¿Cuál es tu oficio? (ej: plomero, electricista, pintor)")
    return ESPERANDO_OFICIO


async def recibir_oficio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el oficio, registra el usuario en la BD y cierra el flujo."""
    oficio = update.message.text.strip()
    if not oficio:
        await update.message.reply_text("Necesito un oficio para continuar. ¿Cuál es tu oficio?")
        return ESPERANDO_OFICIO

    usuario = Usuario(
        telegram_id=update.effective_user.id,
        nombre=context.user_data["nombre"],
        oficio=oficio,
    )
    await crear_usuario(usuario)
    context.user_data.clear()

    await update.message.reply_text(
        f"✅ Listo, {usuario.nombre}. Ya podés usar /presupuesto para crear tu primer presupuesto.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela el registro en curso."""
    context.user_data.clear()
    await update.message.reply_text("Registro cancelado. Escribí /start cuando quieras retomarlo.")
    return ConversationHandler.END


registro_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ESPERANDO_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
        ESPERANDO_OFICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_oficio)],
    },
    fallbacks=[CommandHandler("cancel", cancelar)],
)
