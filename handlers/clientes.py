"""Flujo conversacional de /clientes: historial de clientes y trabajos (Momento 6).

Ver CLAUDE.md — Momento 6. 1 paso: lista clientes con agregado, el
trabajador elige un número y ve el detalle de sus trabajos.
"""
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from database.db import get_clientes_resumen, get_trabajos_de_cliente
from database.models import ClienteResumen, Trabajo

ESPERANDO_CLIENTE = range(1)

_ICONO_ESTADO = {
    "finalizado": "✅",
    "cancelado": "❌",
}


def _texto_lista(clientes: list[ClienteResumen]) -> str:
    """Arma la lista numerada de clientes para mostrar en el chat."""
    lineas = []
    for i, c in enumerate(clientes, start=1):
        plural = "trabajo" if c.cantidad_trabajos == 1 else "trabajos"
        partes = []
        if c.monto_cobrado > 0:
            partes.append(f"${c.monto_cobrado:.0f} cobrado")
        if c.tiene_pendiente:
            partes.append("pendiente de cobro")
        estado = ", ".join(partes) if partes else "sin cobros"
        lineas.append(f"{i}. {c.cliente_nombre} — {c.cantidad_trabajos} {plural} — {estado}")
    return "👥 Tus clientes\n\n" + "\n".join(lineas) + "\n\n¿Querés ver el detalle de alguno?"


def _texto_detalle(cliente_nombre: str, trabajos: list[Trabajo]) -> str:
    """Arma el detalle de trabajos de un cliente."""
    lineas = []
    total_cobrado = 0.0
    total_pendiente = 0.0
    for t in trabajos:
        icono = _ICONO_ESTADO.get(t.estado.value, "⏳")
        fecha = t.creado_en.strftime("%b %Y")
        lineas.append(f"{icono} {t.descripcion} — ${t.monto_total:.0f} — {fecha}")
        if t.estado.value == "finalizado":
            total_cobrado += t.monto_total
        elif t.estado.value != "cancelado":
            total_pendiente += t.monto_total

    separador = "─" * 21
    return (
        f"📋 {cliente_nombre}\n"
        f"{separador}\n" + "\n".join(lineas) + f"\n{separador}\n"
        f"Total cobrado: ${total_cobrado:.0f}\n"
        f"Total pendiente: ${total_pendiente:.0f}"
    )


async def clientes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Punto de entrada de /clientes. Lista el agregado por cliente."""
    lista = await get_clientes_resumen(update.effective_user.id)
    if not lista:
        await update.message.reply_text("Todavía no tenés clientes registrados.")
        return ConversationHandler.END

    context.user_data["clientes_lista"] = lista
    await update.message.reply_text(_texto_lista(lista))
    return ESPERANDO_CLIENTE


async def recibir_cliente(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Valida el número elegido y muestra el detalle de ese cliente."""
    lista: list[ClienteResumen] = context.user_data["clientes_lista"]
    try:
        indice = int(update.message.text.strip()) - 1
        if indice < 0 or indice >= len(lista):
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            f"Elegí un número entre 1 y {len(lista)}, o /cancel para salir."
        )
        return ESPERANDO_CLIENTE

    cliente_nombre = lista[indice].cliente_nombre
    trabajos = await get_trabajos_de_cliente(update.effective_user.id, cliente_nombre)
    await update.message.reply_text(_texto_detalle(cliente_nombre, trabajos))
    return ConversationHandler.END


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la consulta de clientes en curso."""
    context.user_data.pop("clientes_lista", None)
    await update.message.reply_text("Consulta cancelada. Escribí /clientes para empezar de nuevo.")
    return ConversationHandler.END


clientes_handler = ConversationHandler(
    entry_points=[CommandHandler("clientes", clientes)],
    states={
        ESPERANDO_CLIENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_cliente)],
    },
    fallbacks=[CommandHandler("cancel", cancelar)],
)
