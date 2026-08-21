"""Recordatorio automático de pago de seña — Momento 2 (sin comando).

Ver CLAUDE.md — Momento 2. Un job periódico (JobQueue) revisa trabajos en
estado `sena_enviada` con más de REMINDER_DAYS días y sin recordatorio
marcado como pagado, y les manda un aviso con botones inline.

Fase 1: solo [Marcar como pagado] / [Ignorar] — sin [Reenviar link],
que depende de Mercado Pago (fase 2).
"""
import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from database.db import (
    crear_recordatorio,
    get_trabajo,
    get_trabajos_para_recordar,
    marcar_sena_enviada,
    responder_ultimo_recordatorio,
)
from database.models import RespuestaRecordatorio

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 3600  # cada cuánto se revisan trabajos pendientes


async def revisar_pendientes(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job periódico: manda recordatorio a cada trabajo vencido sin pagar."""
    dias = int(os.getenv("REMINDER_DAYS", "3"))
    trabajos = await get_trabajos_para_recordar(dias)

    for trabajo in trabajos:
        await crear_recordatorio(trabajo.id)
        await context.bot.send_message(
            chat_id=trabajo.usuario_id,
            text=(
                f"⏰ {trabajo.cliente_nombre} todavía no pagó "
                f"la seña del trabajo de {trabajo.descripcion}.\n\n¿Qué hacemos?"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Marcar como pagado", callback_data=f"recordatorio_pagado:{trabajo.id}"
                        ),
                        InlineKeyboardButton(
                            "Ignorar", callback_data=f"recordatorio_ignorar:{trabajo.id}"
                        ),
                    ]
                ]
            ),
        )


async def confirmar_sena_enviada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback del botón [Sí]/[Todavía no] tras enviar un presupuesto con seña."""
    query = update.callback_query
    await query.answer()
    _, trabajo_id = query.data.split(":")

    if trabajo_id == "no":
        await query.edit_message_text(
            "Dale, avisame cuando se lo mandes con /confirmar_envio."
        )
        return

    if await get_trabajo(int(trabajo_id)) is None:
        await query.edit_message_text("Esta selección ya expiró.")
        return

    await marcar_sena_enviada(int(trabajo_id))
    await query.edit_message_text("✅ Listo, te aviso si no llega el pago a tiempo.")


async def responder_recordatorio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback de [Marcar como pagado]/[Ignorar] en un recordatorio enviado."""
    query = update.callback_query
    await query.answer()
    accion, trabajo_id = query.data.split(":")
    trabajo_id = int(trabajo_id)

    if accion == "recordatorio_pagado":
        await responder_ultimo_recordatorio(trabajo_id, RespuestaRecordatorio.MARCADO_PAGADO)
        trabajo = await get_trabajo(trabajo_id)
        if trabajo is None:
            await query.edit_message_text("✅ Marcado como pagado.")
            return
        await query.edit_message_text(
            f"✅ Marcado como pagado — {trabajo.cliente_nombre}, seña ${trabajo.monto_sena:.0f}."
        )
    else:
        await responder_ultimo_recordatorio(trabajo_id, RespuestaRecordatorio.IGNORADO)
        await query.edit_message_text("Ok, te vuelvo a avisar más adelante.")


def registrar_recordatorios(app: Application) -> None:
    """Registra los callback handlers y agenda el job periódico de recordatorios."""
    app.add_handler(CallbackQueryHandler(confirmar_sena_enviada, pattern=r"^sena_enviada:"))
    app.add_handler(CallbackQueryHandler(responder_recordatorio, pattern=r"^recordatorio_(pagado|ignorar):"))
    app.job_queue.run_repeating(revisar_pendientes, interval=CHECK_INTERVAL_SECONDS, first=10)
