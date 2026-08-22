"""Arranque del bot de Telegram.

Los handlers de cada comando se registran acá a medida que se
implementan (ver handlers/).
"""
import logging
import os

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from database.db import init_db
from handlers.ayuda import ayuda, comando_no_reconocido, mensaje_no_reconocido
from handlers.cobro import cobro_callback_handler, cobro_handler
from handlers.confirmar_envio import confirmar_envio_handler
from handlers.perfil import perfil_handler
from handlers.presupuesto import presupuesto_handler
from handlers.recordatorio import registrar_recordatorios
from handlers.registro import registro_handler
from handlers.reintentar_pdf import reintentar_pdf_handler
from handlers.resumen import resumen

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


def config_webhook(token: str, env: dict[str, str]) -> dict[str, str | int] | None:
    """Arma los kwargs de run_webhook, o None si corresponde polling.

    Railway inyecta RAILWAY_PUBLIC_DOMAIN solo cuando el servicio tiene
    dominio público — su presencia es la señal de "estamos en Railway".
    """
    dominio = env.get("RAILWAY_PUBLIC_DOMAIN")
    if not dominio:
        return None
    return {
        "listen": "0.0.0.0",
        "port": int(env.get("PORT", "8080")),
        "url_path": token,
        "webhook_url": f"https://{dominio}/{token}",
    }


def main() -> None:
    """Configura el bot y lo arranca en polling (local) o webhook (Railway).

    El modo se elige solo: si Railway inyectó RAILWAY_PUBLIC_DOMAIN (pasa
    automáticamente en cualquier servicio con dominio público, sin config
    manual) se usa webhook contra esa URL; si no, polling — el modo de
    desarrollo local que no requiere URL pública. Ver docs/adr/001.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en las variables de entorno")

    app = Application.builder().token(token).post_init(post_init).build()
    app.add_handler(registro_handler)
    app.add_handler(presupuesto_handler)
    app.add_handler(cobro_handler)
    app.add_handler(cobro_callback_handler)
    app.add_handler(confirmar_envio_handler)
    app.add_handler(reintentar_pdf_handler)
    app.add_handler(perfil_handler)
    app.add_handler(CommandHandler("resumen", resumen))
    app.add_handler(CommandHandler("help", ayuda))
    # Catch-all: van al final para no interceptar los handlers específicos de arriba.
    app.add_handler(MessageHandler(filters.COMMAND, comando_no_reconocido))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_no_reconocido))
    registrar_recordatorios(app)

    webhook_kwargs = config_webhook(token, os.environ)
    if webhook_kwargs:
        logger.info("Bot iniciado en modo webhook (%s)", webhook_kwargs["webhook_url"])
        app.run_webhook(**webhook_kwargs)
    else:
        logger.info("Bot iniciado en modo polling")
        app.run_polling()


if __name__ == "__main__":
    main()
