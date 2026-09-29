# StreamView Analytics — Evaluación Parcial EP3

## Ejecución
1. Instalar dependencias:
   `pip install -r requirements.txt`
2. Desde `StreamView_Analytics/` ejecutar:
   `streamlit run dashboard/app.py`

## Fuentes
- `data/raw/netflix_movies_detailed_up_to_2025.csv`
- `data/raw/netflix_tv_shows_detailed_up_to_2025.csv`

Las dos fuentes se integran en `src/preprocessing.py` y se distinguen mediante `content_type`.

## Dashboard
El dashboard incorpora:
- KPIs dinámicos.
- Filtro por tipo de contenido, año y género.
- Navegación por secciones.
- Visualizaciones interactivas Plotly.
- Análisis financiero sobre registros con presupuesto e ingresos disponibles.
- Catálogo filtrado.

## Estructura
- `data/raw/`: fuentes originales.
- `data/processed/`: datos preparados e integrados.
- `notebooks/`: análisis exploratorio.
- `dashboard/`: aplicación Streamlit.
- `images/`: visualizaciones estáticas.
- `src/`: procesamiento y funciones reutilizables.
- `Presentation/`: informe ejecutivo.
