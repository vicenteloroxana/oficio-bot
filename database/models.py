"""Modelos Pydantic para las tablas de la base de datos.

Estas clases validan los datos antes de persistirlos en SQLite.
No son un ORM — database/db.py usa aio-sqlite directamente con
queries planas, y estos modelos garantizan que lo que se guarda
cumple las reglas de negocio.
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Oficio(str, Enum):
    """Oficios soportados. Se puede extender sin romper datos existentes."""
    PLOMERO = "plomero"
    ELECTRICISTA = "electricista"
    PINTOR = "pintor"
    PROFESOR = "profesor_particular"
    OTRO = "otro"


class Usuario(BaseModel):
    """Trabajador independiente registrado en el bot."""
    telegram_id: int
    nombre: str = Field(min_length=1, max_length=100)
    oficio: str
    logo_path: str | None = None
    creado_en: datetime = Field(default_factory=datetime.now)


class EstadoTrabajo(str, Enum):
    """Estados posibles de un trabajo, en orden del flujo normal."""
    PRESUPUESTADO = "presupuestado"
    SENA_ENVIADA = "sena_enviada"
    SENA_COBRADA = "sena_cobrada"
    FINALIZADO = "finalizado"
    CANCELADO = "cancelado"


class Trabajo(BaseModel):
    """Un trabajo presupuestado para un cliente."""
    id: int | None = None
    usuario_id: int
    cliente_nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = Field(min_length=1)
    monto_total: float = Field(gt=0)
    monto_sena: float = Field(ge=0)
    estado: EstadoTrabajo = EstadoTrabajo.PRESUPUESTADO
    pdf_path: str | None = None
    pdf_error: bool = Field(default=False)
    forma_pago: str | None = None
    creado_en: datetime = Field(default_factory=datetime.now)
    cobrado_en: datetime | None = None

    @field_validator("monto_sena")
    @classmethod
    def sena_no_supera_total(cls, v: float, info) -> float:
        """La seña nunca puede ser mayor que el monto total del trabajo."""
        monto_total = info.data.get("monto_total")
        if monto_total is not None and v > monto_total:
            raise ValueError("monto_sena no puede superar monto_total")
        return v


class FormaPago(str, Enum):
    """Formas de cobro del monto final de un trabajo."""
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"
    MP = "mp"


class RespuestaRecordatorio(str, Enum):
    """Qué pasó tras enviar un recordatorio de pago."""
    IGNORADO = "ignorado"
    REENVIAR = "reenviar"
    MARCADO_PAGADO = "marcado_pagado"
    CLIENTE_NO_ACEPTO = "cliente_no_acepto"


class Recordatorio(BaseModel):
    """Registro de un recordatorio de pago enviado por mora."""
    id: int | None = None
    trabajo_id: int
    enviado_en: datetime = Field(default_factory=datetime.now)
    respuesta: RespuestaRecordatorio | None = None


class ResumenMensual(BaseModel):
    """Resumen agregado de un usuario para un mes (Momento 4 — /resumen)."""
    monto_cobrado: float = Field(ge=0)
    cantidad_cobrados: int = Field(ge=0)
    monto_pendiente: float = Field(ge=0)
    cantidad_pendientes: int = Field(ge=0)
    cantidad_sin_sena: int = Field(ge=0)
    cantidad_presupuestado_sin_enviar: int = Field(ge=0)
    total_trabajos: int = Field(ge=0)
