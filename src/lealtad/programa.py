from src.lealtad.modelos import Cliente, Premio, Compra
from src.lealtad.errores import ErroresBilletera, clienteDuplicado, datosInvalidos, fechaInvalida, clienteNoEncontrado, montoInvalido
from src.lealtad.config import CATALOGO, stockInicial, puntosUnidad, multiplicadorBase
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import math

class ProgramaLealtad:
    def __init__(self):
        
        self._clientes: dict[str, Cliente] = {}

        #Se inicializa como none y luego tomará el valor del primer cliente
        self._ultimaFechaSistema: date | None = None

        # Carga del catálogo desde config.py
        self._catalogo: dict[str, Premio] = {}
        for idPremio, (nombreP, costoP) in CATALOGO.items():
            self._catalogo[idPremio] = Premio(
                idPremio=idPremio,
                nombre=nombreP,
                costo=costoP,
                stock=stockInicial,
            )

        # Contador de compras para IDs únicos
        self._contadorCompras = 0
        # Diccionario para almacenar las compras realizadas
        self._compras: dict[str, Compra] = {}

    #-------Funciones para validar los datos de entrada------

    #Se valida que el texto no sea vacío ni tenga solo espacios en blanco
    def _textoValido(self, texto) -> bool:
        return isinstance(texto, str) and bool(texto.strip())

    #función para validar el correo electrónico
    def _correoValido(self, correo) -> bool:
        #Evalua que se reciba un string y posea un simbolo @
        if not isinstance(correo, str) or correo.count("@") != 1:
            return False
        #Se comprueba que el correo tenga texto antes y después del @ y que el dominio tenga un punto
        antes, despues = correo.split("@")
        return bool(antes.strip()) and bool(despues.strip()) and "." in despues

    #función para validar el formato de la fecha y orden cronológico
    def _validarFecha(self, fechaStr) -> date:
            """Convierte DD-MM-AAAA a date y comprueba el orden cronológico.
            No modifica el estado."""
            try:
                #Se verifica que la fecha tenga el formato correcto y se convierte a objeto date
                fecha = datetime.strptime(fechaStr, "%d-%m-%Y").date()
            except (ValueError, TypeError):
                raise ErroresBilletera(codigo=fechaInvalida, mensaje="Formato de fecha inválido (DD-MM-AAAA)")
            # Se comprueba que la fecha no sea anterior a la última fecha registrada en el sistema
            if self._ultimaFechaSistema is not None and fecha < self._ultimaFechaSistema:
                raise ErroresBilletera(codigo=fechaInvalida, mensaje="La fecha es anterior a la última operación")
            return fecha
    
    # Función para obtener un cliente por su Id
    def _obtenerCliente(self, idCliente: str) -> Cliente:
        """Devuelve el cliente registrado o lanza ErroresBilletera si no existe."""
        if idCliente not in self._clientes:
            raise ErroresBilletera(
                codigo=clienteNoEncontrado,
                mensaje=f"El cliente con ID '{idCliente}' no existe.",
            )
        return self._clientes[idCliente]

    #Consulta de saldo del cliente
    def consultarSaldo(self, idCliente: str) -> int:
      return self._obtenerCliente(idCliente).saldo

    #Consulta de catálogo 

    def consultarCatalogo(self) -> list[dict]:
        """Devuelve una lista con copias (diccionarios) de id, nombre y costo.
        Protege el stock interno contra modificaciones accidentales externas al crear la copia.
        """
        return [
            {
                "id": p.idPremio,
                "nombre": p.nombre,
                "costo": p.costo,
            }
            for p in self._catalogo.values()
        ]

    
    #------------Funciones para validar y registrar compras--------------

    # Función para validar el monto de la compra
    def _validarMonto(self, monto) -> Decimal:
        #Se valida que el monto sea un número válido y no nulo
        if monto is None or isinstance(monto, bool):
            raise ErroresBilletera(codigo=montoInvalido, mensaje="Monto inválido")
        try:
            #Se convierte el monto a Decimal para evitar errores de redondeo
            valor = Decimal(str(monto).strip())
        except InvalidOperation:
            raise ErroresBilletera(codigo=montoInvalido, mensaje="El monto no es un número")
        #Se valida que el monto no sea NaN y que sea positivo
        if (not valor.is_finite() or valor <= 0 or valor.as_tuple().exponent < -2):
            raise ErroresBilletera(codigo=montoInvalido, mensaje="Monto no positivo o con más de 2 decimales")
        return valor

    # Función para calcular los puntos ganados en una compra
    def _calcularPuntos(self, monto: Decimal, multiplicador: Decimal = multiplicadorBase) -> int:
        return math.floor(monto / puntosUnidad * multiplicador)

    
    #Función para registar compras
    def registrarCompra(
        self, idCliente: str, montoInput, fechaStr: str
    ) -> dict:
        #Validar cliente 
        cliente = self._obtenerCliente(idCliente)

        #Validar monto
        monto = self._validarMonto(montoInput)

        #Validar fecha (orden cronológico sin alterar estado)
        fecha = self._validarFecha(fechaStr)

        #Generar Id para la compra usando el contador actual
        idCompra = f"C-{self._contadorCompras + 1}"

        # Calcular puntos ganados 
        puntosOtorgados = self._calcularPuntos(monto)

        nuevaCompra = Compra(
            idCompra=idCompra,
            idCliente=idCliente,
            monto=monto,
            fecha=fecha,
            puntosOtorgados=puntosOtorgados,
        )

        #En este punto todas las validaciones han pasado
        
        #Modificar estado del sistema
        cliente.saldo += puntosOtorgados
        cliente.puntosAcumulados += puntosOtorgados

        self._compras[idCompra] = nuevaCompra
        self._ultimaFechaSistema = fecha

        # incremento del contador 
        self._contadorCompras += 1

        return {"idCompra": idCompra, "puntos": puntosOtorgados, "saldo": cliente.saldo}


    #------------Función para crear clientes----------------
    def crearCliente(self, idCliente: str, nombre: str, correo: str, fechaAlta: str) -> Cliente:

        #Validación del Id del cliente para evitar duplicados
        if idCliente in self._clientes:
            raise ErroresBilletera(codigo=clienteDuplicado, mensaje="Cliente ya existe")

        if not( self._textoValido(idCliente)
            and self._textoValido(nombre)
            and self._correoValido(correo)):
            raise ErroresBilletera(codigo = datosInvalidos, mensaje = "Datos invalidos")

        #Validar el formato de la fecha
        fecha = self._validarFecha(fechaAlta)

        #Crear cliente y guardar en diccionario
        nuevoCliente = Cliente(
            idCliente=idCliente,
            nombre=nombre,
            correo=correo,
            fechaAlta=fecha,
        )

        #Almacenamiento en el diccionario
        self._clientes[idCliente] = nuevoCliente

        #Actualizar la última fecha del sistema
        self._ultimaFechaSistema = fecha

        return nuevoCliente
    

