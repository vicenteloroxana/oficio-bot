"""Tests de services/pdf_service.py: armado del HTML y formato de montos."""
from datetime import datetime

from database.models import Trabajo, Usuario
from services.pdf_service import LOGO_DEFAULT_PATH, _formatear_monto, _renderizar_html


def _usuario(logo_path: str | None = None) -> Usuario:
    return Usuario(telegram_id=1, nombre="Carlos Rodríguez", oficio="electricista", logo_path=logo_path)


def _trabajo(cliente: str = "Juan López", descripcion: str = "Cableado") -> Trabajo:
    return Trabajo(
        usuario_id=1, cliente_nombre=cliente, descripcion=descripcion,
        monto_total=180000, monto_sena=90000, creado_en=datetime(2026, 8, 13),
    )


def test_formatear_monto_usa_punto_como_separador_de_miles() -> None:
    assert _formatear_monto(180000) == "$180.000"


def test_formatear_monto_redondea_a_entero() -> None:
    assert _formatear_monto(89999.6) == "$90.000"


def test_renderizar_html_incluye_los_datos_del_presupuesto() -> None:
    contenido = _renderizar_html(_usuario(), _trabajo())

    assert "Carlos Rodríguez" in contenido
    assert "electricista" in contenido
    assert "Juan López" in contenido
    assert "$180.000" in contenido
    assert "$90.000" in contenido
    assert "13/08/2026" in contenido


def test_renderizar_html_escapa_texto_libre_del_cliente() -> None:
    """cliente_nombre/descripcion vienen de Telegram — no deben romper el HTML."""
    contenido = _renderizar_html(_usuario(), _trabajo(cliente="<script>alert(1)</script>"))

    assert "<script>" not in contenido
    assert "&lt;script&gt;" in contenido


def test_renderizar_html_usa_logo_default_si_usuario_no_tiene() -> None:
    contenido = _renderizar_html(_usuario(logo_path=None), _trabajo())

    assert LOGO_DEFAULT_PATH.resolve().as_uri() in contenido
