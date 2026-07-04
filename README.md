# Bot Comparador de Acciones — Etapa 1

Dashboard comparador del sector semiconductores, procesadores y memoria RAM,
con empresas de EE.UU., Corea, Taiwán, Japón, Holanda y Alemania.

## Requisitos
- Python 3.10 o superior instalado (https://www.python.org/downloads/ — al instalar en Windows, marca la casilla "Add Python to PATH")
- VSCode (opcional pero recomendado)

## Instalación (una sola vez)

1. Descarga esta carpeta y ábrela en VSCode (`Archivo > Abrir carpeta`).
2. Abre la terminal integrada (`Terminal > Nueva terminal`) y ejecuta:

```bash
# Crear un entorno virtual (una cajita aislada para las librerías del proyecto)
python -m venv venv

# Activarlo:
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar las librerías del proyecto
pip install -r requirements.txt
```

## Ejecutar el dashboard

Con el entorno activado (verás `(venv)` al inicio de la línea de la terminal):

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`.
Para detenerlo: `Ctrl + C` en la terminal.

## Qué incluye esta etapa
- **Rendimiento base 100**: compara acciones de distintos países y monedas en igualdad de condiciones.
- **Matriz de correlaciones**: cómo se mueven entre sí los mercados de EE.UU., Asia y Europa.
- **Métricas por acción**: retorno, volatilidad, distancia del máximo, momentum.
- **Puntaje v0**: ranking cuantitativo simple, placeholder de la futura capa de IA.
- **Supuesto básico #1**: cuando una bolsa está cerrada (feriados, husos horarios),
  se asume vigente el último precio conocido para poder alinear las series globales.

## Notas
- Los datos vienen de Yahoo Finance (gratis, retraso ~15 min). En etapas
  posteriores se migrará a una API paga con datos en tiempo real.
- Si Yahoo rechaza consultas por exceso de peticiones, espera unos minutos:
  el dashboard guarda caché por 15 minutos para minimizar esto.
- Esta herramienta es de análisis y no constituye asesoría financiera.

## Subirlo a GitHub (opcional, como respaldo)
```bash
git init
git add .
git commit -m "Etapa 1: dashboard comparador de semiconductores"
```
Luego crea un repositorio en github.com y sigue las instrucciones de
"push an existing repository". Recomendado: hazlo privado.
