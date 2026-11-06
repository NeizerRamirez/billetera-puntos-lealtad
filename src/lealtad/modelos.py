from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

@dataclass
class Cliente:
    idCliente: str
    nombre: str
    correo: str
    fechaAlta: date
    saldo: int = 0
    puntosAcumulados: int = 0
    
    """Se usa default_factory=list para crear una lista por cada cliente creado 
     y no compartir la misma lista entre todos los clientes."""
    historialCompras: list = field(default_factory=list)

@dataclass
class Premio:
    idPremio: str
    nombre: str
    costo: int
    stock: int

@dataclass
class Compra:
    idCompra: str
    idCliente: str
    fecha: date
    monto: Decimal
    puntosOtorgados: int