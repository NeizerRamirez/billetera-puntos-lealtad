from dataclasses import dataclass, field
from datetime import date

@dataclass
class Cliente:
    idCliente: str
    nombre: str
    correo: str
    fechaAlta: date
    saldo: int = 0
    ptsAcumulados: int = 0
    
    """Se usa default_factory=list para crear una lista por cada cliente creado 
     y no compartir la misma lista entre todos los clientes."""
    historialCompras: list = field(default_factory=list)



