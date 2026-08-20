"""Tests del recordatorio automático (Momento 2): query de vencidos y callbacks."""
from functools import partial
from unittest.mock import AsyncMock, MagicMock

import pytest

from database.db import (
    crear_recordatorio,
    crear_trabajo,
    crear_usuario,
    get_connection,
    get_trabajo,
    get_trabajos_para_recordar,
    marcar_sena_enviada,
    responder_ultimo_recordatorio,
)
from database.models import RespuestaRecordatorio, Trabajo, Usuario
import handlers.recordatorio as recordatorio_mod
from handlers.recordatorio import confirmar_sena_enviada, responder_recordatorio


async def _trabajo_con_sena_enviada(db_path: str, dias_atras: int, usuario_id: int = 1) -> int:
    """Crea un trabajo, lo pasa a sena_enviada y le corre el reloj `dias_atras` días hacia atrás."""
    trabajo = Trabajo(
        usuario_id=usuario_id, cliente_nombre="Juan López", descripcion="Pintura",
        monto_total=180000, monto_sena=90000,
    )
    trabajo_id = await crear_trabajo(trabajo, db_path)
    await marcar_sena_enviada(trabajo_id, db_path)
    async with get_connection(db_path) as db:
        await db.execute(
            "UPDATE trabajos SET creado_en = datetime('now', ?) WHERE id = ?",
            (f"-{dias_atras} days", trabajo_id),
        )
        await db.commit()
    return trabajo_id


@pytest.mark.asyncio
async def test_get_trabajos_para_recordar_incluye_vencidos(db_path: str) -> None:
    """Un trabajo con seña enviada hace >= REMINDER_DAYS aparece en la lista."""
    await _trabajo_con_sena_enviada(db_path, dias_atras=5)

    trabajos = await get_trabajos_para_recordar(dias=3, db_path=db_path)

    assert len(trabajos) == 1
    assert trabajos[0].cliente_nombre == "Juan López"


@pytest.mark.asyncio
async def test_get_trabajos_para_recordar_excluye_recientes(db_path: str) -> None:
    """Un trabajo con seña enviada hace menos de REMINDER_DAYS no aparece."""
    await _trabajo_con_sena_enviada(db_path, dias_atras=1)

    trabajos = await get_trabajos_para_recordar(dias=3, db_path=db_path)

    assert trabajos == []


@pytest.mark.asyncio
async def test_get_trabajos_para_recordar_excluye_presupuestado(db_path: str) -> None:
    """Un trabajo que nunca pasó a sena_enviada no dispara recordatorio, aunque tenga días."""
    trabajo = Trabajo(
        usuario_id=1, cliente_nombre="María", descripcion="Cableado",
        monto_total=50000, monto_sena=20000,
    )
    trabajo_id = await crear_trabajo(trabajo, db_path)
    async with get_connection(db_path) as db:
        await db.execute(
            "UPDATE trabajos SET creado_en = datetime('now', '-10 days') WHERE id = ?",
            (trabajo_id,),
        )
        await db.commit()

    trabajos = await get_trabajos_para_recordar(dias=3, db_path=db_path)

    assert trabajos == []


@pytest.mark.asyncio
async def test_get_trabajos_para_recordar_excluye_marcado_pagado(db_path: str) -> None:
    """Un trabajo ya marcado como pagado no vuelve a aparecer aunque siga venciendo."""
    trabajo_id = await _trabajo_con_sena_enviada(db_path, dias_atras=10)
    await crear_recordatorio(trabajo_id, db_path)
    await responder_ultimo_recordatorio(trabajo_id, RespuestaRecordatorio.MARCADO_PAGADO, db_path)

    trabajos = await get_trabajos_para_recordar(dias=3, db_path=db_path)

    assert trabajos == []


