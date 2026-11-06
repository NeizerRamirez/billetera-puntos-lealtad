from dataclasses import dataclass, field

@dataclass
class Cliente:
    idCliente: str
    nombre: str
    correo: str
    fechaAlta: str
    saldo: int = 0
    ptsAcumulados: int = 0
    
    """Se usa default_factory=list para crear una lista por cada cliente creado 
     y no compartir la misma lista entre todos los clientes."""
    historialCompras: list = field(default_factory=list)



