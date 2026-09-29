# Visualizacion_de_datos_EV2

# 🎬 StreamView Analytics

Dashboard interactivo para el análisis del catálogo de películas de una plataforma de streaming ficticia denominada **StreamView Analytics**.

El proyecto utiliza técnicas de análisis y visualización de datos para identificar patrones relacionados con la **popularidad, valoración, volumen del catálogo y desempeño financiero** de las películas, con el propósito de apoyar la toma de decisiones de las áreas de **Contenido y Adquisición**.

---

## 📌 Contexto del proyecto

StreamView Analytics busca comprender mejor el comportamiento de su catálogo para apoyar decisiones relacionadas con:

* Retención y engagement de usuarios.
* Preferencias de contenido.
* Adquisición de nuevas películas.
* Distribución y composición del catálogo.
* Identificación de contenidos con mayor popularidad.
* Evaluación del desempeño financiero de las películas.

El análisis se concentra principalmente en dos problemas de negocio:

1. **Identificar qué géneros presentan mayores niveles de popularidad**, para facilitar la toma de decisiones sobre el contenido ofrecido.
2. **Comprender las características de los contenidos mejor valorados y más populares**, entregando información útil para las decisiones de adquisición.

---

## 🎯 Objetivos

### Objetivo general

Analizar y visualizar información del catálogo de películas de StreamView Analytics para identificar patrones de popularidad, valoración, composición del catálogo y desempeño financiero.

### Objetivos específicos

* Analizar la popularidad promedio de las películas según género.
* Comparar el volumen de películas de cada género con su popularidad.
* Analizar la evolución temporal del catálogo.
* Examinar la relación entre presupuesto e ingresos.
* Comparar valoración y popularidad entre géneros.
* Proporcionar indicadores clave mediante un dashboard interactivo.
* Facilitar la exploración de los datos mediante filtros.

---

## 👥 Público objetivo

### Público principal

**Gerencia de Contenidos y Adquisición**

El dashboard permite identificar géneros y características de contenido que pueden ser relevantes para decisiones de adquisición y composición del catálogo.

### Público secundario

* Directorio.
* Gerencia General.

---

## 📊 Dataset

El análisis utiliza principalmente el dataset:

`netflix_movies_detailed_up_to_2025.csv`

El archivo contiene **16.000 registros de películas** y las siguientes variables principales:

| Variable       | Descripción                                       |
| -------------- | ------------------------------------------------- |
| `show_id`      | Identificador de la película                      |
| `type`         | Tipo de contenido                                 |
| `title`        | Título                                            |
| `director`     | Director                                          |
| `cast`         | Reparto                                           |
| `country`      | País                                              |
| `date_added`   | Fecha de incorporación                            |
| `release_year` | Año de estreno                                    |
| `rating`       | Variable original eliminada durante la limpieza   |
| `duration`     | Variable original eliminada por ausencia de datos |
| `genres`       | Géneros asociados                                 |
| `language`     | Idioma                                            |
| `description`  | Descripción                                       |
| `popularity`   | Indicador de popularidad                          |
| `vote_count`   | Cantidad de votos                                 |
| `vote_average` | Valoración promedio                               |
| `budget`       | Presupuesto                                       |
| `revenue`      | Ingresos                                          |

El proyecto también contiene un dataset de series en `data/raw`, pero el análisis y dashboard actuales se concentran en el **catálogo de películas**.

---

## 🧹 Preparación de los datos

El proceso de preparación se encuentra implementado principalmente en:

`src/preprocessing.py`

Entre las transformaciones realizadas se encuentran:

* Eliminación de `duration`, debido a que no contiene información útil para el análisis.
* Eliminación de `rating`, ya que en este dataset replica la información de `vote_average`.
* Conversión de `date_added` a formato fecha.
* Tratamiento de valores `0` en `budget` y `revenue` como datos faltantes.
* Identificación de posibles duplicados según `title` y `release_year`.
* Conservación de registros con información limitada cuando no existe evidencia suficiente para eliminarlos.
* Separación de los géneros para permitir análisis por género.
* Creación de un subconjunto financiero compuesto por películas que poseen presupuesto e ingresos disponibles.

