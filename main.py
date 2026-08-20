"""Arranque del bot de Telegram.

Los handlers de cada comando se registran acá a medida que se
implementan (ver handlers/).
"""
import logging
import os

from dotenv import load_dotenv
from telegram.ext import Application

from database.db import init_db
from handlers.presupuesto import presupuesto_handler
from handlers.recordatorio import registrar_recordatorios
from handlers.registro import registro_handler

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


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
    app.add_handler(registro_handler)
    app.add_handler(presupuesto_handler)
    registrar_recordatorios(app)

    logger.info("Bot iniciado")
    app.run_polling()


if __name__ == "__main__":
    main()
