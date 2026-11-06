from src.lealtad.modelos import Cliente
from src.lealtad.errores import ErroresBilletera, clienteDuplicado

class ProgramaLealtad:
    def __init__(self):
        self._clientes: dict[str, Cliente] = {}

    def crearCliente(self, idCliente: str, nombre: str, correo: str, fechaAlta: str) -> Cliente:
        #Validación del Id del cliente para evitar duplicados
        if idCliente in self._clientes:
            raise ErroresBilletera(clienteDuplicado)

        cliente = Cliente(idCliente = idCliente, nombre = nombre, correo = correo, fechaAlta = fechaAlta)

        # 3. Almacenamiento en el diccionario
        self._clientes[idCliente] = cliente
        return cliente

