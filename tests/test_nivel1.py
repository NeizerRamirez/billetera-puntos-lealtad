import pytest
from src.lealtad.errores import ErroresBilletera, clienteDuplicado, fechaInvalida, datosInvalidos, clienteNoEncontrado, montoInvalido
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


def testConsultarSaldoClienteNuevo():
    programa = ProgramaLealtad()
    programa.crearCliente("C001", "Ana Pérez", "ana@correo.com", "05-01-2026")
    assert programa.consultarSaldo("C001") == 0


def testConsultarSaldoClienteInexistente():
    programa = ProgramaLealtad()
    with pytest.raises(ErroresBilletera) as error:
        programa.consultarSaldo("C999")
    assert error.value.codigo == clienteNoEncontrado


def testCatalogoTieneCincoPremios():
    programa = ProgramaLealtad()
    catalogo = programa.consultarCatalogo()
    assert len(catalogo) == 5
    assert catalogo[0] == {"id": "P01", "nombre": "Café de cortesía", "costo": 100}


def testCatalogoDevuelveCopias():
    programa = ProgramaLealtad()
    programa.consultarCatalogo()[0]["costo"] = 1   # intento de alterar la copia
    assert programa.consultarCatalogo()[0]["costo"] == 100



def _programaConClienteAna():
    programa = ProgramaLealtad()
    programa.crearCliente("C001", "Ana Pérez", "ana@correo.com", "05-01-2026")
    return programa


def testCompraAcumulaYRedondeaHaciaAbajo():
    p = _programaConClienteAna()
    r1 = p.registrarCompra("C001", "500.00", "10-01-2026")
    assert (r1["idCompra"], r1["puntos"], r1["saldo"]) == ("C-1", 50, 50)
    r2 = p.registrarCompra("C001", "1234.50", "11-01-2026")
    assert (r2["idCompra"], r2["puntos"], r2["saldo"]) == ("C-2", 123, 173)


def testCompraMenorA10DaCeroPuntosPeroSeRegistra():
    p = _programaConClienteAna()
    p.registrarCompra("C001", "1234.50", "11-01-2026")
    r = p.registrarCompra("C001", "9.99", "12-01-2026")
    assert (r["idCompra"], r["puntos"]) == ("C-2", 0)


@pytest.mark.parametrize("monto", ["-5.00", "10.555", "abc", "0", "NaN", None])
def testMontoInvalido(monto):
    p = _programaConClienteAna()
    with pytest.raises(ErroresBilletera) as e:
        p.registrarCompra("C001", monto, "12-01-2026")
    assert e.value.codigo == montoInvalido


def testCompraFallidaNoCambiaNada():
    p = _programaConClienteAna()
    p.registrarCompra("C001", "500.00", "10-01-2026")
    with pytest.raises(ErroresBilletera):
        p.registrarCompra("C001", "-5.00", "11-01-2026")
    assert p.consultarSaldo("C001") == 50
    # el id no se "gastó" en la compra fallida
    assert p.registrarCompra("C001", "100.00", "11-01-2026")["idCompra"] == "C-2"