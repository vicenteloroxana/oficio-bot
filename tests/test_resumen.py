"""Tests del resumen mensual (Momento 4): query agregada y formato de salida."""
from datetime import datetime
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest

from database.db import crear_trabajo, get_connection, get_resumen_mensual, marcar_cobrado, marcar_sena_enviada
from database.models import FormaPago, Trabajo
import handlers.resumen as resumen_mod
from handlers.resumen import _texto_resumen, resumen

MES = "2026-08"


def _trabajo(monto_total: float = 100000, monto_sena: float = 0) -> Trabajo:
    return Trabajo(
        usuario_id=1, cliente_nombre="Juan López", descripcion="Pintura living",
        monto_total=monto_total, monto_sena=monto_sena,
    )


async def _forzar_fecha(campo: str, trabajo_id: int, fecha: str, db_path: str) -> None:
    """Sobrescribe una fecha del trabajo para simular otro mes (creado_en/cobrado_en)."""
    async with get_connection(db_path) as db:
        await db.execute(f"UPDATE trabajos SET {campo} = ? WHERE id = ?", (fecha, trabajo_id))
        await db.commit()


@pytest.mark.asyncio
async def test_resumen_vacio_para_usuario_sin_trabajos(db_path: str) -> None:
    """Un usuario sin trabajos da un resumen todo en cero, sin romper."""
    datos = await get_resumen_mensual(1, MES, db_path)

    assert datos.monto_cobrado == 0
    assert datos.cantidad_cobrados == 0
    assert datos.monto_pendiente == 0
    assert datos.cantidad_pendientes == 0
    assert datos.cantidad_sin_sena == 0
    assert datos.total_trabajos == 0


@pytest.mark.asyncio
async def test_resumen_cuenta_cobrado_del_mes_por_cobrado_en(db_path: str) -> None:
    """Cobrado se filtra por cobrado_en del mes, no por creado_en."""
    trabajo_id = await crear_trabajo(_trabajo(monto_total=180000), db_path)
    await marcar_cobrado(trabajo_id, FormaPago.EFECTIVO, db_path)
    await _forzar_fecha("cobrado_en", trabajo_id, f"{MES}-15 10:00:00", db_path)
    await _forzar_fecha("creado_en", trabajo_id, "2026-01-01 10:00:00", db_path)

    datos = await get_resumen_mensual(1, MES, db_path)

    assert datos.monto_cobrado == 180000
    assert datos.cantidad_cobrados == 1


@pytest.mark.asyncio
async def test_resumen_excluye_cobrado_de_otro_mes(db_path: str) -> None:
    """Un trabajo cobrado en otro mes no cuenta como cobrado este mes."""
    trabajo_id = await crear_trabajo(_trabajo(), db_path)
    await marcar_cobrado(trabajo_id, FormaPago.EFECTIVO, db_path)
    await _forzar_fecha("cobrado_en", trabajo_id, "2026-01-15 10:00:00", db_path)

    datos = await get_resumen_mensual(1, MES, db_path)

    assert datos.monto_cobrado == 0
    assert datos.cantidad_cobrados == 0


@pytest.mark.asyncio
async def test_resumen_cuenta_pendiente_por_estado_actual_sin_importar_el_mes(db_path: str) -> None:
    """Pendiente es deuda viva por estado: no depende de cuándo se creó el trabajo."""
    trabajo_id = await crear_trabajo(_trabajo(monto_total=180000, monto_sena=90000), db_path)
    await marcar_sena_enviada(trabajo_id, db_path)
    await _forzar_fecha("creado_en", trabajo_id, "2026-01-05 10:00:00", db_path)

    datos = await get_resumen_mensual(1, MES, db_path)

    assert datos.monto_pendiente == 90000
    assert datos.cantidad_pendientes == 1
    assert datos.cantidad_sin_sena == 0


@pytest.mark.asyncio
async def test_resumen_cuenta_sin_sena_por_estado_actual_sin_importar_el_mes(db_path: str) -> None:
    """Sin seña es deuda viva por estado: un presupuestado de otro mes igual cuenta."""
    trabajo_id = await crear_trabajo(_trabajo(), db_path)
    await _forzar_fecha("creado_en", trabajo_id, "2026-01-05 10:00:00", db_path)

    datos = await get_resumen_mensual(1, MES, db_path)

    assert datos.cantidad_sin_sena == 1
    assert datos.cantidad_pendientes == 0
    assert datos.total_trabajos == 0  # total_trabajos sí es por creado_en del mes


