import pytest
from src.lealtad.errores import ErroresBilletera, clienteDuplicado, fechaInvalida, datosInvalidos, clienteNoEncontrado, montoInvalido, premioNoEncontrado, premioSinStock, saldoInsuficiente
from src.lealtad.programa import ProgramaLealtad
from src.lealtad.config import stockInicial


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


def _programaConSaldo173():
    p = _programaConClienteAna()
    p.registrarCompra("C001", "500.00", "10-01-2026")
    p.registrarCompra("C001", "1234.50", "11-01-2026")
    return p


def testCanjeExitoso():
    p = _programaConSaldo173()
    r = p.canjearPremio("C001", "P01", "15-01-2026")
    assert (r["puntosDescontados"], r["saldo"]) == (100, 73)


def testCanjeSaldoInsuficienteNoCambiaNada():
    p = _programaConSaldo173()
    p.canjearPremio("C001", "P01", "15-01-2026")
    with pytest.raises(ErroresBilletera) as e:
        p.canjearPremio("C001", "P02", "15-01-2026")
    assert e.value.codigo == saldoInsuficiente
    assert p.consultarSaldo("C001") == 73
    assert p._catalogo["P02"].stock == stockInicial   # el stock tampoco cambió


def testPremioInexistente():
    p = _programaConSaldo173()
    with pytest.raises(ErroresBilletera) as e:
        p.canjearPremio("C001", "P99", "15-01-2026")
    assert e.value.codigo == premioNoEncontrado


def testSinStockSeValidaAntesQueSaldo():
    p = _programaConClienteAna()            # saldo 0
    p._catalogo["P01"].stock = 0
    with pytest.raises(ErroresBilletera) as e:
        p.canjearPremio("C001", "P01", "15-01-2026")
    assert e.value.codigo == premioSinStock   # no saldoInsuficiente

def testCanjeConFechaAnteriorALaUltimaOperacion():
    p = _programaConSaldo173()              # última operación: 11-01-2026
    with pytest.raises(ErroresBilletera) as e:
        p.canjearPremio("C001", "P01", "05-01-2026")
    assert e.value.codigo == fechaInvalida
    assert p.consultarSaldo("C001") == 173  # no cambió nada


from datetime import date

def test_prueba4_historial_completo():
    p = ProgramaLealtad()
    p.crearCliente("C001", "Jorge Mora", "jorge@correo.com", "01-03-2026")
    p.registrarCompra("C001", "80000.00", "02-03-2026")
    p.canjearPremio("C001", "P05", "03-03-2026")
    p.canjearPremio("C001", "P05", "04-03-2026")
    with pytest.raises(ErroresBilletera) as e:
        p.canjearPremio("C001", "P05", "05-03-2026")
    assert e.value.codigo == saldoInsuficiente

    h = p.consultarHistorial("C001")
    assert [(m["tipo"], m["puntos"], m["fecha"], m["referencia"]) for m in h] == [
        ("ACUMULACION", 8000, date(2026, 3, 2), "C-1"),
        ("CANJE", -4000, date(2026, 3, 3), "P05"),
        ("CANJE", -4000, date(2026, 3, 4), "P05"),
    ]
    assert sum(m["puntos"] for m in h) == p.consultarSaldo("C001") == 0


def test_prueba5_operaciones_fallidas_no_dejan_rastro():
    p = ProgramaLealtad()
    p.crearCliente("C001", "Sofía Rojas", "sofia@correo.com", "01-03-2026")
    p.registrarCompra("C001", "200.00", "10-03-2026")
    for fecha in ("05-03-2026", "30-02-2026"):
        with pytest.raises(ErroresBilletera) as e:
            p.registrarCompra("C001", "100.00", fecha)
        assert e.value.codigo == fechaInvalida
    h = p.consultarHistorial("C001")
    assert len(h) == 1 and (h[0]["puntos"], h[0]["referencia"]) == (20, "C-1")
    assert p.consultarSaldo("C001") == 20


def test_historial_devuelve_copia_y_no_altera_el_estado():
    p = ProgramaLealtad()
    p.crearCliente("C001", "Ana", "ana@correo.com", "05-01-2026")
    p.registrarCompra("C001", "500.00", "10-01-2026")
    p.consultarHistorial("C001").clear()             # intento de alterar la copia
    assert len(p.consultarHistorial("C001")) == 1


def test_historial_cliente_inexistente():
    with pytest.raises(ErroresBilletera) as e:
        ProgramaLealtad().consultarHistorial("C999")
    assert e.value.codigo == clienteNoEncontrado


from datetime import date

def test_prueba4_historial_completo():
    p = ProgramaLealtad()
    p.crearCliente("C001", "Jorge Mora", "jorge@correo.com", "01-03-2026")
    p.registrarCompra("C001", "80000.00", "02-03-2026")
    p.canjearPremio("C001", "P05", "03-03-2026")
    p.canjearPremio("C001", "P05", "04-03-2026")
    with pytest.raises(ErroresBilletera) as e:
        p.canjearPremio("C001", "P05", "05-03-2026")
    assert e.value.codigo == saldoInsuficiente

    h = p.consultarHistorial("C001")
    assert [(m["tipo"], m["puntos"], m["fecha"], m["idReferencia"]) for m in h] == [
        ("ACUMULACION", 8000, date(2026, 3, 2), "C-1"),
        ("CANJE", -4000, date(2026, 3, 3), "P05"),
        ("CANJE", -4000, date(2026, 3, 4), "P05"),
    ]
    assert sum(m["puntos"] for m in h) == p.consultarSaldo("C001") == 0


def test_prueba5_operaciones_fallidas_no_dejan_rastro():
    p = ProgramaLealtad()
    p.crearCliente("C001", "Sofía Rojas", "sofia@correo.com", "01-03-2026")
    p.registrarCompra("C001", "200.00", "10-03-2026")
    for fecha in ("05-03-2026", "30-02-2026"):
        with pytest.raises(ErroresBilletera) as e:
            p.registrarCompra("C001", "100.00", fecha)
        assert e.value.codigo == fechaInvalida
    h = p.consultarHistorial("C001")
    assert len(h) == 1 and (h[0]["puntos"], h[0]["idReferencia"]) == (20, "C-1")
    assert p.consultarSaldo("C001") == 20


def test_historial_devuelve_copia_y_no_altera_el_estado():
    p = ProgramaLealtad()
    p.crearCliente("C001", "Ana", "ana@correo.com", "05-01-2026")
    p.registrarCompra("C001", "500.00", "10-01-2026")
    p.consultarHistorial("C001").clear()             # intento de alterar la copia
    assert len(p.consultarHistorial("C001")) == 1


def test_historial_cliente_inexistente():
    with pytest.raises(ErroresBilletera) as e:
        ProgramaLealtad().consultarHistorial("C999")
    assert e.value.codigo == clienteNoEncontrado