import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocessing import get_financial_subset

st.set_page_config(page_title="StreamView Analytics", page_icon="🎬", layout="wide")

@st.cache_data
def load_data():
    data_path = PROJECT_ROOT / "data" / "processed" / "catalogo_integrado.csv"
    df = pd.read_csv(data_path)
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    return df


def explode_genres(data):
    out = data.dropna(subset=["genres"]).copy()
    out["genres"] = out["genres"].str.split(",")
    out = out.explode("genres")
    out["genres"] = out["genres"].str.strip()
    return out[out["genres"].ne("")]


def reset_filters():
    st.session_state["type_filter"] = content_types
    st.session_state["year_filter"] = "Todos"
    st.session_state["genre_filter"] = []
    st.session_state["country_filter"] = []
    st.session_state["language_filter"] = []


df = load_data()

st.title("🎬 StreamView Analytics")
st.subheader("Visual Analytics para decisiones de Marketing y Adquisición de Contenidos")
st.write(
    "Explora el catálogo integrado de películas y series para identificar géneros y contenidos "
    "con mayor popularidad y valoración, además de tendencias temporales y desempeño financiero."
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
        "Catálogo",
    ],
)

st.sidebar.header("🔎 Filtros")
content_types = sorted(df["content_type"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect(
    "Tipo de contenido", content_types, default=content_types, key="type_filter"
)

years = sorted(df["release_year"].dropna().astype(int).unique().tolist())
selected_year = st.sidebar.selectbox("Año de estreno", ["Todos"] + years, key="year_filter")

genres = sorted({g.strip() for value in df["genres"].dropna() for g in value.split(",") if g.strip()})
selected_genres = st.sidebar.multiselect("Géneros", genres, key="genre_filter")

countries = sorted({c.strip() for value in df["country"].dropna() for c in str(value).split(",") if c.strip()})
selected_countries = st.sidebar.multiselect("País", countries, key="country_filter")

languages = sorted(df["language"].dropna().astype(str).unique().tolist())
selected_languages = st.sidebar.multiselect("Idioma", languages, key="language_filter")

st.sidebar.button("🔄 Restablecer filtros", on_click=reset_filters)

# Aplicación de filtros
filtered = df.copy()
if selected_types:
    filtered = filtered[filtered["content_type"].isin(selected_types)]
else:
    filtered = filtered.iloc[0:0]

if selected_year != "Todos":
    filtered = filtered[filtered["release_year"] == selected_year]

if selected_genres:
    filtered = filtered[
        filtered["genres"].fillna("").apply(
            lambda x: any(g.strip() in selected_genres for g in x.split(","))
        )
    ]

if selected_countries:
    filtered = filtered[
        filtered["country"].fillna("").apply(
            lambda x: any(c.strip() in selected_countries for c in str(x).split(","))
        )
    ]

if selected_languages:
    filtered = filtered[filtered["language"].isin(selected_languages)]

if filtered.empty:
    st.warning("⚠️ No existen contenidos que coincidan con los filtros seleccionados.")
    st.stop()

df_filtered = filtered
ratings = df_filtered[df_filtered["vote_count"] > 0].copy()
df_genres = explode_genres(df_filtered)
df_financial = get_financial_subset(df_filtered)

# KPIs comunes
movie_count = int((df_filtered["content_type"] == "Movie").sum())
tv_count = int((df_filtered["content_type"] == "TV Show").sum())
avg_rating = ratings["vote_average"].mean()
avg_popularity = df_filtered["popularity"].mean()
unique_genres = df_genres["genres"].nunique()

genre_kpi = (
    df_genres.groupby("genres", as_index=False)["popularity"].mean()
    .sort_values("popularity", ascending=False)
)
top_genre = genre_kpi.iloc[0]["genres"] if not genre_kpi.empty else "N/A"

top_content_row = df_filtered.dropna(subset=["popularity"]).sort_values("popularity", ascending=False).head(1)
top_content = top_content_row.iloc[0]["title"] if not top_content_row.empty else "N/A"
top_content_pop = top_content_row.iloc[0]["popularity"] if not top_content_row.empty else None

if seccion == "Resumen ejecutivo":
    st.divider()
    st.header("📌 Resumen ejecutivo")
    st.caption("Los indicadores y gráficos se actualizan con los filtros seleccionados.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎬 Total contenidos", f"{len(df_filtered):,}")
    c2.metric("🎥 Películas", f"{movie_count:,}")
    c3.metric("📺 Series", f"{tv_count:,}")
    c4.metric("🎭 Géneros", f"{unique_genres:,}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("🔥 Popularidad promedio", f"{avg_popularity:.2f}" if pd.notna(avg_popularity) else "N/A")
    c6.metric("⭐ Valoración promedio", f"{avg_rating:.2f} / 10" if pd.notna(avg_rating) else "N/A")
    c7.metric("🏆 Género más popular", top_genre)
    c8.metric("🚀 Contenido más popular", top_content)

    if top_content_pop is not None:
        st.caption(f"El contenido más popular registra un índice de popularidad de {top_content_pop:.2f}.")

    left, right = st.columns(2)
    with left:
        st.subheader("🔥 Top 10 géneros por popularidad")
        top10 = (
            df_genres.groupby("genres", as_index=False)
            .agg(popularidad_promedio=("popularity", "mean"), contenidos=("title", "count"))
            .sort_values("popularidad_promedio", ascending=False)
            .head(10)
            .sort_values("popularidad_promedio")
        )
        fig = px.bar(
            top10, x="popularidad_promedio", y="genres", orientation="h",
            labels={"popularidad_promedio": "Popularidad promedio", "genres": "Género"},
            hover_data={"contenidos": True},
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("📚 Composición del catálogo")
        type_counts = df_filtered["content_type"].value_counts().rename_axis("Tipo").reset_index(name="Contenidos")
        fig = px.bar(type_counts, x="Tipo", y="Contenidos", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("⭐ Popularidad vs. valoración")
        scatter_data = ratings.dropna(subset=["popularity", "vote_average"]).copy()
        fig = px.scatter(
            scatter_data, x="vote_average", y="popularity", color="content_type",
            hover_name="title", opacity=0.6,
            labels={"vote_average": "Valoración promedio", "popularity": "Popularidad", "content_type": "Tipo"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("🌳 Catálogo por tipo y género")
        tree = (
            df_genres.groupby(["content_type", "genres"], as_index=False)
            .agg(contenidos=("title", "count"))
        )
        fig = px.treemap(tree, path=["content_type", "genres"], values="contenidos")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("💡 Lectura ejecutiva")
    volume = df_genres.groupby("genres")["title"].count().sort_values(ascending=False)
    top_volume_genre = volume.index[0] if not volume.empty else "N/A"
    if top_genre != "N/A" and top_volume_genre != "N/A":
        if top_genre != top_volume_genre:
            st.info(
                f"El género con mayor popularidad promedio es **{top_genre}**, mientras que **{top_volume_genre}** "
                "concentra el mayor volumen del catálogo. Esto sugiere que volumen y popularidad no deben interpretarse "
                "como equivalentes al decidir campañas o futuras adquisiciones."
            )
        else:
            st.info(
                f"**{top_genre}** lidera tanto en popularidad promedio como en volumen dentro del filtro actual, "
                "por lo que merece atención prioritaria en decisiones de posicionamiento."
            )

elif seccion == "Análisis por género":
    st.divider()
    st.header("🎭 Análisis por género")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 Popularidad promedio por género")
        pop = (
            df_genres.groupby("genres", as_index=False)
            .agg(popularidad_promedio=("popularity", "mean"), contenidos=("title", "count"))
            .sort_values("popularidad_promedio", ascending=False)
        )
        fig = px.bar(pop, x="popularidad_promedio", y="genres", orientation="h",
                     labels={"popularidad_promedio": "Popularidad promedio", "genres": "Género"})
        fig.update_layout(yaxis=dict(categoryorder="total ascending"), height=650)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📚 Volumen del catálogo vs. popularidad")
        comp = df_genres.groupby("genres", as_index=False).agg(
            contenidos=("title", "count"), popularidad_promedio=("popularity", "mean")
        )
        fig = px.scatter(
            comp, x="contenidos", y="popularidad_promedio", text="genres", size="contenidos",
            hover_name="genres", labels={"contenidos": "Cantidad de contenidos", "popularidad_promedio": "Popularidad promedio"},
        )
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌳 Treemap de composición por tipo y género")
    tree = df_genres.groupby(["content_type", "genres"], as_index=False).agg(contenidos=("title", "count"))
    st.plotly_chart(px.treemap(tree, path=["content_type", "genres"], values="contenidos"), use_container_width=True)

elif seccion == "Evolución del catálogo":
    st.divider()
    st.header("📈 Evolución temporal")

    st.subheader("Estrenos por año y tipo de contenido")
    releases = (
        df_filtered.dropna(subset=["release_year", "content_type"])
        .groupby(["release_year", "content_type"], as_index=False).size()
        .rename(columns={"size": "contenidos"}).sort_values("release_year")
    )
    fig = px.line(
        releases, x="release_year", y="contenidos", color="content_type", markers=True,
        labels={"release_year": "Año de estreno", "contenidos": "Cantidad de contenidos", "content_type": "Tipo"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Incorporaciones a la plataforma por año")
    additions = df_filtered.dropna(subset=["date_added", "content_type"]).copy()
    additions["year_added"] = additions["date_added"].dt.year
    additions = (
        additions.groupby(["year_added", "content_type"], as_index=False).size()
        .rename(columns={"size": "contenidos"}).sort_values("year_added")
    )
    fig_area = px.area(
        additions, x="year_added", y="contenidos", color="content_type",
        labels={"year_added": "Año de incorporación", "contenidos": "Contenidos incorporados", "content_type": "Tipo"},
    )
    st.plotly_chart(fig_area, use_container_width=True)
    st.caption("El gráfico de línea usa el año de estreno; el gráfico de área usa la fecha de incorporación a la plataforma.")

elif seccion == "Insights ejecutivos":
    st.divider()
    st.header("💡 Insights ejecutivos")
    genre_pop = df_genres.groupby("genres", as_index=False).agg(
        popularidad_promedio=("popularity", "mean"), contenidos=("title", "nunique")
    ).sort_values("popularidad_promedio", ascending=False)
    genre_vol = df_genres.groupby("genres", as_index=False).agg(contenidos=("title", "nunique")).sort_values("contenidos", ascending=False)
    if not genre_pop.empty and not genre_vol.empty:
        gp, gv = genre_pop.iloc[0], genre_vol.iloc[0]
        st.info(f"🔥 **Qué está ocurriendo:** **{gp['genres']}** presenta la mayor popularidad promedio ({gp['popularidad_promedio']:.2f}).")
        st.info(f"📚 **Evidencia de volumen:** **{gv['genres']}** concentra el mayor número de contenidos ({int(gv['contenidos']):,}).")
        if gp["genres"] != gv["genres"]:
            st.success(
                f"🎯 **Decisión sugerida:** Marketing debería evaluar **{gp['genres']}** para posicionamiento por su alta popularidad, "
                f"mientras Adquisición debe contrastar esa señal con la alta presencia de **{gv['genres']}** antes de ampliar el catálogo."
            )
        else:
            st.success(f"🎯 **Decisión sugerida:** **{gp['genres']}** merece atención prioritaria al combinar alta popularidad y alta presencia.")

    fin = get_financial_subset(df_filtered)
    if len(fin) >= 2:
        corr = fin["budget"].corr(fin["revenue"])
        st.info(f"💰 **Evidencia financiera:** correlación presupuesto-ingresos de **{corr:.2f}** en películas con ambos datos disponibles.")

elif seccion == "Desempeño financiero":
    st.divider()
    st.header("💰 Desempeño financiero")
    fin = get_financial_subset(df_filtered).copy()
    if len(fin) < 2:
        st.warning("No hay suficientes películas con presupuesto e ingresos disponibles para el filtro actual.")
    else:
        corr = fin["budget"].corr(fin["revenue"])
        c1, c2, c3 = st.columns(3)
        c1.metric("📈 Correlación presupuesto-ingresos", f"{corr:.2f}")
        c2.metric("💵 Presupuesto promedio", f"${fin['budget'].mean():,.0f}")
        c3.metric("💰 Ingresos promedio", f"${fin['revenue'].mean():,.0f}")
        fig = px.scatter(
            fin, x="budget", y="revenue", hover_name="title",
            hover_data={"budget": ":$,.0f", "revenue": ":$,.0f", "release_year": True, "popularity": ":.2f", "vote_average": ":.2f"},
            labels={"budget": "Presupuesto (USD)", "revenue": "Ingresos (USD)"},
        )
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Budget y revenue están disponibles únicamente para películas; las series se excluyen de este análisis.")

elif seccion == "Valoración vs. popularidad":
    st.divider()
    st.header("⭐ Valoración vs. popularidad por género")
    quality = explode_genres(ratings)
    quality_by_genre = quality.groupby("genres", as_index=False).agg(
        valoracion_promedio=("vote_average", "mean"),
        popularidad_promedio=("popularity", "mean"),
        contenidos=("title", "count"),
    )
    fig = px.scatter(
        quality_by_genre, x="valoracion_promedio", y="popularidad_promedio", size="contenidos", text="genres",
        hover_data=["contenidos"], labels={"valoracion_promedio": "Valoración promedio", "popularidad_promedio": "Popularidad promedio", "contenidos": "Cantidad de contenidos"},
        title="Valoración y popularidad según género",
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("La valoración promedio considera únicamente contenidos con al menos un voto (vote_count > 0).")

elif seccion == "Catálogo":
    st.divider()
    st.header("📋 Catálogo filtrado")
    st.caption(f"Mostrando {len(df_filtered):,} contenidos según los filtros seleccionados.")
    columns = ["title", "content_type", "release_year", "genres", "country", "language", "popularity", "vote_average", "vote_count"]
    st.dataframe(df_filtered[columns], use_container_width=True, hide_index=True)