@pytest.mark.asyncio
async def test_get_trabajos_para_recordar_reincluye_ignorado(db_path: str) -> None:
    """Un trabajo ignorado sigue apareciendo en el próximo ciclo (no queda silenciado)."""
    trabajo_id = await _trabajo_con_sena_enviada(db_path, dias_atras=10)
    await crear_recordatorio(trabajo_id, db_path)
    await responder_ultimo_recordatorio(trabajo_id, RespuestaRecordatorio.IGNORADO, db_path)

    trabajos = await get_trabajos_para_recordar(dias=3, db_path=db_path)

    assert len(trabajos) == 1


def _callback_update(data: str) -> MagicMock:
    update = MagicMock()
    update.callback_query.data = data
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    return update


@pytest.mark.asyncio
async def test_confirmar_sena_enviada_si_pasa_estado(db_path: str, monkeypatch) -> None:
    """Responder 'Sí' pasa el trabajo a sena_enviada."""
    await crear_usuario(Usuario(telegram_id=1, nombre="Carlos", oficio="pintor"), db_path)
    trabajo = Trabajo(
        usuario_id=1, cliente_nombre="Juan López", descripcion="Pintura",
        monto_total=180000, monto_sena=90000,
    )
    trabajo_id = await crear_trabajo(trabajo, db_path)
    monkeypatch.setattr(recordatorio_mod, "marcar_sena_enviada", partial(marcar_sena_enviada, db_path=db_path))

    update = _callback_update(f"sena_enviada:{trabajo_id}")
    await confirmar_sena_enviada(update, MagicMock())

    async with get_connection(db_path) as db:
        cursor = await db.execute("SELECT estado FROM trabajos WHERE id = ?", (trabajo_id,))
        fila = await cursor.fetchone()
    assert fila["estado"] == "sena_enviada"


@pytest.mark.asyncio
async def test_confirmar_sena_enviada_todavia_no_no_cambia_estado(db_path: str, monkeypatch) -> None:
    """Responder 'Todavía no' deja el trabajo como estaba (presupuestado)."""
    update = _callback_update("sena_enviada:no")
    await confirmar_sena_enviada(update, MagicMock())

    update.callback_query.edit_message_text.assert_called_once()


@pytest.mark.asyncio
async def test_responder_recordatorio_marcado_pagado(db_path: str, monkeypatch) -> None:
    """El botón [Marcar como pagado] registra la respuesta en el último recordatorio."""
    trabajo_id = await _trabajo_con_sena_enviada(db_path, dias_atras=5)
    await crear_recordatorio(trabajo_id, db_path)
    monkeypatch.setattr(
        recordatorio_mod, "responder_ultimo_recordatorio", partial(responder_ultimo_recordatorio, db_path=db_path)
    )
    monkeypatch.setattr(recordatorio_mod, "get_trabajo", partial(get_trabajo, db_path=db_path))

    update = _callback_update(f"recordatorio_pagado:{trabajo_id}")
    await responder_recordatorio(update, MagicMock())

    async with get_connection(db_path) as db:
        cursor = await db.execute(
            "SELECT respuesta FROM recordatorios WHERE trabajo_id = ?", (trabajo_id,)
        )
        fila = await cursor.fetchone()
    assert fila["respuesta"] == "marcado_pagado"


@pytest.mark.asyncio
async def test_responder_recordatorio_ignorar(db_path: str, monkeypatch) -> None:
    """El botón [Ignorar] registra la respuesta 'ignorado' sin tocar el estado del trabajo."""
    trabajo_id = await _trabajo_con_sena_enviada(db_path, dias_atras=5)
    await crear_recordatorio(trabajo_id, db_path)
    monkeypatch.setattr(
        recordatorio_mod, "responder_ultimo_recordatorio", partial(responder_ultimo_recordatorio, db_path=db_path)
    )

    update = _callback_update(f"recordatorio_ignorar:{trabajo_id}")
    await responder_recordatorio(update, MagicMock())

    async with get_connection(db_path) as db:
        cursor = await db.execute(
            "SELECT respuesta FROM recordatorios WHERE trabajo_id = ?", (trabajo_id,)
        )
        fila = await cursor.fetchone()
    assert fila["respuesta"] == "ignorado"
