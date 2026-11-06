import pytest
from src.lealtad.errores import ErroresBilletera, clienteDuplicado
from src.lealtad.programa import ProgramaLealtad


def testCrearClienteDuplicado():
    programa = ProgramaLealtad()
    programa.crearCliente("C001", "Ana Pérez", "ana@correo.com", "05-01-2026")

    with pytest.raises(ErroresBilletera) as error:
        programa.crearCliente("C001", "Ana Pérez", "ana@correo.com", "05-01-2026")

    assert error.value.codigo == clienteDuplicado