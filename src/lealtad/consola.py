from src.lealtad.errores import ErroresBilletera
from src.lealtad.programa import ProgramaLealtad


def _pedir(texto: str) -> str:
    """Solicita un dato al usuario y elimina espacios en blanco al inicio/final."""
    return input(f"{texto}: ").strip()


# ---------- Opciones de la Consola ----------


def _registrarCliente(programa: ProgramaLealtad):
    idCliente = _pedir("Id del cliente")
    nombre = _pedir("Nombre")
    correo = _pedir("Correo")
    fecha = _pedir("Fecha (DD-MM-AAAA)")

    cliente = programa.crearCliente(idCliente, nombre, correo, fecha)
    print(f"> Cliente {idCliente} ({nombre}) creado con éxito.")


def _registrarCompra(programa: ProgramaLealtad):
    idCliente = _pedir("Id del cliente")
    monto = _pedir("Monto")  
    fecha = _pedir("Fecha (DD-MM-AAAA)")

    compraActual = programa.registrarCompra(idCliente, monto, fecha)

    # Obtenemos el saldo actual 
    cliente = programa._obtenerCliente(idCliente)
    print(
        f"> Compra {compraActual['idCompra']} registrada. "
        f"Nivel: {compraActual['nivel']} (x{compraActual['multiplicador']:.2f}). "
        f"Puntos ganados: {compraActual['puntos']}. "
        f"Saldo: {compraActual['saldo']}"
    )


def _consultarSaldo(programa: ProgramaLealtad):
    idCliente = _pedir("Id del cliente")
    saldo = programa.consultarSaldo(idCliente)
    print(f"> Cliente {idCliente} | Saldo: {saldo} puntos")


def _consultarCatalogo(programa: ProgramaLealtad):
    catalogo = programa.consultarCatalogo()
    print("\n--- Catálogo de Premios Disponibles ---")
    for p in catalogo:
        print(f"  [{p['id']}] {p['nombre']} - Costo: {p['costo']} pts")


def _canjearPremio(programa: ProgramaLealtad):
    idCliente = _pedir("Id del cliente")
    idPremio = _pedir("Id del premio")
    fecha = _pedir("Fecha (DD-MM-AAAA)")

    premioActual = programa.canjearPremio(idCliente, idPremio, fecha)
    print(
        f"> Canje exitoso de {idPremio}. "
        f"Puntos descontados: {premioActual['puntosDescontados']}. "
        f"Nuevo saldo: {premioActual['saldo']:.2f} "
    )


def _consultarNivel(programa: ProgramaLealtad):
    idCliente = _pedir("Id del cliente")
    nivelActual = programa.consultarNivel(idCliente)

    puntosFaltantes = (
        f"{nivelActual['puntosFaltantes']} pts"
        if nivelActual["puntosFaltantes"] is not None
        else "Se encuentra en el nivel maximo"
    )

    print(
        f"> Cliente {idCliente} | "
        f"Nivel Actual: {nivelActual['nivel']} | "
        f"Puntos Acumulados: {nivelActual['puntosAcumulados']} | "
        f"Puntos Faltantes Siguiente Nivel: {puntosFaltantes}"
    )


def _consultarHistorial(programa: ProgramaLealtad):
    idCliente = _pedir("Id del cliente")
    historial = programa.consultarHistorial(idCliente)

    #Mensaje en caso de que no haya historial que mostrar
    if not historial:
        print(f"> El cliente {idCliente} no posee movimientos registrados.")
        return

    print(f"\n--- Historial de Movimientos para {idCliente} ---")
    for mov in historial:
        signo = "+" if mov["puntos"] > 0 else ""
        fecha_str = (
            mov["fecha"].strftime("%d-%m-%Y")
            if hasattr(mov["fecha"], "strftime")
            else str(mov["fecha"])
        )
        print(
            f"  - [{fecha_str}] Tipo: {mov['tipo']} | "
            f"Puntos: {signo}{mov['puntos']} | Ref: {mov['idReferencia']}"
        )


# Mapa de opciones de menú
OPCIONES = {
    "1": ("Registrar cliente", _registrarCliente),
    "2": ("Registrar compra", _registrarCompra),
    "3": ("Consultar saldo", _consultarSaldo),
    "4": ("Consultar catalogo", _consultarCatalogo),
    "5": ("Canjear premio", _canjearPremio),
    "6": ("Consultar nivel", _consultarNivel),
    "7": ("Consultar historial", _consultarHistorial),
}


def ejecutar():
    programa = ProgramaLealtad()

    while True:
        print("\n=== Bienvenido al Programa de Lealtad ===")
        for clave, (titulo, _) in OPCIONES.items():
            print(f"{clave}. {titulo}")
        #Se pone el 0 en este nivel para no afectar la ejecución de las opciones
        print("0. Salir")

        try:
            opcion = _pedir("\nSeleccione una opción")

            if opcion == "0":
                print("Hasta luego.")
                break

            if opcion not in OPCIONES:
                print("> Opción no válida.")
                continue

            # Ejecuta la función asociada a la opción seleccionada
            OPCIONES[opcion][1](programa)

        except ErroresBilletera as error:
            print(f"> Error {error.codigo}: {error.mensaje}")
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo.")
            break
        except Exception as error:   # red de seguridad: el programa nunca debe cerrarse
            print(f"> Error inesperado ({type(error).__name__}): {error}")


