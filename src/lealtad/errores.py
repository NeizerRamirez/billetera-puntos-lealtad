class ErroresBilletera(Exception):
    #Error identificado en la billetera del usuario.
    def __init__(self, codigo, mensaje: str = ""):
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(self.mensaje)

#Codigos de error para la billetera del usuario
clienteDuplicado = "CLIENTE_DUPLICADO"
clienteNoEncontrado = "CLIENTE_NO_ENCONTRADO"
datosInvalidos = "DATOS_INVALIDOS"
montoInvalido = "MONTO_INVALIDO"
fechaInvalida = "FECHA_INVALIDA"
premioNoEncontrado = "PREMIO_NO_ENCONTRADO"
premioSinStock = "PREMIO_SIN_STOCK"
saldoInsuficiente = "SALDO_INSUFICIENTE"
compraNoEncontrada = "COMPRA_NO_ENCONTRADA"
#eliminar si no se llega al punto 3:
compraYaDevuelta = "COMPRA_YA_DEVUELTA"
devolucionFueraDePlazo = "DEVOLUCION_FUERA_DE_PLAZO"

