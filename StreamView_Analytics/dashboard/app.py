import streamlit as st
import pandas as pd
import plotly.express as px

from src.preprocessing import load_clean_movies, get_financial_subset


# CONFIGURACIÓN

st.set_page_config(
    page_title="StreamView Analytics",
    page_icon="🎬",
    layout="wide",
)


# CARGA DE DATOS

@st.cache_data
def load_data():
    return load_clean_movies()


df = load_data()

# TÍTULO

st.title("🎬 StreamView Analytics")

st.subheader("Análisis del catálogo de películas")

st.write(
    "Dashboard interactivo para analizar popularidad, valoración "
    "y desempeño financiero del catálogo."
)

st.sidebar.header("🧭 Navegación")

seccion = st.sidebar.radio(
    "Ir a:",
    [
        "Resumen ejecutivo",
        "Análisis por género",
        "Evolución del catálogo",
        "Insights ejecutivos",
        "Desempeño financiero",
        "Valoración vs. popularidad",
        "Catálogo"
    ]
)

# FILTROS

st.sidebar.header("🔎 Filtros")


# Filtro por año

years = sorted(
    df["release_year"].dropna().unique()
)

selected_year = st.sidebar.selectbox(
    "Año de estreno",
    ["Todos"] + years,
    key="year_filter"
)


# Filtro por género

genres = sorted(
    set(
        genre.strip()
        for value in df["genres"].dropna()
        for genre in value.split(",")
    )
)

selected_genres = st.sidebar.multiselect(
    "Géneros",
    genres,
    key="genre_filter"
)


# Restablecer filtros

def reset_filters():
    st.session_state["year_filter"] = "Todos"
    st.session_state["genre_filter"] = []


st.sidebar.button(
    "🔄 Restablecer filtros",
    on_click=reset_filters
)

# APLICACIÓN DE FILTROS

df_filtered = df.copy()


if selected_year != "Todos":
    df_filtered = df_filtered[
        df_filtered["release_year"] == selected_year
    ]


if selected_genres:
    df_filtered = df_filtered[
        df_filtered["genres"]
        .fillna("")
        .apply(
            lambda x: any(
                genre in x.split(",")
                for genre in selected_genres
            )
        )
    ]

# VALIDAR RESULTADOS DE LOS FILTROS

if df_filtered.empty:
    st.warning(
        "⚠️ No existen películas que coincidan con los filtros seleccionados."
    )
    st.stop()

# PREPARACIÓN PARA KPIs

df_ratings = df_filtered[
    df_filtered["vote_count"] > 0
].copy()


df_financial = get_financial_subset(
    df_filtered
)


# KPIs

total_movies = len(df_filtered)

avg_rating = df_ratings["vote_average"].mean()

avg_popularity = df_filtered["popularity"].mean()

avg_revenue = df_financial["revenue"].mean()

if seccion == "Resumen ejecutivo":
    st.divider()
    st.header("📌 Resumen ejecutivo")

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        label="🎬 Total de películas",
        value=f"{total_movies:,}"
    )


with col2:
    st.metric(
        label="⭐ Valoración promedio",
        value=(
            f"{avg_rating:.2f}"
            if pd.notna(avg_rating)
            else "N/A"
        )
    )


with col3:
    st.metric(
        label="🔥 Popularidad promedio",
        value=(
            f"{avg_popularity:.2f}"
            if pd.notna(avg_popularity)
            else "N/A"
        )
    )


with col4:
    st.metric(
        label="💰 Ingresos promedio",
        value=(
            f"${avg_revenue:,.0f}"
            if pd.notna(avg_revenue)
            else "N/A"
        )
    )

st.caption(
    f"Los indicadores financieros consideran únicamente "
    f"{len(df_financial):,} películas con presupuesto e ingresos disponibles."
)

# Preparación de géneros

df_genres = df_filtered.dropna(subset=["genres"]).copy()

df_genres["genres"] = df_genres["genres"].str.split(",")

df_genres = df_genres.explode("genres")

df_genres["genres"] = df_genres["genres"].str.strip()

