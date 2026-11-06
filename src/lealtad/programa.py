from src.lealtad.modelos import Cliente
from src.lealtad.errores import ErroresBilletera, clienteDuplicado, datosInvalidos, fechaInvalida
from datetime import date, datetime

class ProgramaLealtad:
    def __init__(self):
        
        self._clientes: dict[str, Cliente] = {}
        #Se inicializa como none y luego tomará el valor del primer cliente
        self._ultimaFechaSistema: date | None = None

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
        self._ultimaFechaSistema = fecha
        return nuevoCliente
    

