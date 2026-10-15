# 🎬 StreamView Analytics

Dashboard interactivo en **Power BI** para el análisis integrado del catálogo de **películas y series** de una plataforma de streaming, desarrollado por el equipo consultor **StreamView Analytics**.

El proyecto utiliza técnicas de análisis y visualización de datos para identificar patrones relacionados con la **popularidad, valoración, volumen del catálogo y desempeño financiero** de los contenidos, con el propósito de apoyar la toma de decisiones de las áreas de **Marketing y Adquisición de Contenidos**.

---

## 📌 Contexto del proyecto

StreamView Analytics busca comprender mejor el comportamiento de su catálogo para apoyar decisiones relacionadas con:

* Retención y engagement de usuarios.
* Preferencias de contenido.
* Adquisición y gestión de nuevos contenidos.
* Distribución y composición del catálogo.
* Identificación de contenidos con mayor popularidad.
* Evaluación del desempeño financiero de los contenidos que disponen de información de presupuesto e ingresos.

El análisis se concentra principalmente en dos problemas de negocio:

1. **Identificar qué géneros presentan mayores niveles de popularidad**, para facilitar la toma de decisiones sobre el contenido ofrecido.
2. **Comprender las características de los contenidos mejor valorados y más populares**, entregando información útil para las decisiones de adquisición.

**Pregunta central:** ¿qué géneros combinan mejor calidad, popularidad, evolución y desempeño financiero?

---

## 🎯 Objetivos

### Objetivo general

Analizar y visualizar información integrada del catálogo de películas y series para identificar patrones de popularidad, valoración, composición del catálogo y desempeño financiero.

### Objetivos específicos

* Analizar la popularidad promedio de películas y series según género.
* Comparar el volumen de contenidos de cada género con su popularidad.
* Medir la calidad de las películas por género mediante su valoración promedio.
* Analizar la evolución temporal del catálogo.
* Examinar la relación entre presupuesto e ingresos, y el ROI por género.
* Comparar valoración y popularidad entre géneros.
* Proporcionar indicadores clave (KPIs) e insights mediante un dashboard interactivo.
* Facilitar la exploración de los datos mediante filtros.

---

## 👥 Público objetivo

### Público principal

**Gerencias de Marketing y Adquisición de Contenidos**

* **Marketing:** decidir qué géneros promocionar según popularidad y valoración.
* **Adquisición:** decidir qué contenido incorporar según calidad y retorno financiero.

### Público secundario

* Directorio.
* Gerencia General y Finanzas.

---

## 📊 Dataset

El análisis integra dos fuentes de datos entregadas para el caso, ubicadas en `data/raw/` y conservadas sin modificar:

* `netflix_movies_detailed_up_to_2025.csv`: **16.000 registros de películas** (2010–2025).
* `netflix_tv_shows_detailed_up_to_2025.csv`: **16.000 registros de series** (2010–2025).

Ambas fuentes se estandarizan e integran en `data/processed/catalogo_integrado.csv`, permitiendo analizar el catálogo de forma conjunta y diferenciar los contenidos mediante su tipo. Las variables principales son:

| Variable       | Descripción                                                  |
| -------------- | ------------------------------------------------------------ |
| `show_id`      | Identificador del contenido                                  |
| `type`         | Tipo de contenido (Movie / TV Show)                          |
| `title`        | Título                                                       |
| `director`     | Director                                                     |
| `cast`         | Reparto                                                      |
| `country`      | País                                                         |
| `date_added`   | Fecha de incorporación                                       |
| `release_year` | Año de estreno                                               |
| `rating`       | Variable original eliminada (idéntica a `vote_average`)      |
| `duration`     | Variable original eliminada por ausencia de datos útiles     |
| `genres`       | Géneros asociados                                            |
| `language`     | Idioma original                                              |
| `description`  | Descripción                                                  |
| `popularity`   | Índice de popularidad del contenido                          |
| `vote_count`   | Cantidad de votos                                            |
| `vote_average` | Valoración promedio (0–10)                                   |
| `budget`       | Presupuesto en USD (solo películas)                          |
| `revenue`      | Ingresos en USD (solo películas)                             |

La integración conserva los atributos comparables entre ambos tipos de contenido y mantiene las variables financieras cuando están disponibles.

---

## 🔗 Integración de fuentes

