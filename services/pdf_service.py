"""Generación del PDF de presupuesto con WeasyPrint.

Ver CLAUDE.md — Momento 1. El template usa placeholders $nombre con
string.Template (no hay Jinja2 instalado; str.format() no sirve acá
porque el CSS del template ya usa llaves {} para sus reglas).
"""
import html
import os
from pathlib import Path
from string import Template

from database.models import Trabajo, Usuario

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "presupuesto.html"
LOGO_DEFAULT_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo_default.png"
PDF_DIR = Path(os.getenv("PDF_DIR", "pdfs"))


def _formatear_monto(monto: float) -> str:
    """Formatea un monto como pesos argentinos: $180.000."""
    return f"${monto:,.0f}".replace(",", ".")


def _renderizar_html(usuario: Usuario, trabajo: Trabajo) -> str:
    """Arma el HTML del presupuesto, escapando los campos de texto libre
    (cliente, descripción) para que no rompan el template."""
    logo_path = Path(trabajo_logo) if (trabajo_logo := usuario.logo_path) else LOGO_DEFAULT_PATH
    plantilla = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return plantilla.substitute(
        nombre_trabajador=html.escape(usuario.nombre),
        oficio_trabajador=html.escape(usuario.oficio),
        logo_src=logo_path.resolve().as_uri(),
        cliente_nombre=html.escape(trabajo.cliente_nombre),
        descripcion=html.escape(trabajo.descripcion),
        fecha=trabajo.creado_en.strftime("%d/%m/%Y"),
        monto_sena=_formatear_monto(trabajo.monto_sena),
        monto_total=_formatear_monto(trabajo.monto_total),
    )


def generar_pdf(usuario: Usuario, trabajo: Trabajo) -> str:
    """Genera el PDF de un presupuesto y devuelve la ruta del archivo."""
    from weasyprint import HTML  # import diferido: requiere librerías nativas (Pango/Cairo)

    html_contenido = _renderizar_html(usuario, trabajo)

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = PDF_DIR / f"presupuesto_{trabajo.usuario_id}_{trabajo.id}.pdf"
    HTML(string=html_contenido, base_url=str(TEMPLATE_PATH)).write_pdf(str(pdf_path))

    return str(pdf_path)
