import pytest
from src.lealtad.errores import ErroresBilletera, clienteDuplicado, fechaInvalida, datosInvalidos
from src.lealtad.programa import ProgramaLealtad


def testCrearClienteDuplicado():
    programa = ProgramaLealtad()
    programa.crearCliente("C001", "Ana Pérez", "ana@correo.com", "05-01-2026")

    with pytest.raises(ErroresBilletera) as error:
        programa.crearCliente("C001", "Ana Pérez", "ana@correo.com", "05-01-2026")

    assert error.value.codigo == clienteDuplicado

def testCrearClienteConDatosInvalidos():
    programa = ProgramaLealtad()
    programa.crearCliente("C001", "Ana", "ana@correo.com", "05-01-2026")

    with pytest.raises(ErroresBilletera):
        programa.crearCliente("C002", "", "x@correo.com", "20-01-2026")  # falla por nombre

    # Como la operación falló, la fecha 06-01-2026 sigue siendo válida
    programa.crearCliente("C003", "Luis", "luis@correo.com", "06-01-2026")

def testCrearClienteFechaAnterior():
    programa = ProgramaLealtad()
    # Primera operación en 10-01-2026
    programa.crearCliente("C001", "Ana Pérez", "ana@correo.com", "10-01-2026")

    # Intentar operar en 05-01-2026 debe dar FECHA_INVALIDA
    with pytest.raises(ErroresBilletera) as error:
        programa.crearCliente("C002", "Carlos", "carlos@correo.com", "05-01-2026")

    assert error.value.codigo == fechaInvalida

def testCrearClienteConDatosInvalidos():
    programa = ProgramaLealtad()

    # Paso 3: Nombre vacío debe dar DATOS_INVALIDOS
    with pytest.raises(ErroresBilletera) as error_nombre:
        programa.crearCliente("C001", "", "ana@correo.com", "05-01-2026")
    assert error_nombre.value.codigo == datosInvalidos

    # Paso 4: Correo sin @ debe dar DATOS_INVALIDOS
    with pytest.raises(ErroresBilletera) as error_correo:
        programa.crearCliente("C002", "Pedro", "pedrocorreo.com", "05-01-2026")
    assert error_correo.value.codigo == datosInvalidos