* **Clave de integración:** `content_type + show_id`. Existen **397 `show_id` presentes tanto en películas como en series**, pero corresponden a contenidos distintos, por lo que `show_id` por sí solo no identifica un título.
* **Duplicados en series:** se detectaron **9 `show_id` repetidos (18 filas)**, con el mismo título y metadatos y diferencias solo en `popularity`. Se consolidaron en una sola fila usando el promedio de `popularity`.
* **Resultado:** **31.991 contenidos únicos** (16.000 películas y 15.991 series), sin duplicados en la clave compuesta. La auditoría queda documentada en `data/processed/auditoria_calidad_ids.csv`.

### ¿Por qué una sola tabla en Power BI?

El script `src/export_looker.py` transforma el catálogo integrado en `data/looker/streamview_generos_looker.csv`, con **una fila por cada combinación título × género (66.980 filas)**. Esta tabla plana permite filtrar todo el dashboard por género sin relaciones complejas entre tablas.

Para no contar dos veces un título con varios géneros, se calculan **pesos y valores atribuidos**: si una película tiene 3 géneros, cada género recibe un tercio de su presupuesto, ingresos y ganancia.

### Relación con retención y engagement

Las fuentes no contienen datos de usuarios (visualizaciones, permanencia o cancelaciones). Por ello, **la popularidad se usa como señal de engagement** (interés del público) y **la valoración como señal de satisfacción**, no como retención medida.

---

## 🧹 Preparación de los datos

El proceso de preparación se encuentra implementado en `src/preprocessing.py` (limpieza e integración) y `src/export_looker.py` (tabla para Power BI).

Entre las transformaciones realizadas se encuentran:

* Eliminación de `duration`, debido a que no contiene información útil para el análisis.
* Eliminación de `rating`, ya que en este dataset replica la información de `vote_average`.
* Conversión de `date_added` a formato fecha.
* Tratamiento de valores `0` en `budget` y `revenue` como datos faltantes.
* Consolidación de series duplicadas y creación de la clave `content_type + show_id`.
* Conservación de registros con información limitada cuando no existe evidencia suficiente para eliminarlos.
* Separación de los géneros (una fila por título × género) con pesos para evitar doble conteo.
* Cálculo de ganancia (`revenue − budget`) y resultado financiero (ganancia / pérdida / sin dato).

### Criterios de aceptación de los datos

| Criterio | Regla |
| --- | --- |
| Valoración válida | Solo contenidos con `vote_count > 0` |
| Datos financieros | Solo películas con `budget` y `revenue` mayores a 0 (**3.540 películas**) |
| Rankings de popularidad y calidad | Géneros con al menos **100 títulos** (o 100 películas valoradas) |
| Ranking de ROI | Géneros con al menos **30 películas** con datos financieros |
| Géneros sin clasificar | `Unknown` y `Sin género` se excluyen de los rankings |

---

## 📁 Estructura del proyecto

```text
StreamView_Analytics/
├── data/
│   ├── raw/          Archivos originales sin modificar (películas y series)
│   ├── processed/    Catálogo integrado y auditoría de calidad
│   └── looker/       streamview_generos_looker.csv (tabla para Power BI)
├── notebooks/        Análisis exploratorio
├── dashboard/        StreamView_Dashboard.pbix (dashboard principal, Power BI)
│                     app.py (versión previa en Streamlit, opcional)
├── images/           Capturas de las 7 páginas del dashboard
├── src/
│   ├── preprocessing.py   Limpieza e integración de las fuentes
│   ├── analysis.py        Funciones de análisis
│   └── export_looker.py   Genera la tabla para Power BI
├── Documentos/       Informe ejecutivo (PDF) y presentación
├── requirements.txt
└── README.md
```

---

## 🛠️ Tecnologías utilizadas

* **Power BI Desktop** (dashboard principal) y **DAX** (medidas e insights dinámicos)
* **Python**: Pandas, NumPy
* **Matplotlib** y **Seaborn** (análisis exploratorio)
* **Jupyter Notebook**

---

## 🚀 Instalación y ejecución

### 1. Preparar los datos (Python)

Se recomienda utilizar un entorno virtual. Desde la carpeta `StreamView_Analytics`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Generar la tabla para Power BI (solo es necesario si se modifican los datos):

```powershell
python src/export_looker.py
```

### 2. Abrir el dashboard (Power BI)

1. Abrir `dashboard/StreamView_Dashboard.pbix` con **Power BI Desktop**.
2. Si aparece un error de origen de datos, ir a **Transformar datos → Configuración de origen de datos → Cambiar origen** y seleccionar el archivo `data/looker/streamview_generos_looker.csv` de esta carpeta.
3. Presionar **Actualizar**.

