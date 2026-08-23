"""Handler de /help y fallback para mensajes que ningún otro handler atiende.

Sin esto, un comando desconocido o un texto libre fuera de cualquier flujo
conversacional quedaba en silencio total — el usuario no tenía forma de
saber si el bot estaba roto o si el comando no existía.
"""
from telegram import Update
from telegram.ext import ContextTypes

TEXTO_AYUDA = (
    "🤖 Comandos disponibles:\n\n"
    "/presupuesto — crear un presupuesto nuevo\n"
    "/cobrar — registrar el cobro de un trabajo\n"
    "/pendientes — ver trabajos sin cobrar\n"
    "/resumen — ver el resumen del mes actual\n"
    "/clientes — ver historial de clientes\n"
    "/perfil — ver o editar tus datos (nombre, logo)\n"
    "/reintentar_pdf — regenerar el PDF de un trabajo que falló\n"
    "/confirmar_envio — avisar que mandaste un presupuesto pendiente\n"
    "/cancel — cancelar el paso en curso\n"
    "/help — ver esta ayuda"
)


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Punto de entrada de /help. Sin lógica de estado, solo responde el texto fijo."""
    await update.message.reply_text(TEXTO_AYUDA)


async def comando_no_reconocido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback para /comandos que no matchean ningún CommandHandler registrado."""
    await update.message.reply_text(
        "No reconozco ese comando. Escribí /help para ver los disponibles."
    )


async def mensaje_no_reconocido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback para texto libre fuera de cualquier flujo conversacional activo."""
    await update.message.reply_text(
        "No entendí ese mensaje. Escribí /help para ver los comandos disponibles."
    )
