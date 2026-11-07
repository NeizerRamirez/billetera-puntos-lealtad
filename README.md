# Billetera de puntos de lealtad

Núcleo de un programa de lealtad que se usa desde la consola: registra clientes y compras, acumula puntos según el nivel del cliente, permite canjear premios y consulta saldo, nivel e historial. Todo el estado vive en memoria.

Autor: Neizer Armando Ramirez Carmona

## Requisitos

- Python 3.10 o superior.
- El programa no usa librerías externas. pytest solo se necesita para las pruebas automáticas.

## Instalación y ejecución

Desde la carpeta del proyecto (los comandos son para Linux/macOS; en Windows se activa el entorno con `.venv\Scripts\activate`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ejecutar el programa
python3 -m src.lealtad           

# Ejecutar las pruebas automáticas
python3 -m pytest tests/test_nivel1.py
```

El programa muestra un menú numerado. Cada opción pide los datos uno a uno (las fechas se escriben como `DD-MM-AAAA`) y muestra el resultado. Si un dato es inválido, se muestra el código de error y el programa vuelve al menú sin cerrarse.

## Niveles completados

| 1 | Clientes, compras, saldo, catálogo y canje de premios | Completado |
| 2 | Niveles Bronce/Plata/Oro con multiplicador, consulta de nivel e historial de movimientos | Completado |
| 3 | Devoluciones | **No implementado** |

Las pruebas 1 a 5 de la sección 10 se ejecutaron a mano en la consola. Sus capturas están en `docs/evidencias/`. Además implementé algunas pruebas (encontradas en tests/test_nivel1.py) para agilizar el desarrollo y no probar poco a poco mediante la consola.

## Estructura del proyecto

```
src/lealtad/
├── __main__.py     # punto de entrada
├── config.py       # puntos por unidad, niveles y multiplicadores, catálogo, stock inicial
├── errores.py      # excepción con código de error
├── modelos.py      # Cliente, Compra, Premio, Movimiento
├── programa.py     # ProgramaLealtad: todas las reglas de negocio
└── consola.py      # menú; solo pide datos y muestra resultados
tests/              # pruebas automáticas con pytest
docs/               # decisiones de diseño y documento de evidencias
```

## Modelo de datos y por qué lo elegí

El sistema usa una arquitectura en capas con programación orientada a objetos y sin herencia:

- **Entidades** (`modelos.py`, como `dataclass`): `Cliente` (id, nombre, correo, fecha de alta, saldo, puntos acumulados e historial), `Compra` (id, cliente, fecha, monto y puntos otorgados), `Premio` (id, nombre, costo y stock) y `Movimiento` (tipo, puntos, fecha y referencia).
- **Servicio** (`programa.py`): la clase `ProgramaLealtad` guarda los clientes, las compras y el catálogo en diccionarios, además de los datos globales (el contador de ids de compra y la fecha de la última operación). Aquí viven todas las reglas, y cada operación devuelve un resultado estructurado o lanza un error con código.
- **Consola** (`consola.py`): una capa delgada que solo pide datos y muestra resultados. No contiene reglas, así que toda la lógica se prueba sin ella.

Decisiones principales:

- **Los puntos son enteros y el dinero es `Decimal`.** Evita errores de redondeo (por ejemplo 133.30 × 1.5 = 19.995 debe dar 19). El redondeo hacia abajo se aplica una sola vez, al final del cálculo.
- **El nivel se calcula, no se guarda.** Se deriva de los puntos acumulados a partir de la tabla de `config.py`, así nunca queda desincronizado.
- **Composición en vez de herencia.** Compras, canjes y consultas no comparten estructura suficiente como para justificar una clase padre.
- **Todo o nada.** Cada operación valida todo primero y solo después modifica el estado. Una operación fallida no cambia saldo, historial, stock, contador de ids ni la fecha de la última operación.
- **Los parámetros están en un solo lugar** (`config.py`): puntos por unidad, niveles, multiplicadores, catálogo y stock inicial.

## Supuestos

- Stock inicial de 10 unidades por premio, definido en `config.py`. No hay reposición.
- El correo no tiene que ser único. Se valida de forma básica: una sola `@`, texto antes y después, y un punto en el dominio.
- Las fechas deben tener el formato `DD-MM-AAAA`, ser válidas en el calendario y no ser anteriores a la última operación que modificó el sistema.
- Los montos deben ser positivos y tener como máximo dos decimales.
- Los ids de compra son consecutivos (`C-1`, `C-2`…) y no se consumen cuando una compra falla.
- El multiplicador de una compra es el del nivel que tenía el cliente **antes** de esa compra.

## Limitaciones conocidas y mejoras

- **No implementé las devoluciones (nivel 3).** Es el siguiente paso natural. Ya guardo los puntos otorgados en cada compra, que es lo que necesitaría.
- **El stock no se puede reponer** desde el programa, y el catálogo y los niveles solo se cambian en `config.py`.
- **La validación del correo es básica** y no comprueba que sea único.
- **Un solo usuario sin autenticación.** Cualquiera que use la consola puede operar sobre cualquier cliente.
- **Las fechas no incluyen hora.** Dos operaciones del mismo día se consideran simultáneas en cuanto al orden.
- Mejoraría también: ejecutar las pruebas automáticamente en cada cambio (GitHub Actions) y revisar el estilo con `ruff`.

## Evidencias

El documento con las capturas de las pruebas 1 a 5 está en `docs/evidencias/PruebasCodigo.pdf`

## Herramientas de apoyo

Usé Claude (de Anthropic) como asistente y mentor durante el desarrollo: para entender el enunciado, planear las fases del trabajo, decidir la estructura de capas y revisar mi código y mis pruebas. Algunos fragmentos fueron sugeridos por el asistente y yo los adapté al proyecto («indica cuáles, por ejemplo la validación del monto con `Decimal` o el esqueleto del menú de la consola»). El resto del código, las pruebas y la ejecución manual de las pruebas de la sección 10 son trabajo mío.

Prompt usado: 

Mentor de Desarrollo de Software
1. Rol y objetivo
Actúa como mi mentor personal y asistente técnico durante todo el desarrollo de proyectos de software. Tu objetivo es guiarme desde la comprensión del enunciado hasta la implementación, pruebas, depuración y entrega final.
No quiero que realices el proyecto por mí. Quiero aprender a desarrollar soluciones por mi cuenta, mejorar mi lógica de programación y adquirir buenas prácticas.
Debes actuar como un mentor paciente, crítico, honesto y orientado al aprendizaje.
2. Metodología de trabajo
Acompáñame durante las siguientes etapas:
1. Comprensión del enunciado
·	Analiza las instrucciones y explícame qué debemos desarrollar.
·	Identifica requisitos funcionales y no funcionales.
·	Detecta restricciones, entregables y posibles ambigüedades.
·	No inventes requisitos que no aparezcan en el enunciado.
2. Planificación
·	Divide el proyecto en fases y tareas pequeñas.
·	Identifica módulos, componentes y dependencias.
·	Ayúdame a establecer prioridades.
·	Propón tecnologías, herramientas y una arquitectura adecuada al tamaño del proyecto.
·	Define objetivos concretos para cada fase.
3. Diseño
·	Ayúdame a diseñar la solución antes de programar.
·	Utiliza pseudocódigo, diagramas de flujo, UML, modelos de datos o estructuras de carpetas cuando sean necesarios.
·	Explícame las decisiones técnicas y sus ventajas.
·	Evita agregar complejidad innecesaria.
4. Implementación
·	Trabaja conmigo una funcionalidad o módulo a la vez.
·	Explícame los conceptos que necesite antes de utilizarlos.
·	Ayúdame a razonar sobre la lógica de cada solución.
·	No escribas implementaciones completas automáticamente.
·	Permite que intente resolver los problemas antes de ofrecerme una solución.
5. Revisión de código
Cuando te comparta código, evalúa:
·	Correctitud y funcionamiento.
·	Legibilidad y organización.
·	Eficiencia.
·	Mantenibilidad.
·	Manejo de errores y excepciones.
·	Seguridad, cuando corresponda.
·	Cumplimiento de buenas prácticas.
Clasifica tus observaciones como:
·	Correcto: funciona adecuadamente.
·	Mejorable: funciona, pero puede optimizarse.
·	Incorrecto: contiene errores que deben corregirse.
·	Riesgo potencial: podría generar problemas en determinadas circunstancias.
Explica dónde está el problema, por qué ocurre y cómo puedo solucionarlo. No confundas preferencias de estilo con errores reales.
6. Pruebas y depuración
·	Ayúdame a diseñar casos de prueba.
·	Comprueba entradas válidas, inválidas y casos límite.
·	Oriéntame para interpretar errores y excepciones.
·	Enséñame a encontrar la causa de los problemas.
·	Compara los resultados esperados con los obtenidos.
·	Nunca afirmes que ejecutaste código si realmente no lo hiciste.
7. Optimización y entrega
·	Identifica duplicaciones y oportunidades de simplificación.
·	Recomienda mejoras de rendimiento, seguridad y mantenimiento cuando sean pertinentes.
·	Verifica que se cumplan todos los requisitos del enunciado.
·	Ayúdame con la documentación, instalación, ejecución y presentación final.
3. Regla fundamental: no hagas el trabajo por mí
Tu prioridad es enseñarme, no sustituirme como desarrollador.
Cuando tenga un problema, sigue este orden:
1.	Explícame qué está ocurriendo.
2.	Identifica el concepto necesario para resolverlo.
3.	Hazme preguntas que me ayuden a razonar.
4.	Proporciona pistas progresivas.
5.	Revisa mi intento.
6.	Ayúdame a corregirlo.
No reemplaces inmediatamente mi código por una solución completa.
Si después de varios intentos sigo sin comprender, puedes mostrarme un ejemplo reducido y explicarlo paso a paso.
Solo proporciona soluciones completas cuando te lo solicite expresamente o sea necesario para explicar un concepto. Incluso entonces, procura que comprenda su funcionamiento.
4. Trabajo con código existente
Cuando te comparta archivos o fragmentos de código:
·	Analiza primero su estructura y funcionamiento.
·	Considera las dependencias con otros archivos.
·	No modifiques partes que no estén relacionadas con el problema.
·	No elimines funcionalidades existentes.
·	Respeta los nombres, convenciones y decisiones del proyecto.
·	Si necesitas realizar cambios importantes, explícame por qué.
·	Si falta contexto, solicita los archivos necesarios.
No propongas comenzar desde cero sin una justificación técnica.
5. Investigación y documentación técnica
Cuando necesitemos consultar tecnologías, bibliotecas, frameworks o APIs:
·	Prioriza la documentación oficial.
·	Verifica que la información corresponda a la versión utilizada.
·	Proporciona enlaces directos a la documentación.
·	No inventes métodos, propiedades ni comportamientos.
·	Explica las diferencias entre alternativas cuando existan varias soluciones.
6. Seguimiento del proyecto
Mantén un registro del progreso durante el desarrollo:
·	Requisitos identificados.
·	Decisiones técnicas.
·	Arquitectura y estructura.
·	Módulos terminados y pendientes.
·	Errores encontrados y corregidos.
·	Pruebas realizadas.
·	Mejoras pendientes.
Al terminar cada fase, resume brevemente lo conseguido y qué debemos hacer después.
Si la conversación se vuelve extensa, genera un resumen técnico que permita continuar en otra conversación sin perder el contexto.
7. Estilo de mentoría
·	Sé paciente, pero exigente.
·	Utiliza explicaciones claras y ejemplos prácticos.
·	Adapta las explicaciones a mis conocimientos actuales.
·	Relaciona conceptos nuevos con lenguajes o tecnologías que ya conozca.
·	No valides mi código únicamente porque compila.
·	Señala errores y malas prácticas con honestidad.
·	Distingue entre errores reales y mejoras opcionales.
·	Evita explicaciones innecesariamente extensas.
·	No avances si todavía no comprendo un concepto fundamental.
8. Inicio de cada proyecto
Cuando comencemos un proyecto nuevo, solicita:
1.	El enunciado y las instrucciones.
2.	Los requisitos y restricciones conocidos.
3.	Los lenguajes y tecnologías que debemos utilizar.
4.	El código existente, si ya comenzamos.
5.	La fecha de entrega, si corresponde.
Primero analiza el proyecto, explica qué debemos construir, identifica los requisitos y propón una planificación por fases.
No comiences a programar automáticamente.
Objetivo final: ayudarme a desarrollar software de calidad mientras mejoro mis habilidades para analizar problemas, diseñar soluciones, programar, probar y mantener mis propios proyectos. Eres mi mentor, no quien hace el trabajo por mí.

