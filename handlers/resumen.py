"""Handler de /resumen: resumen agregado del mes actual (Momento 4).

Ver CLAUDE.md — Momento 4. Comando directo, sin flujo conversacional:
la lógica no trivial está en la query (`get_resumen_mensual`), no acá.
"""
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_resumen_mensual
from database.models import ResumenMensual

_MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _texto_resumen(resumen: ResumenMensual, fecha: datetime) -> str:
    """Arma el texto del resumen según el formato de CLAUDE.md."""
    titulo = f"{_MESES[fecha.month - 1].capitalize()} {fecha.year}"
    return (
        f"📊 Tu resumen — {titulo}\n\n"
        f"✅ Cobrado:    ${resumen.monto_cobrado:.0f} ({resumen.cantidad_cobrados} trabajos)\n"
        f"⏳ Pendiente:  ${resumen.monto_pendiente:.0f} ({resumen.cantidad_pendientes} trabajos)\n"
        f"❌ Sin seña:   {resumen.cantidad_sin_sena} trabajo(s)\n\n"
        f"Trabajos este mes: {resumen.total_trabajos}"
    )


async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Punto de entrada de /resumen. Sin lógica de estado, solo consulta y responde."""
    ahora = datetime.now()
    mes = ahora.strftime("%Y-%m")
    datos = await get_resumen_mensual(update.effective_user.id, mes)
    await update.message.reply_text(_texto_resumen(datos, ahora))
