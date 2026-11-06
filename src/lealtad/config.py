"""
archivo de configuración para la billetera de lealtad del cliente.
"""

#Importación de la clase decimal para  evitar errores de redondeo.
from decimal import Decimal

#Se define 1 punto por cada 10 u.m.
puntosUnidad = Decimal("10")

#Se define el multiplicador base para los clientes de nivel bronce
multiplicadorBase = Decimal("1.00")

#Se tiene el stock inicial de los premios para poder probar el uso de la billetera
stockInicial = 10

#Reglas de negocio para los niveles de los clientes 

#(nombre, puntos acumulados necesarios, multiplicador)

NIVELES = [("Oro", 5000, Decimal("1.50")),("Plata", 1000, Decimal("1.25")),("Bronce", 0, Decimal("1.00"))]


CATALOGO = {"P01": ("Café de cortesía", 100),
            "P02": ("Cupon de descuento 10%", 250),
            "P03": ("Gift card de 50 u.m.",800), 
            "P04": ("Audifonos inalámbricos", 1200),
            "P05": ("Fin de semana en hotel", 4000)}
