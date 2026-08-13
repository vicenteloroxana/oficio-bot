"""Arranque del bot de Telegram.

Los handlers de cada comando se registran acá a medida que se
implementan (ver handlers/). Por ahora solo /start está activo.
"""
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from database.db import init_db

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responde al comando /start con un mensaje de bienvenida."""
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente de gestión.\n\n"
        "Usá /presupuesto para crear un presupuesto nuevo."
    )


async def post_init(application: Application) -> None:
    """Inicializa la base de datos antes de que el bot empiece a recibir updates."""
    await init_db()
    logger.info("Base de datos inicializada")


def main() -> None:
    """Configura y arranca el bot en modo polling."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en las variables de entorno")

    app = Application.builder().token(token).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))

    logger.info("Bot iniciado")
    app.run_polling()


if __name__ == "__main__":
    main()