---

## 📓 Análisis exploratorio

El análisis exploratorio se encuentra en dos notebooks:

```text
notebooks/01_analisis_popularidad_por_genero.ipynb
notebooks/02_analisis_series_popularidad_por_genero.ipynb
```

El primero desarrolla el análisis de películas y el segundo replica y adapta el proceso para las series, permitiendo posteriormente integrar ambas fuentes.

Los notebooks contienen las principales etapas del análisis:

1. Carga de datos.
2. Exploración inicial.
3. Diccionario de datos.
4. Identificación de valores faltantes.
5. Limpieza de variables.
6. Análisis de duplicados.
7. Análisis de distribuciones.
8. Análisis financiero.
9. Análisis por género.
10. Análisis de valoración y popularidad.
11. Identificación de valores atípicos.
12. Análisis de correlaciones.
13. Preparación de información para el dashboard.
14. Exportación de resultados procesados.

---

# 🖥️ Dashboard en Power BI

El dashboard tiene **7 páginas** organizadas como una **pirámide invertida**: primero los KPIs más importantes, luego los gráficos que los explican y al final el detalle título por título. Cada página parte con una **pregunta de negocio** en su subtítulo.

## 🧭 Navegación e interacción

* **Menú de navegación** entre las 7 páginas, siempre en la misma posición.
* **Filtros sincronizados entre páginas**: tipo de contenido, año de estreno, país, idioma y género. Al cambiar un filtro en una página, se mantiene en las demás.
* **Tooltips** con información adicional (por ejemplo, cantidad de títulos) al pasar el mouse sobre los gráficos.
* **Insights dinámicos**: los textos de la página de Insights se recalculan con los filtros activos.

## 🎨 Criterios de diseño

* Fondo negro con un único color de acento (rosado) para títulos y elementos importantes.
* Verde y rojo solo donde tienen significado: ganancia y pérdida en el Catálogo.
* Los rankings muestran el tamaño de muestra junto al nombre del género, por ejemplo `Soap (631)`.

---

## 1. Resumen ejecutivo

![Resumen ejecutivo](images/01_resumen_ejecutivo.png)

Panorama general del catálogo: tamaño, composición, popularidad y valoración.

**KPIs:** total de contenidos (31.991), películas (16.000), series (15.991), géneros (27 + 2 sin clasificar), popularidad promedio, valoración promedio (6,63) y % de títulos bien valorados (valoración ≥ 7).

**Visualizaciones:** popularidad por género, distribución películas/series, composición por género (treemap) y dispersión de popularidad y valoración por título.

---

## 2. Análisis por género

![Análisis por género](images/02_analisis_por_genero.png)

*¿Qué géneros dominan el catálogo, cuáles son los más populares y cuáles tienen mejor calidad?*

* Popularidad promedio por género, con tamaño de muestra.
* Volumen del catálogo vs. popularidad.
* Calidad de películas por género (valoración promedio, mínimo 100 películas valoradas).

---

## 3. Evolución del catálogo

![Evolución del catálogo](images/03_evolucion_del_catalogo.png)

*¿Cuánto contenido se estrena cada año y cómo cambia por tipo y género?*

* Contenidos estrenados por año, por tipo.
* Películas por año según género.

> ⚠️ La muestra tiene un máximo de 1.000 películas y 1.000 series por año, por lo que el volumen anual no mide el crecimiento real del catálogo.

---

## 4. Desempeño financiero

![Desempeño financiero](images/04_desempeno_financiero.png)

*¿Qué géneros generan más ingresos y qué tan bien se traduce el presupuesto en resultados?*

**KPIs:** películas con datos financieros (3.540), presupuesto promedio, ingreso promedio, ganancia total y correlación presupuesto–ingresos (0,75).

**Visualizaciones:** géneros con más y menos ingresos, presupuesto vs. ingresos por película (escala logarítmica) y **ROI por género** (ganancia / presupuesto).

---

## 5. Valoración vs. popularidad por género

![Valoración vs. popularidad](images/05_valoracion_vs_popularidad.png)

*¿Los géneros mejor valorados son también los más populares?*

Gráfico de dispersión: a la derecha, mejor valoración; arriba, mayor popularidad; el tamaño de la burbuja indica la cantidad de contenidos.

---

## 6. Catálogo