Las películas con `vote_count = 0` no se consideran para los indicadores de valoración, ya que no existe evidencia de votos que permita interpretar adecuadamente la valoración.

---

## 📁 Estructura del proyecto

```text
StreamView_Analytics/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   │   ├── netflix_movies_detailed_up_to_2025.csv
│   │   └── netflix_tv_shows_detailed_up_to_2025.csv
│   │
│   └── processed/
│       └── resumen_por_genero.csv
│
├── docs/
│
├── images/
│   ├── comparacion_volumen_vs_popularidad.png
│   ├── distribucion_popularity_kde.png
│   ├── distribuciones_numericas.png
│   ├── mapa_calor_nulos.png
│   ├── matriz_correlacion.png
│   └── outliers_boxplot.png
│
├── notebooks/
│   └── 01_analisis_popularidad_por_genero.ipynb
│
├── src/
│   ├── analysis.py
│   └── preprocessing.py
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Tecnologías utilizadas

* **Python**
* **Pandas**
* **NumPy**
* **Matplotlib**
* **Seaborn**
* **Plotly**
* **Streamlit**
* **Jupyter Notebook**

---

## 🚀 Instalación

Se recomienda utilizar un entorno virtual para instalar las dependencias del proyecto.

### 1. Crear un entorno virtual

Desde la carpeta `StreamView_Analytics`:

```powershell
python -m venv .venv
```

### 2. Activar el entorno virtual

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

---

## ▶️ Ejecución del dashboard

Desde la carpeta:

```text
StreamView_Analytics/
```

ejecutar:

```powershell
python -m streamlit run dashboard/app.py
```

Streamlit iniciará la aplicación y mostrará la dirección local correspondiente.

---

## 📓 Ejecución del análisis exploratorio

El análisis exploratorio se encuentra en:

```text
notebooks/01_analisis_popularidad_por_genero.ipynb
```

El notebook contiene las principales etapas del análisis:

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

# 🖥️ Funcionalidades del dashboard

El dashboard está construido con Streamlit y permite explorar el catálogo de forma interactiva.

## 🧭 Navegación

El dashboard cuenta con una navegación lateral que permite acceder a diferentes secciones:

* **Resumen ejecutivo**
* **Análisis por género**
* **Evolución del catálogo**
* **Desempeño financiero**
* **Valoración vs. popularidad**
* **Catálogo**

La navegación permite concentrar cada análisis en una sección específica y reducir la carga cognitiva al momento de interpretar los resultados.

---

## 🔎 Filtros

El usuario puede filtrar el catálogo mediante:

### Año de estreno

Permite seleccionar un año específico o visualizar todos los años disponibles.

### Géneros

Permite seleccionar uno o varios géneros.

Cuando se seleccionan múltiples géneros, se consideran las películas que pertenecen al menos a uno de los géneros seleccionados.

### Restablecer filtros

El botón:

**🔄 Restablecer filtros**

permite volver rápidamente a la configuración inicial.

Si los filtros seleccionados no producen resultados, el dashboard muestra un mensaje de advertencia en lugar de intentar generar visualizaciones vacías.

---

# 📌 Indicadores principales

La sección **Resumen ejecutivo** presenta cuatro indicadores:

* 🎬 Total de películas.
* ⭐ Valoración promedio.
* 🔥 Popularidad promedio.
* 💰 Ingresos promedio.

Los indicadores financieros consideran únicamente las películas que poseen información disponible tanto de presupuesto como de ingresos.

---

# 📊 Visualizaciones

## 🔥 Popularidad promedio por género

Gráfico de barras horizontal utilizado para comparar directamente la popularidad promedio entre géneros.

Permite identificar rápidamente los géneros con mayores niveles de popularidad.

---

## 📚 Volumen del catálogo vs. popularidad

Gráfico de dispersión que compara:

* Cantidad de películas por género.
* Popularidad promedio.

El tamaño de los puntos representa el volumen de películas.

Esta visualización permite identificar diferencias entre géneros con gran presencia en el catálogo y géneros que, aunque tienen menor volumen, presentan una mayor popularidad promedio.

---

## 📈 Evolución del catálogo

Gráfico de líneas que muestra la cantidad de películas estrenadas según año.

Permite observar la evolución temporal del catálogo y detectar períodos de mayor o menor incorporación de contenidos.

---

## 💰 Presupuesto vs. ingresos

Gráfico de dispersión que compara presupuesto e ingresos de las películas que cuentan con ambos datos disponibles.

La visualización utiliza escalas logarítmicas para facilitar la interpretación debido a la gran diferencia de magnitudes existente entre las películas.

También se muestra la correlación entre ambas variables.

---

## ⭐ Valoración vs. popularidad

Gráfico de dispersión que compara la valoración promedio y la popularidad promedio de los géneros.

El tamaño de cada punto representa la cantidad de películas.

Esta visualización permite analizar si los géneros más populares también presentan mayores niveles de valoración.

---

## 📋 Catálogo filtrado

La sección **Catálogo** permite revisar los registros correspondientes a los filtros seleccionados.

Se muestran hasta 20 registros mediante una tabla interactiva.

---

# 💡 Insights ejecutivos

El dashboard genera información interpretativa a partir de los datos filtrados.

Entre los indicadores considerados se encuentran:

* Género con mayor popularidad promedio.
* Género con mayor volumen de películas.
* Diferencia entre el género más popular y el género con mayor volumen.
* Relación entre presupuesto e ingresos.

Estos insights buscan transformar los resultados de los gráficos en información directamente interpretable para la toma de decisiones.

---

# 📈 Principales hallazgos del análisis

El análisis exploratorio permitió identificar diferentes patrones dentro del catálogo.

Entre los resultados observados:

* Los géneros **Adventure** y **Science Fiction** presentan niveles elevados de popularidad promedio.
* **Drama** concentra un volumen importante del catálogo, pero no presenta la misma posición relativa en popularidad.
* Existe una diferencia entre los géneros con mayor presencia en el catálogo y aquellos con mayor popularidad.
* El presupuesto y los ingresos presentan una relación positiva importante dentro del subconjunto de películas con información financiera disponible.
* Popularidad, valoración y desempeño financiero no representan exactamente el mismo fenómeno, por lo que deben analizarse conjuntamente.

Por esta razón, las decisiones de adquisición no deberían basarse únicamente en una métrica individual.

---

# ⚠️ Consideraciones sobre los datos

Los datos presentan algunas limitaciones que deben considerarse al interpretar los resultados:

* Existe información faltante en variables como director, reparto, país y género.
* Una proporción importante de las películas no posee información financiera completa.
* Los valores `0` de presupuesto e ingresos se consideran datos faltantes para el análisis financiero.
* Las películas sin votos (`vote_count = 0`) se excluyen del cálculo de valoración promedio.
* La popularidad es una métrica del dataset y no debe interpretarse automáticamente como número de usuarios de StreamView.
* La correlación entre variables no implica causalidad.

---

# 🔁 Reproducibilidad

Para reproducir el proyecto:

1. Descargar o clonar el repositorio.
2. Ubicarse en la carpeta `StreamView_Analytics`.
3. Crear un entorno virtual.
4. Instalar las dependencias mediante `requirements.txt`.
5. Verificar que los datasets se encuentren en `data/raw/`.
6. Ejecutar el notebook para revisar el análisis exploratorio.
7. Ejecutar el dashboard mediante Streamlit.

Comando principal:

```powershell
python -m streamlit run dashboard/app.py
```

---

# 📄 Entregables

El proyecto contempla los siguientes componentes:

* Análisis exploratorio mediante Jupyter Notebook.
* Dataset original.
* Datos procesados.
* Código fuente de procesamiento y análisis.
* Dashboard interactivo desarrollado con Streamlit.
* Visualizaciones exploratorias.
* Documentación del proyecto.
* Informe ejecutivo.
* Resumen ejecutivo para presentación.

---

## 👨‍💻 Proyecto

**StreamView Analytics**

Proyecto académico de visualización y análisis de datos.

Tecnologías principales: **Python + Pandas + Plotly + Streamlit**.
