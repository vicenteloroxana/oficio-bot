"""Flujo conversacional de /perfil: ver y editar datos del trabajador.

Ver CLAUDE.md — Momento 6. Muestra el perfil actual con botones para
editar nombre, oficio o subir logo.
"""
import os
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from database.db import actualizar_usuario, get_usuario, guardar_logo_path
from database.models import Usuario

ESPERANDO_CAMPO, ESPERANDO_NOMBRE, ESPERANDO_OFICIO, ESPERANDO_LOGO = range(4)

LOGO_DIR = Path("assets/logos")
MAX_LOGO_SIZE_MB = float(os.getenv("MAX_LOGO_SIZE_MB", "2"))


def _texto_perfil(usuario: Usuario) -> str:
    logo = "No configurado (se usará tu nombre en el PDF)" if not usuario.logo_path else "Configurado"
    return (
        f"👤 Tu perfil actual:\n"
        f"Nombre: {usuario.nombre}\n"
        f"Oficio: {usuario.oficio}\n"
        f"Logo:   {logo}\n\n"
        f"¿Qué querés cambiar?"
    )


_BOTONES = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Nombre", callback_data="perfil_editar:nombre"),
            InlineKeyboardButton("Oficio", callback_data="perfil_editar:oficio"),
            InlineKeyboardButton("Subir logo", callback_data="perfil_editar:logo"),
        ]
    ]
)


async def perfil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Punto de entrada de /perfil. Requiere estar registrado (ver ADR-003)."""
    usuario = await get_usuario(update.effective_user.id)
    if usuario is None:
        await update.message.reply_text("Todavía no estás registrado. Usá /start primero.")
        return ConversationHandler.END

    await update.message.reply_text(_texto_perfil(usuario), reply_markup=_BOTONES)
    return ESPERANDO_CAMPO


async def elegir_campo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback de los botones [Nombre] [Oficio] [Subir logo]: pide el valor nuevo."""
    query = update.callback_query
    await query.answer()
    _, campo = query.data.split(":")

    if campo == "nombre":
        await query.message.reply_text("¿Cómo te llamás o cuál es tu razón social?")
        return ESPERANDO_NOMBRE
    if campo == "oficio":
        await query.message.reply_text("¿Cuál es tu oficio?")
        return ESPERANDO_OFICIO
    await query.message.reply_text(
        f"Enviame la imagen de tu logo (PNG o JPG, máximo {MAX_LOGO_SIZE_MB:.0f}MB)"
    )
    return ESPERANDO_LOGO


async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el nombre nuevo."""
    valor = update.message.text.strip()
    if not valor:
        await update.message.reply_text("Necesito un nombre. ¿Cómo te llamás?")
        return ESPERANDO_NOMBRE

    await actualizar_usuario(update.effective_user.id, nombre=valor)
    await update.message.reply_text(f"✅ Nombre actualizado a {valor}.")
    return ConversationHandler.END


async def recibir_oficio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el oficio nuevo."""
    valor = update.message.text.strip()
    if not valor:
        await update.message.reply_text("Necesito un oficio. ¿Cuál es tu oficio?")
        return ESPERANDO_OFICIO

    await actualizar_usuario(update.effective_user.id, oficio=valor)
    await update.message.reply_text(f"✅ Oficio actualizado a {valor}.")
    return ConversationHandler.END


async def recibir_logo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida tamaño y guarda el logo enviado como foto."""
    foto = update.message.photo[-1]
    if foto.file_size and foto.file_size > MAX_LOGO_SIZE_MB * 1024 * 1024:
        await update.message.reply_text(
            f"La imagen supera los {MAX_LOGO_SIZE_MB:.0f}MB. Probá con una más liviana."
        )
        return ESPERANDO_LOGO

    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    logo_path = str(LOGO_DIR / f"{update.effective_user.id}.jpg")
    archivo = await foto.get_file()
    await archivo.download_to_drive(logo_path)

    await guardar_logo_path(update.effective_user.id, logo_path)
    await update.message.reply_text(
        "✅ Logo guardado. Aparecerá en todos tus próximos presupuestos."
    )
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la edición de perfil en curso."""
    await update.message.reply_text("Edición cancelada. Escribí /perfil para volver a empezar.")
    return ConversationHandler.END


perfil_handler = ConversationHandler(
    entry_points=[CommandHandler("perfil", perfil)],
    states={
        ESPERANDO_CAMPO: [CallbackQueryHandler(elegir_campo, pattern=r"^perfil_editar:")],
        ESPERANDO_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
        ESPERANDO_OFICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_oficio)],
        ESPERANDO_LOGO: [MessageHandler(filters.PHOTO, recibir_logo)],
    },
    fallbacks=[CommandHandler("cancel", cancelar)],
)