@pytest.mark.asyncio
async def test_resumen_sin_sena_excluye_trabajo_ya_cobrado(db_path: str) -> None:
    """Caso real reportado: un trabajo sin seña (monto_sena=0) que ya se cobró
    (finalizado) no debe seguir contando como 'Sin seña' — ya no es deuda viva."""
    trabajo_id = await crear_trabajo(_trabajo(monto_total=200, monto_sena=0), db_path)
    await marcar_cobrado(trabajo_id, FormaPago.EFECTIVO, db_path)

    datos = await get_resumen_mensual(1, MES, db_path)

    assert datos.cantidad_sin_sena == 0


@pytest.mark.asyncio
async def test_resumen_distingue_sin_sena_de_presupuestado_sin_enviar(db_path: str) -> None:
    """Caso real: un presupuestado CON seña pedida (el trabajador respondió
    'Todavía no') no debe contar como 'sin seña' — son categorías distintas.
    Antes 'sin seña' medía solo estado=presupuestado, sin mirar el monto."""
    con_sena_id = await crear_trabajo(_trabajo(monto_total=10000, monto_sena=800), db_path)
    sin_sena_id = await crear_trabajo(_trabajo(monto_total=200, monto_sena=0), db_path)

    datos = await get_resumen_mensual(1, MES, db_path)

    assert datos.cantidad_sin_sena == 1  # solo sin_sena_id
    assert datos.cantidad_presupuestado_sin_enviar == 1  # solo con_sena_id


@pytest.mark.asyncio
async def test_resumen_trabajo_presupuestado_en_un_mes_y_avanzado_en_otro_no_desaparece(db_path: str) -> None:
    """Caso que motivó el cambio: creado_en julio, seña enviada en agosto — sigue

    apareciendo como pendiente al consultar agosto (con el filtro viejo por
    creado_en del mes, este trabajo no aparecía en ningún lado en agosto).
    """
    trabajo_id = await crear_trabajo(_trabajo(monto_total=180000, monto_sena=90000), db_path)
    await _forzar_fecha("creado_en", trabajo_id, "2026-07-01 10:00:00", db_path)
    await marcar_sena_enviada(trabajo_id, db_path)  # ocurre "en agosto"

    datos_agosto = await get_resumen_mensual(1, MES, db_path)

    assert datos_agosto.cantidad_pendientes == 1
    assert datos_agosto.monto_pendiente == 90000


@pytest.mark.asyncio
async def test_resumen_no_mezcla_usuarios(db_path: str) -> None:
    """El resumen de un usuario no incluye trabajos de otro, en ningún eje (fecha o estado)."""
    sin_sena = Trabajo(usuario_id=2, cliente_nombre="Otro", descripcion="X", monto_total=1000, monto_sena=0)
    sin_sena_id = await crear_trabajo(sin_sena, db_path)
    await _forzar_fecha("creado_en", sin_sena_id, f"{MES}-05 10:00:00", db_path)

    pendiente = Trabajo(usuario_id=2, cliente_nombre="Otro", descripcion="Y", monto_total=2000, monto_sena=500)
    pendiente_id = await crear_trabajo(pendiente, db_path)
    await marcar_sena_enviada(pendiente_id, db_path)

    datos = await get_resumen_mensual(1, MES, db_path)

    assert datos.total_trabajos == 0
    assert datos.cantidad_sin_sena == 0
    assert datos.cantidad_pendientes == 0
    assert datos.monto_pendiente == 0


def test_texto_resumen_sigue_formato_del_mockup() -> None:
    """El texto de salida respeta el formato de CLAUDE.md (Momento 4)."""
    from database.models import ResumenMensual

    datos = ResumenMensual(
        monto_cobrado=360000, cantidad_cobrados=4,
        monto_pendiente=180000, cantidad_pendientes=2,
        cantidad_sin_sena=1, cantidad_presupuestado_sin_enviar=1, total_trabajos=6,
    )
    texto = _texto_resumen(datos, datetime(2026, 8, 20))

    assert "Agosto 2026" in texto
    assert "Cobrado:    $360000 (4 trabajos)" in texto
    assert "Pendiente:  $180000 (2 trabajos)" in texto
    assert "Sin seña:   1 trabajo" in texto
    assert "Presupuestado sin enviar: 1 trabajo" in texto
    assert "Trabajos este mes: 6" in texto


@pytest.mark.asyncio
async def test_handler_resumen_responde_con_texto(db_path: str, monkeypatch) -> None:
    """El handler consulta la BD y responde el texto armado."""
    monkeypatch.setattr(resumen_mod, "get_resumen_mensual", partial(get_resumen_mensual, db_path=db_path))

    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()

    await resumen(update, MagicMock())

    update.message.reply_text.assert_called_once()
    assert "Tu resumen" in update.message.reply_text.call_args[0][0]
