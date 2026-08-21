"""Flujo conversacional de /presupuesto: alta de un trabajo presupuestado.

Ver CLAUDE.md — Momento 1. 4 pasos (cliente → descripción → monto → seña),
guarda el Trabajo en estado `presupuestado`, genera el PDF y lo envía.
"""
import asyncio
import logging
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from database.db import (
    crear_trabajo,
    get_usuario,
    guardar_pdf_path,
    limpiar_pdf_error,
    marcar_pdf_error,
)
from database.models import Trabajo
from services.pdf_service import generar_pdf

logger = logging.getLogger(__name__)

ESPERANDO_CLIENTE, ESPERANDO_DESCRIPCION, ESPERANDO_MONTO, ESPERANDO_SENA = range(4)
MAX_INTENTOS_PDF = 3
ESPERA_ENTRE_INTENTOS_SEG = 2


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


async def _generar_y_adjuntar_pdf(
    update: Update, usuario, trabajo: Trabajo, trabajo_id: int
) -> None:
    """Reintenta generar_pdf hasta MAX_INTENTOS_PDF veces y adjunta el resultado.

    Si se agotan los intentos, marca pdf_error=True en el trabajo y avisa
    al usuario — el Trabajo en sí ya está guardado, no se pierde nada.
    """
    for intento in range(1, MAX_INTENTOS_PDF + 1):
        try:
            # WeasyPrint es sync — se corre en un thread aparte para no bloquear el event loop.
            pdf_path = await asyncio.to_thread(generar_pdf, usuario, trabajo)
            await guardar_pdf_path(trabajo_id, pdf_path)
            await limpiar_pdf_error(trabajo_id)
            pdf_bytes = await asyncio.to_thread(Path(pdf_path).read_bytes)
            await update.message.reply_document(pdf_bytes, filename="presupuesto.pdf")
            return
        except Exception:
            logger.exception(
                "Intento %s/%s: fallo al generar/enviar el PDF del trabajo %s",
                intento, MAX_INTENTOS_PDF, trabajo_id,
            )
            if intento < MAX_INTENTOS_PDF:
                await asyncio.sleep(ESPERA_ENTRE_INTENTOS_SEG)

    await marcar_pdf_error(trabajo_id)
    await update.message.reply_text(
        "⚠️ El presupuesto quedó guardado, pero no pude generar el PDF tras "
        f"{MAX_INTENTOS_PDF} intentos. Podés seguir sin el PDF por ahora — acordá "
        "la seña con el cliente igual, y cuando cobres usá /cobrar. Usá "
        "/reintentar_pdf cuando quieras volver a intentar generarlo."
    )


async def _guardar_y_enviar_presupuesto(
    update: Update, context: ContextTypes.DEFAULT_TYPE, trabajo: Trabajo
) -> None:
    """Persiste el Trabajo, genera su PDF y lo envía por chat."""
    trabajo_id = await crear_trabajo(trabajo)
    trabajo = trabajo.model_copy(update={"id": trabajo_id})
    context.user_data.clear()

    usuario = await get_usuario(update.effective_user.id)
    await update.message.reply_text(
        f"✅ Presupuesto guardado.\n\n"
        f"Cliente: {trabajo.cliente_nombre}\n"
        f"Trabajo: {trabajo.descripcion}\n"
        f"Total:   ${trabajo.monto_total:.0f}\n"
        f"Seña:    ${trabajo.monto_sena:.0f}",
        reply_markup=ReplyKeyboardRemove(),
    )

    await _generar_y_adjuntar_pdf(update, usuario, trabajo, trabajo_id)

    if trabajo.monto_sena > 0:
        # El recordatorio automático (Momento 2) solo arranca a contar una vez
        # confirmado que el presupuesto ya llegó al cliente.
        await update.message.reply_text(
            f"¿Ya le mandaste este presupuesto a {trabajo.cliente_nombre}?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Sí", callback_data=f"sena_enviada:{trabajo.id}"),
                        InlineKeyboardButton("Todavía no", callback_data="sena_enviada:no"),
                    ]
                ]
            ),
        )


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
    await _guardar_y_enviar_presupuesto(update, context, trabajo)
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
