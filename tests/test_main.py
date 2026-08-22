"""Tests de la lógica de selección polling/webhook en main.py."""
from main import config_webhook


def test_sin_railway_public_domain_usa_polling() -> None:
    assert config_webhook("token123", {}) is None


def test_con_railway_public_domain_arma_webhook() -> None:
    env = {"RAILWAY_PUBLIC_DOMAIN": "mi-bot.up.railway.app"}
    kwargs = config_webhook("token123", env)

    assert kwargs is not None
    assert kwargs["webhook_url"] == "https://mi-bot.up.railway.app/token123"
    assert kwargs["url_path"] == "token123"
    assert kwargs["port"] == 8080


def test_usa_puerto_de_railway_si_esta_seteado() -> None:
    env = {"RAILWAY_PUBLIC_DOMAIN": "mi-bot.up.railway.app", "PORT": "3000"}
    kwargs = config_webhook("token123", env)

    assert kwargs is not None
    assert kwargs["port"] == 3000
