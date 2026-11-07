from src.lealtad.modelos import Cliente, Premio, Compra, Movimiento, tipoAcumulacion, tipoCanje
from src.lealtad.errores import ErroresBilletera, clienteDuplicado, datosInvalidos, fechaInvalida, clienteNoEncontrado, montoInvalido, premioNoEncontrado, premioSinStock, saldoInsuficiente
from src.lealtad.config import CATALOGO, stockInicial, puntosUnidad, NIVELES
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import math

class ProgramaLealtad:
    def __init__(self):
        
        self._clientes: dict[str, Cliente] = {}

        # Se inicializa como None y luego se actualizará con la fecha de cada operación
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

    # Se valida que el texto no sea vacío ni tenga solo espacios en blanco
    def _textoValido(self, texto) -> bool:
        return isinstance(texto, str) and bool(texto.strip())

    # Función para validar el correo electrónico
    def _correoValido(self, correo) -> bool:
        # Evalua que se reciba un string y contenga @
        if not isinstance(correo, str) or correo.count("@") != 1:
            return False
        # Se comprueba que el correo tenga texto antes y después del @ y que el dominio tenga un punto
        antes, despues = correo.split("@")
        return bool(antes.strip()) and bool(despues.strip()) and "." in despues

    #función para validar el formato de la fecha y orden cronológico
    def _validarFecha(self, fechaStr) -> date:
            """Convierte DD-MM-AAAA a date y comprueba el orden cronológico.
            No modifica el estado."""
            try:
                # Se verifica que la fecha tenga el formato correcto y se convierte a objeto date
                fecha = datetime.strptime(fechaStr, "%d-%m-%Y").date()
            except (ValueError, TypeError):
                raise ErroresBilletera(codigo=fechaInvalida, mensaje="Formato de fecha inválido (DD-MM-AAAA)")
            # Se comprueba que la fecha no sea anterior a la última fecha registrada en el sistema
            if self._ultimaFechaSistema is not None and fecha < self._ultimaFechaSistema:
                raise ErroresBilletera(codigo=fechaInvalida, mensaje="La fecha es anterior a la última operación")
            return fecha

    #----------Funciones de consulta de datos-------------------
    # Función para obtener un cliente por su Id
    def _obtenerCliente(self, idCliente: str) -> Cliente:
        """Devuelve el cliente registrado o lanza ErroresBilletera si no existe."""
        if idCliente not in self._clientes:
            raise ErroresBilletera(
                codigo=clienteNoEncontrado,
                mensaje=f"El cliente con ID '{idCliente}' no existe.",
            )
        return self._clientes[idCliente]

    # Consulta de saldo del cliente
    def consultarSaldo(self, idCliente: str) -> int:
      return self._obtenerCliente(idCliente).saldo

    # Consulta de catálogo 

    def consultarCatalogo(self) -> list[dict]:
        """Devuelve una lista con copias (diccionarios) de id, nombre y costo.
        Protege el premio interno contra modificaciones accidentales externas.
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
        # Se valida que el monto sea un número válido y no nulo
        if monto is None or isinstance(monto, bool):
            raise ErroresBilletera(codigo=montoInvalido, mensaje="Monto inválido")
        try:
            # Se convierte el monto a Decimal para evitar errores de redondeo
            valor = Decimal(str(monto).strip())
        except InvalidOperation:
            raise ErroresBilletera(codigo=montoInvalido, mensaje="El monto no es un número")
        # Se valida que el monto no sea NaN, que sea positivo y tenga solo 2 decimales
        if (not valor.is_finite() or valor <= 0 or valor.as_tuple().exponent < -2):
            raise ErroresBilletera(codigo=montoInvalido, mensaje="Monto no positivo o con más de 2 decimales")
        return valor

    def _nivelPara(self, puntosAcumulados: int) -> tuple[str, Decimal]:
        """Recorre NIVELES (de mayor a menor) y retorna (nombre_nivel multiplicador)
        Como Bronce pide 0 puntos, siempre devolverá al menos Bronce.
        """
        for nombre, minimo, multiplicador in NIVELES:
            if puntosAcumulados >= minimo:
                return nombre, multiplicador
        # Se retornan indices para no dar datos de la estructura del config
        return NIVELES[-1][0], NIVELES[-1][2]

    # Función para calcular los puntos ganados en una compra
    def _calcularPuntos(self, monto: Decimal, multiplicador: Decimal) -> int:
        ## Se calcula la cantidad de puntos ganados redondeando hacia abajo
        return math.floor(monto / puntosUnidad * multiplicador)

    
    # Función para registar compras
    def registrarCompra(
        self, idCliente: str, montoInput, fechaStr: str
    ) -> dict:
        # Validar cliente 
        cliente = self._obtenerCliente(idCliente)

        # Validar monto
        monto = self._validarMonto(montoInput)

        # Validar fecha (orden cronológico sin alterar estado)
        fecha = self._validarFecha(fechaStr)

        # Determinar nivel y multiplicador del cliente
        nivel, multiplicador = self._nivelPara(cliente.puntosAcumulados)

        # Calcular puntos a otorgar aplicando el multiplicador
        puntosOtorgados = self._calcularPuntos(monto, multiplicador)

        # Generar Id para la compra usando el contador actual
        idCompra = f"C-{self._contadorCompras + 1}"

        nuevaCompra = Compra(
            idCompra=idCompra,
            idCliente=idCliente,
            monto=monto,
            fecha=fecha,
            puntosOtorgados=puntosOtorgados,
        )

        # En este punto todas las validaciones han pasado
        
        # Modificar estado del sistema
        cliente.saldo += puntosOtorgados
        cliente.puntosAcumulados += puntosOtorgados

        # Se registra en el historial solo si otorgó más de 0 puntos
        if puntosOtorgados > 0:
            cliente.historial.append(
                Movimiento(
                    tipo=tipoAcumulacion,
                    puntos=puntosOtorgados, 
                    fecha=fecha,
                    idReferencia=idCompra,
                )
            )

        self._compras[idCompra] = nuevaCompra
        self._ultimaFechaSistema = fecha

        # incremento del contador 
        self._contadorCompras += 1

        return {"idCompra": idCompra, "puntos": puntosOtorgados, "saldo": cliente.saldo, "nivel": nivel, "multiplicador": multiplicador }

    #------------Función para canjear premios----------------
    def canjearPremio(self, idCliente: str, idPremio: str, fechaStr: str) -> dict:

        # Validar Cliente 
        cliente = self._obtenerCliente(idCliente)

        # Validar Fecha 
        fecha = self._validarFecha(fechaStr)

        # Validar Premio Inexistente
        if idPremio not in self._catalogo:
            raise ErroresBilletera(
                codigo=premioNoEncontrado,
                mensaje=f"El premio '{idPremio}' no existe en el catálogo."
            )
        premio = self._catalogo[idPremio]

        # Validar Sin Stock (va antes que saldo insuficiente)
        if premio.stock <= 0:
            raise ErroresBilletera(
                codigo=premioSinStock,
                mensaje=f"El premio '{premio.nombre}' no tiene stock disponible."
            )

        # Validar Saldo 
        if cliente.saldo < premio.costo:
            raise ErroresBilletera(
                codigo=saldoInsuficiente,
                mensaje=f"El saldo continúa siendo de ({cliente.saldo}) puntos."
            )


        # Descontar el costo del saldo del cliente
        cliente.saldo -= premio.costo
        
        # Reducir el stock del premio
        premio.stock -= 1

        # Registrar movimiento en el historial (puntos negativos)
        cliente.historial.append(
            Movimiento(
                tipo=tipoCanje,
                puntos=-premio.costo,  # Negativo
                fecha=fecha,
                idReferencia=idPremio,
            )
        )

        # Actualizar la fecha del sistema (último paso)
        self._ultimaFechaSistema = fecha

        return {
            "puntosDescontados": premio.costo,
            "saldo": cliente.saldo
        }
    #-----Función para consultar el historial --------
    def consultarHistorial(self, idCliente: str) -> list[dict]:
        """Devuelve una copia del historial de movimientos del cliente."""
        cliente = self._obtenerCliente(idCliente)

        return [
            {
                "tipo": mov.tipo,
                "puntos": mov.puntos,
                "fecha": mov.fecha,
                "idReferencia": mov.idReferencia,
            }
            for mov in cliente.historial
        ]


    #------------Funcion para consultar el nivel del cliente----------
    def consultarNivel(self, idCliente: str) -> dict:
        """Devuelve un diccionario con el nivel actual, puntos acumulados y los puntos que le faltan para el siguiente nivel.
        """
        # 1. Obtener cliente 
        cliente = self._obtenerCliente(idCliente)
        pts = cliente.puntosAcumulados

        # 2. Determinar el nivel actual y su posición en la lista NIVELES
        nivelActual, _ = self._nivelPara(pts)

        # Buscar el índice del nivel
        idxActual = next(
            i for i, (nombre, _, _) in enumerate(NIVELES) if nombre == nivelActual
        )

        # 3. Determinar los puntos faltantes para el siguiente nivel
        if idxActual == 0:
            # Es Oro ,el nivel máximo
            puntosFaltantes = None
            siguienteNivel = None
        else:
            # El siguiente nivel es se encuentra arriba (la lista es de mayor a menor)
            siguienteNivel, ptsSiguienteMinimo, _ = NIVELES[idxActual - 1]
            puntosFaltantes = ptsSiguienteMinimo - pts

        return {
            "nivel": nivelActual,
            "puntosAcumulados": pts,
            "puntosFaltantes": puntosFaltantes,
            "siguienteNivel": siguienteNivel
        }


    #------------Función para crear clientes----------------
    def crearCliente(self, idCliente: str, nombre: str, correo: str, fechaAlta: str) -> Cliente:

        #Validación del Id del cliente para evitar duplicados
        if idCliente in self._clientes:
            raise ErroresBilletera(codigo=clienteDuplicado, mensaje="Cliente ya existe")

        if not( self._textoValido(idCliente)
            and self._textoValido(nombre)
            and self._correoValido(correo)):
            raise ErroresBilletera(codigo = datosInvalidos, mensaje = "Datos invalidos")

        #Validar el formato de la fecha y orden cronológico
        fecha = self._validarFecha(fechaAlta)

        #Crear cliente
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
    

