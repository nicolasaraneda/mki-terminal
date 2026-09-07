# Criterio de elegibilidad de corredor (pre-registro del riel de dinero)

**Escrito:** 7-sep-2026. **Estado:** PROPUESTA, espera firma de Nicolás.
**Origen:** propuesto por Nicolás; verificado contra fuente oficial en esta sesión.
**Qué NO es:** no es una recomendación de inversión ni una evaluación de qué
corredor conviene. Es un criterio de eliminación previo a cualquier
comparación de precio.

---

## 1. El criterio

Un corredor es elegible para el riel de dinero de MKI Terminal sólo si cumple
las dos capacidades siguientes, verificadas contra documentación oficial del
propio corredor y no contra terceros:

**C1. Envío.** La máquina puede enviar sus propias órdenes por una interfaz
programática oficial y soportada, sin intervención humana en el momento del
envío.

**C2. Registro.** La máquina puede leer sus propias ejecuciones por esa misma
interfaz o por otra oficial, obteniendo al menos identificador de orden,
instrumento, cantidad, precio de ejecución y marca de tiempo, sin
intervención humana.

Un corredor que falle C1 o C2 no es elegible, **cualquiera sea su tarifa,
incluida una tarifa de cero**.

## 2. Por qué son dos y no una

Son capacidades separables. Un corredor puede permitir leer ejecuciones por
extractos o reportes sin permitir enviarlas, y en principio lo inverso
también. La versión de una sola condición dejaba pasar el primer caso, que no
sirve, porque un sistema que no puede enviar sus propias órdenes no es un
sistema automático sino una hoja de instrucciones.

## 3. Por qué el precio no puede compensar

El proyecto lleva un track record sellado cuyo valor entero descansa en que
la marca de tiempo la pone la máquina y no una persona. Si las ejecuciones
entran al sistema tipeadas a mano después del hecho, la separación entre
"emitido antes" y "reproducido después" desaparece, que es exactamente la
distinción que el riel de medición existe para sostener. Ese costo no tiene
precio comparable con una comisión, porque no es un costo por operación: es
la pérdida de la propiedad que hace que el registro signifique algo.

Corolario incómodo y declarado: este criterio puede obligar a pagar comisión
donde existe una alternativa de comisión cero. Eso es intencional.

## 4. Aplicación, con evidencia

### XTB: NO ELEGIBLE

Falla C1 y C2.

Fuente oficial, centro de ayuda de XTB, consultado 7-sep-2026:
`https://www.xtb.com/cy/help-center/our-platforms-2/do-you-offer-api-2`
y `https://www.xtb.com/int/help-center/our-platforms-6-4/does-xtb-offer-investment-automation-tools-4`

Declaran que ya no ofrecen acceso por API y que desde el 14 de marzo de 2025
el servicio por los hosts `xapi.xtb.com` y `ws.xtb.com` está deshabilitado,
recomendando la plataforma web o la aplicación móvil. En la segunda página
agregan que tampoco ofrecen copy trading.

Existen clientes de Python, PHP, Go, Java, NodeJS y Elixir para xAPI
publicados en repositorios públicos. Son de ingeniería inversa y apuntan a
hosts que el proveedor declara deshabilitados. **No cuentan como C1 ni C2**,
por dos razones independientes: no son interfaz oficial ni soportada, y su
licenciamiento no está verificado, lo que choca con la regla de la casa sobre
código de terceros.

La tarifa de XTB, cero por ciento en acciones y ETF reales hasta 100.000 euros
mensuales, es irrelevante bajo este criterio y no se evaluó.

### Interactive Brokers: ELEGIBLE

Cumple C1 y C2. IBKR publica y soporta la TWS API y la Client Portal (Web)
API, y documenta su uso contra la cuenta de práctica y contra la cuenta real.

Advertencia registrada, de la página oficial de comisiones consultada
7-sep-2026 (`https://www.interactivebrokers.com/en/pricing/commissions-stocks.php`):
las órdenes dirigidas por API no pueden usar la estructura Tiered; las
órdenes por API con SmartRouting sí pueden usar Tiered o Fixed. Esto no
afecta la elegibilidad, afecta el arancel. Ver el insumo del §40.

Advertencia adicional, de la misma página: IBKR Lite tiene elegibilidad de
residentes de Estados Unidos solamente. La estructura aplicable es IBKR Pro.

## 5. Qué haría caer este criterio

Se declara antes de usarlo, para que la revisión posterior sea legítima:

- Si aparece un corredor que cumple C1 y C2 con costo total materialmente
  menor que IBKR para el tamaño de este proyecto, el criterio no cambia: el
  corredor cambia. El criterio no privilegia a IBKR, sólo elimina a quien no
  cumple.
- Si XTB restablece una API oficial y soportada, XTB vuelve a ser elegible y
  hay que reevaluar. El criterio no lo excluye por identidad sino por
  capacidad, y la capacidad puede volver.
- Si se demuestra que el registro de ejecuciones leído por API difiere del
  registro oficial del corredor, C2 no está cumplida aunque la llamada
  responda. Verificar esto es trabajo, no supuesto.

## 6. Qué este criterio no dice

No dice que IBKR sea buen corredor. No dice que operar sea buena idea. No
dice nada sobre retorno esperado, y no puede: al 7-sep-2026 el riel de dinero
no tiene ninguna afirmación positiva en pie, con L1 refutada por su propia
regla pre-registrada y la celda superviviente caída bajo multiplicidad y bajo
ablación anual. Un criterio de elegibilidad de corredor no produce una razón
para operar.
