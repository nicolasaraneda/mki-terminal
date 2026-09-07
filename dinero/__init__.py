"""
dinero/ — el RIEL DE DINERO de MKI Terminal (Etapa 7.0.0, corrida 10).

Dos rieles, declarados como separados (DECISIONES.md, acta de la corrida 10):

  · RIEL DE MEDICIÓN — el gap asiático sellado. Horizonte de una noche. No
    mueve plata. Vive en motor.py / senales.py / snapshot.py y NO se toca.
  · RIEL DE DINERO — este paquete. Instrumentos listados en Estados Unidos,
    horizonte de semanas, presupuesto de 100 a 500 dólares. Todo SIMULADO.

AISLAMIENTO, en las dos direcciones:
  · nada de `dinero/` importa el camino de sellado (motor, senales,
    snapshot, universo, alertas, noticias). La adquisición se duplica a
    propósito, por el mismo motivo por el que GEMELO la duplicó: una fuente
    nueva es una forma nueva de romper el sello de las 18:15.
  · nada del camino de sellado importa `dinero/`.
Las dos direcciones están puestas como test en tests/test_dinero.py.

PROHIBICIONES DE DISEÑO, no de estilo:
  · ninguna función de este paquete envía una orden a una corredora, ni
    guarda credenciales de una. No hay cuenta abierta. Todo es papel.
  · todas las entradas son datos públicos.
"""
