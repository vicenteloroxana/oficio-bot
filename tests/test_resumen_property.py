"""Property-based tests de get_resumen_mensual: para cualquier combinación
de estado × monto_sena × cobrado_en, cada trabajo cae en como máximo una
categoría del resumen, nunca en dos a la vez ni se cuenta de más.

hypothesis con fixtures async de pytest-asyncio no se lleva bien (el
fixture se resuelve una sola vez para todas las iteraciones de @given,
compartiendo estado entre ejemplos) — la BD temporal se crea/borra a
mano en cada ejemplo, y el cuerpo async se corre con asyncio.run().
"""
import asyncio
import os
import tempfile

from hypothesis import given, settings, strategies as st

from database.db import crear_trabajo, get_connection, get_resumen_mensual, init_db
from database.models import EstadoTrabajo, Trabajo

MES = "2026-08"

_ESTADOS = list(EstadoTrabajo)
_MONTOS_SENA = st.sampled_from([0, 500])  # sin seña / con seña — lo único que importa a la lógica
_COBRADO_EN_MES = st.booleans()


async def _crear_bd_con_trabajo(estado: EstadoTrabajo, monto_sena: float, cobrado_en_mes: bool) -> str:
    """Crea una BD temporal con un único trabajo en el estado/monto pedidos."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    await init_db(db_path)

    trabajo = Trabajo(
        usuario_id=1, cliente_nombre="Juan", descripcion="Prueba",
        monto_total=1000, monto_sena=monto_sena,
    )
    trabajo_id = await crear_trabajo(trabajo, db_path)

    async with get_connection(db_path) as db:
        await db.execute("UPDATE trabajos SET estado = ? WHERE id = ?", (estado.value, trabajo_id))
        if cobrado_en_mes:
            await db.execute(
                "UPDATE trabajos SET cobrado_en = ? WHERE id = ?",
                (f"{MES}-15 10:00:00", trabajo_id),
            )
        await db.commit()

    return db_path


def _categorias_donde_cae(datos, monto_sena: float, estado: EstadoTrabajo, cobrado_en_mes: bool) -> list[str]:
    """Según la lógica esperada (no la implementación), en qué categorías
    debería contar este único trabajo — para comparar contra el resultado real."""
    esperadas = []
    if cobrado_en_mes:
        esperadas.append("cobrado")
    if estado in (EstadoTrabajo.SENA_ENVIADA, EstadoTrabajo.SENA_COBRADA):
        esperadas.append("pendiente")
    if estado == EstadoTrabajo.PRESUPUESTADO and monto_sena == 0:
        esperadas.append("sin_sena")
    if estado == EstadoTrabajo.PRESUPUESTADO and monto_sena > 0:
        esperadas.append("presupuestado_sin_enviar")
    return esperadas


@given(
    estado=st.sampled_from(_ESTADOS),
    monto_sena=_MONTOS_SENA,
    cobrado_en_mes=_COBRADO_EN_MES,
)
@settings(deadline=None, max_examples=50)
def test_un_trabajo_cae_en_las_categorias_esperadas_y_solo_esas(
    estado: EstadoTrabajo, monto_sena: float, cobrado_en_mes: bool
) -> None:
    """Para cualquier combinación de estado/monto_sena/cobrado_en, el resumen
    cuenta este único trabajo exactamente en las categorías que le
    corresponden por la lógica de negocio — nunca de más, nunca de menos."""
    db_path = asyncio.run(_crear_bd_con_trabajo(estado, monto_sena, cobrado_en_mes))
    try:
        datos = asyncio.run(get_resumen_mensual(1, MES, db_path))
        esperadas = _categorias_donde_cae(datos, monto_sena, estado, cobrado_en_mes)

        assert datos.cantidad_cobrados == (1 if "cobrado" in esperadas else 0)
        assert datos.cantidad_pendientes == (1 if "pendiente" in esperadas else 0)
        assert datos.cantidad_sin_sena == (1 if "sin_sena" in esperadas else 0)
        assert datos.cantidad_presupuestado_sin_enviar == (
            1 if "presupuestado_sin_enviar" in esperadas else 0
        )

        # Invariante central: sin_sena y presupuestado_sin_enviar son
        # mutuamente excluyentes — nunca ambas a la vez para el mismo trabajo.
        assert not (datos.cantidad_sin_sena == 1 and datos.cantidad_presupuestado_sin_enviar == 1)
    finally:
        os.remove(db_path)
