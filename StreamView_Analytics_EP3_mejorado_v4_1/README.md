# StreamView Analytics — EP3

Proyecto de Visualización de Datos orientado a apoyar decisiones de Marketing y Adquisición de Contenidos mediante el análisis integrado de películas y series.

## Estructura

- `data/raw/`: datasets originales entregados para el caso.
- `data/processed/`: catálogo integrado y archivos derivados.
- `notebooks/`: análisis exploratorio de películas y series.
- `dashboard/app.py`: dashboard interactivo desarrollado con Streamlit y Plotly.
- `src/preprocessing.py`: funciones reproducibles de carga, limpieza e integración.
- `src/analysis.py`: funciones auxiliares de análisis.
- `images/`: visualizaciones generadas durante el EDA.
- `Presentation/`: informe ejecutivo.

## Calidad e integración de datos

Los archivos originales contienen 16.000 filas de películas y 16.000 de series. En películas `show_id` no presenta duplicados. En series se detectaron 9 `show_id` repetidos (18 filas): corresponden al mismo título y metadatos, con pequeñas diferencias únicamente en `popularity`. Para evitar contar dos veces el mismo contenido, el procesamiento consolida cada ID repetido de series en una sola fila y utiliza el promedio de `popularity` de esas observaciones.

También existen 397 valores de `show_id` presentes tanto en Movies como en TV Shows, pero representan contenidos diferentes. Por ello la clave analítica es `content_type + show_id`, no `show_id` por sí solo.

El catálogo procesado final contiene **31.991 contenidos únicos**: 16.000 películas y 15.991 series, sin duplicados en la clave compuesta. La auditoría queda documentada en `data/processed/auditoria_calidad_ids.csv`.

Para valoración se consideran contenidos con `vote_count > 0`. Los indicadores financieros usan exclusivamente películas con `budget` y `revenue` disponibles simultáneamente.

## Ejecución

Desde la carpeta raíz del proyecto:

```powershell
pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

## Reproducibilidad

El catálogo integrado puede reconstruirse desde los archivos originales con `build_integrated_catalog()` definido en `src/preprocessing.py`. Los archivos dentro de `data/raw/` se conservan sin modificar.