if seccion == "Análisis por género":
    # CREAR DOS COLUMNAS

    col1, col2 = st.columns(2)


    # GRÁFICO 1 — POPULARIDAD POR GÉNERO

    with col1:

        st.subheader("🔥 Popularidad promedio por género")

        popularity_by_genre = (
            df_genres
            .groupby("genres", as_index=False)
            .agg(
                popularidad_promedio=("popularity", "mean"),
                peliculas=("title", "count")
            )
            .sort_values(
                "popularidad_promedio",
                ascending=False
            )
        )

        fig_genre = px.bar(
            popularity_by_genre,
            x="popularidad_promedio",
            y="genres",
            orientation="h",
            labels={
                "popularidad_promedio": "Popularidad promedio",
                "genres": "Género"
            }
        )

        fig_genre.update_layout(
            yaxis=dict(
                categoryorder="total ascending"
            ),
            height=650
        )

        st.plotly_chart(
            fig_genre,
            use_container_width=True
        )


    # GRÁFICO 2 — VOLUMEN VS. POPULARIDAD

    with col2:

        st.subheader("📚 Volumen del catálogo vs. popularidad")

        genre_comparison = (
            df_genres
            .groupby("genres", as_index=False)
            .agg(
                peliculas=("title", "count"),
                popularidad_promedio=("popularity", "mean")
            )
        )

        fig_volume_popularity = px.scatter(
        genre_comparison,
        x="peliculas",
        y="popularidad_promedio",
        text="genres",
        size="peliculas",
        hover_name="genres",
        hover_data={
            "peliculas": True,
            "popularidad_promedio": ":.2f"
        },
        labels={
            "peliculas": "Cantidad de películas",
            "popularidad_promedio": "Popularidad promedio",
            "genres": "Género"
        }
    )
        
        fig_volume_popularity.update_traces(
            textposition="top center"
        )

        st.plotly_chart(
            fig_volume_popularity,
            use_container_width=True
        )

# EVOLUCIÓN DEL CATÁLOGO

