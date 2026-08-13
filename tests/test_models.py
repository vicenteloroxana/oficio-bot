"""Tests de validaciones de negocio en los modelos Pydantic."""
import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError

from database.models import Trabajo

_montos = st.floats(
    min_value=0.01, max_value=10_000_000, allow_nan=False, allow_infinity=False
)


def _trabajo(monto_total: float, monto_sena: float) -> Trabajo:
    return Trabajo(
        usuario_id=1,
        cliente_nombre="Juan López",
        descripcion="Pintura de living",
        monto_total=monto_total,
        monto_sena=monto_sena,
    )


@given(monto_total=_montos, extra=_montos)
def test_sena_mayor_al_total_siempre_rechazada(monto_total: float, extra: float) -> None:
    """Para cualquier monto_total, una seña que lo supera debe fallar la validación."""
    with pytest.raises(ValidationError):
        _trabajo(monto_total, monto_total + extra)


@given(monto_total=_montos, fraccion=st.floats(min_value=0, max_value=1))
def test_sena_hasta_el_total_siempre_aceptada(monto_total: float, fraccion: float) -> None:
    """Para cualquier monto_total, una seña entre 0 y el total debe ser válida."""
    trabajo = _trabajo(monto_total, monto_total * fraccion)
    assert trabajo.monto_sena <= trabajo.monto_total