![Catálogo](images/06_catalogo.png)

Tabla con cada título: tipo, año, géneros, país, idioma, popularidad, valoración, presupuesto, ingresos y ganancia. La ganancia usa una escala de color: **verde** = ganancia, **rojo** = pérdida (más intenso, mayor monto); sin color = sin datos financieros.

---

## 7. Insights ejecutivos

![Insights ejecutivos](images/07_insights_ejecutivos.png)

Resume el análisis en cuatro preguntas: **qué ocurre, por qué ocurre, qué evidencia lo demuestra y qué decisiones tomar**. Los textos son **medidas DAX** que se recalculan con los filtros activos. Los rankings consideran géneros con muestra mínima (100 títulos, o 30 películas con datos financieros en el caso del ROI).

---

# 📈 Principales hallazgos

Con el catálogo completo (sin filtros):

* **Drama** es el género con más títulos (14.769), pero no el más popular.
* **Soap** es el género más popular (popularidad 155,5, con 631 títulos). Es un género solo de series, y las series tienen en promedio **~3 veces más popularidad** que las películas (64,9 vs. 20,4).
* **Documentary** es el género de películas mejor valorado (7,10, con 786 películas valoradas), seguido de Music (6,96) y Animation (6,94).
* **Action** es el género con más ingresos (60,1 mil millones de USD).
* **Horror** tiene el mayor ROI (330 %, con 463 películas con datos financieros).
* Presupuesto e ingresos tienen una correlación de **0,75**, pero el **37 % de las películas con datos financieros perdió dinero**.

Popularidad, valoración y desempeño financiero no representan el mismo fenómeno. Por esta razón, las decisiones de adquisición no deberían basarse en una sola métrica.

---

# 💡 Recomendaciones

**Marketing**

* Cruzar popularidad con valoración y tamaño de muestra.
* Priorizar campañas con evidencia de interés, no solo por volumen.

**Adquisición**

* No ampliar un género solo por su cantidad de títulos.
* Comparar ingresos, ganancia y ROI antes de decisiones financieras.
* Revisar valores atípicos y disponibilidad de datos antes de concluir.

---

# ⚠️ Limitaciones

* **Muestra limitada por año:** máximo de 1.000 películas y 1.000 series por año (2010–2025). Es un recorte de la muestra, no un equilibrio real del catálogo, y no permite medir su crecimiento.
* **Sin fecha real de incorporación:** en los datos, la fecha de incorporación coincide con la de estreno.
* **Datos financieros parciales:** presupuesto e ingresos solo existen para 3.540 películas. Los resultados no aplican a series.
* **Sin datos de retención:** no hay datos de visualizaciones ni de permanencia de usuarios. Popularidad y votos se usan como indicadores aproximados de engagement.
* **2025 incompleto:** muchos títulos recientes aún no tienen votos.
* La popularidad es una métrica del dataset y no representa número de usuarios.
* La correlación entre variables no implica causalidad.

---

# 🔁 Reproducibilidad

1. Descargar o clonar el repositorio.
2. Ubicarse en la carpeta `StreamView_Analytics`.
3. Crear un entorno virtual e instalar las dependencias de `requirements.txt`.
4. Verificar que los datasets se encuentren en `data/raw/`.
5. Ejecutar los notebooks `01_analisis_popularidad_por_genero.ipynb` y `02_analisis_series_popularidad_por_genero.ipynb`.
6. Verificar la generación de `data/processed/catalogo_integrado.csv`.
7. Ejecutar `python src/export_looker.py` para generar `data/looker/streamview_generos_looker.csv`.
8. Abrir `dashboard/StreamView_Dashboard.pbix` en Power BI Desktop y actualizar los datos.

---

# 📄 Entregables

* Dashboard interactivo en Power BI (`dashboard/StreamView_Dashboard.pbix`).
* Análisis exploratorio en Jupyter Notebook.
* Datos originales y datos procesados.
* Código fuente de procesamiento, análisis y exportación.
* Capturas del dashboard (`images/`).
* Informe ejecutivo y presentación (`Documentos/`).
* Documentación del proyecto (este README).

---

## 👨‍💻 Equipo

**StreamView Analytics** — Proyecto académico de Visualización de Datos, Duoc UC.

* Sebastián Aird
* María Calfileo
* Stephanie Chamorro
* Rocío Cruces

Docente: Alicia Ramos

Tecnologías principales: **Python + Pandas + Power BI + DAX**.