if seccion == "Evolución del catálogo":

    st.divider()

    st.header("📈 Evolución del catálogo")

    st.subheader("Cantidad de películas estrenadas por año")

    movies_by_year = (
        df_filtered
        .dropna(subset=["release_year"])
        .groupby("release_year", as_index=False)
        .agg(
            peliculas=("title", "count")
        )
        .sort_values("release_year")
    )

    fig_year = px.line(
        movies_by_year,
        x="release_year",
        y="peliculas",
        markers=True,
        labels={
            "release_year": "Año de estreno",
            "peliculas": "Cantidad de películas"
        }
    )

    fig_year.update_traces(
        hovertemplate=(
            "Año: %{x}<br>"
            "Películas: %{y:,}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        fig_year,
        use_container_width=True
    )

# INSIGHTS EJECUTIVOS
if seccion == "Insights ejecutivos":
    st.divider()

    st.header("💡 Insights ejecutivos")

    # Preparación de géneros
    genre_insights = (
        df_filtered
        .dropna(subset=["genres"])
        .assign(genres=lambda x: x["genres"].str.split(","))
        .explode("genres")
    )

    genre_insights["genres"] = genre_insights["genres"].str.strip()


    # Popularidad por género
    genre_popularity = (
        genre_insights
        .groupby("genres", as_index=False)
        .agg(
            popularidad_promedio=("popularity", "mean"),
            peliculas=("title", "nunique")
        )
        .sort_values("popularidad_promedio", ascending=False)
    )


    # Volumen por género
    genre_volume = (
        genre_insights
        .groupby("genres", as_index=False)
        .agg(
            peliculas=("title", "nunique")
        )
        .sort_values("peliculas", ascending=False)
    )


    if not genre_popularity.empty and not genre_volume.empty:

        top_genre = genre_popularity.iloc[0]["genres"]
        top_popularity = genre_popularity.iloc[0]["popularidad_promedio"]

        top_volume_genre = genre_volume.iloc[0]["genres"]
        top_volume = genre_volume.iloc[0]["peliculas"]

        # Insight 1
        st.info(
            f"🔥 **Mayor popularidad:** {top_genre} presenta la mayor "
            f"popularidad promedio del catálogo, con **{top_popularity:.2f}**."
        )

        # Insight 2
        st.info(
            f"📚 **Mayor volumen:** {top_volume_genre} concentra el mayor "
            f"número de películas, con **{top_volume:,} títulos**."
        )

        # Insight 3
        if top_genre != top_volume_genre:
            st.success(
                f"💡 **Oportunidad de contenido:** el género con mayor "
                f"popularidad ({top_genre}) no coincide con el género con "
                f"mayor volumen ({top_volume_genre}). Esto permite evaluar "
                f"si la distribución del catálogo está alineada con la demanda."
            )
        else:
            st.success(
                f"💡 **Alineación de contenido:** {top_genre} lidera tanto "
                f"en popularidad como en volumen del catálogo."
            )


    # Insight financiero
    df_financial_insight = get_financial_subset(df_filtered)

    if len(df_financial_insight) >= 2:

        financial_corr = (
            df_financial_insight["budget"]
            .corr(df_financial_insight["revenue"])
        )

        if financial_corr >= 0.7:
            financial_message = (
                "existe una relación positiva fuerte entre el presupuesto "
                "y los ingresos"
            )
        elif financial_corr >= 0.4:
            financial_message = (
                "existe una relación positiva moderada entre el presupuesto "
                "y los ingresos"
            )
        elif financial_corr >= 0:
            financial_message = (
                "existe una relación positiva débil entre el presupuesto "
                "y los ingresos"
            )
        else:
            financial_message = (
                "no se observa una relación positiva entre el presupuesto "
                "y los ingresos"
            )

        st.info(
            f"💰 **Desempeño financiero:** {financial_message} "
            f"(correlación: **{financial_corr:.2f}**)."
        )

# PRESUPUESTO VS. INGRESOS

if seccion == "Desempeño financiero":
        
    st.divider()

    st.header("💰 Desempeño financiero")

    st.subheader("Presupuesto vs. ingresos")

    df_financial = get_financial_subset(df_filtered).copy()

    financial_correlation = df_financial["budget"].corr(
        df_financial["revenue"]
    )
    st.metric(
        "📈 Correlación presupuesto-ingresos: 0.75",
        f"{financial_correlation:.2f}"
    )

    fig_financial = px.scatter(
        df_financial,
        x="budget",
        y="revenue",
        hover_name="title",
        hover_data={
            "budget": ":$,.0f",
            "revenue": ":$,.0f",
            "release_year": True,
            "popularity": ":.2f",
            "vote_average": ":.2f"
        },
        labels={
            "budget": "Presupuesto (USD)",
            "revenue": "Ingresos (USD)",
            "release_year": "Año de estreno",
            "popularity": "Popularidad",
            "vote_average": "Valoración"
        }
    )

    fig_financial.update_xaxes(
        type="log"
    )

    fig_financial.update_yaxes(
        type="log"
    )

    st.plotly_chart(
        fig_financial,
        use_container_width=True
    )

# CALIDAD VS. POPULARIDAD POR GÉNERO
if seccion == "Valoración vs. popularidad":
        
    st.divider()

    st.write("### ⭐ Valoración vs. popularidad por género")

    df_quality = df_filtered[
        df_filtered["vote_count"] > 0
    ].copy()

    df_quality["genres"] = df_quality["genres"].str.split(",")

    df_quality = df_quality.explode("genres")

    df_quality["genres"] = df_quality["genres"].str.strip()


    quality_by_genre = (
        df_quality
        .groupby("genres", as_index=False)
        .agg(
            valoracion_promedio=("vote_average", "mean"),
            popularidad_promedio=("popularity", "mean"),
            peliculas=("title", "count")
        )
    )


    fig_quality = px.scatter(
        quality_by_genre,
        x="valoracion_promedio",
        y="popularidad_promedio",
        size="peliculas",
        text="genres",
        hover_data=["peliculas"],
        labels={
            "valoracion_promedio": "Valoración promedio",
            "popularidad_promedio": "Popularidad promedio",
            "peliculas": "Cantidad de películas"
        },
        title="Valoración y popularidad según género"
    )


    fig_quality.update_traces(
        textposition="top center"
    )


    st.plotly_chart(
        fig_quality,
        use_container_width=True
    )


# CATÁLOGO

if seccion == "Catálogo":

    st.divider()

    st.write("### Catálogo filtrado")

    st.caption(
        f"Mostrando {len(df_filtered):,} películas "
        "según los filtros seleccionados."
    )


    with st.expander("Ver datos del catálogo"):

        st.dataframe(
            df_filtered.head(20),
            use_container_width=True
        )