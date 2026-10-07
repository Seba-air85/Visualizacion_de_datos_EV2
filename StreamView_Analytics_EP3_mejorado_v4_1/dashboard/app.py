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


def financial_by_genre(data):
    """Distribuye ingresos y ganancia entre los géneros de cada película para evitar doble conteo."""
    fin = get_financial_subset(data).copy()
    if fin.empty:
        return pd.DataFrame(columns=["genres", "ingresos_atribuidos", "ganancia_atribuida", "peliculas"])
    fin["genre_count"] = fin["genres"].fillna("").apply(
        lambda x: max(1, len([g for g in str(x).split(",") if g.strip()]))
    )
    fin["ingreso_atribuido"] = fin["revenue"] / fin["genre_count"]
    fin["ganancia_atribuida"] = (fin["revenue"] - fin["budget"]) / fin["genre_count"]
    ex = explode_genres(fin)
    return ex.groupby("genres", as_index=False).agg(
        ingresos_atribuidos=("ingreso_atribuido", "sum"),
        ganancia_atribuida=("ganancia_atribuida", "sum"),
        peliculas=("title", "nunique"),
    )


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

    st.subheader("⭐ Calidad de películas por género")
    st.caption(
        "La calidad se mide como la valoración promedio (0–10) de películas con al menos un voto. "
        "Para el ranking se muestran géneros con al menos 100 películas valoradas, reduciendo el efecto de muestras muy pequeñas."
    )
    movies_rated = df_filtered[(df_filtered["content_type"] == "Movie") & (df_filtered["vote_count"] > 0)].copy()
    movies_genres = explode_genres(movies_rated)
    quality_movies = movies_genres.groupby("genres", as_index=False).agg(
        calidad_promedio=("vote_average", "mean"),
        peliculas_valoradas=("title", "nunique"),
        votos=("vote_count", "sum"),
    )
    quality_movies = quality_movies[quality_movies["peliculas_valoradas"] >= 100].sort_values("calidad_promedio", ascending=False)
    if quality_movies.empty:
        st.info("No hay suficientes películas valoradas por género para el filtro actual.")
    else:
        best_q = quality_movies.iloc[0]
        st.metric("🏅 Género con mayor calidad promedio", f"{best_q['genres']} · {best_q['calidad_promedio']:.2f}/10")
        fig_q = px.bar(
            quality_movies.head(15).sort_values("calidad_promedio"),
            x="calidad_promedio", y="genres", orientation="h",
            hover_data={"peliculas_valoradas": True, "votos": ":,.0f"},
            labels={"calidad_promedio": "Valoración promedio (0–10)", "genres": "Género",
                    "peliculas_valoradas": "Películas valoradas", "votos": "Votos"},
        )
        fig_q.update_xaxes(range=[0, 10])
        st.plotly_chart(fig_q, use_container_width=True)

    st.subheader("🌳 Treemap de composición por tipo y género")
    tree = df_genres.groupby(["content_type", "genres"], as_index=False).agg(contenidos=("title", "count"))
    st.plotly_chart(px.treemap(tree, path=["content_type", "genres"], values="contenidos"), use_container_width=True)

elif seccion == "Evolución del catálogo":
    st.divider()
    st.header("📈 Evolución temporal")

    st.subheader("Cantidad de contenidos estrenados cada año")
    st.caption(
        "Muestra cuántos títulos del catálogo actual fueron estrenados en cada año. "
        "La línea total permite ver el crecimiento o disminución del volumen de estrenos; las líneas por tipo permiten comparar películas y series."
    )
    releases_type = (
        df_filtered.dropna(subset=["release_year", "content_type"])
        .groupby(["release_year", "content_type"], as_index=False).size()
        .rename(columns={"size": "contenidos"}).sort_values("release_year")
    )
    releases_total = (
        df_filtered.dropna(subset=["release_year"])
        .groupby("release_year", as_index=False).size()
        .rename(columns={"size": "contenidos"}).sort_values("release_year")
    )
    fig = px.line(
        releases_type, x="release_year", y="contenidos", color="content_type", markers=False,
        labels={"release_year": "Año de estreno", "contenidos": "Cantidad de contenidos", "content_type": "Tipo"},
    )
    fig.add_scatter(x=releases_total["release_year"], y=releases_total["contenidos"], mode="lines", name="Total", line=dict(width=4, dash="dot"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Películas estrenadas por año según género")
    st.caption(
        "Cada línea representa un género y permite comparar cómo cambia la cantidad de películas estrenadas a lo largo del tiempo. "
        "Si no seleccionas géneros en la barra lateral, se muestran los 5 géneros con mayor volumen de películas."
    )
    movies = df_filtered[df_filtered["content_type"] == "Movie"].copy()
    movie_genres = explode_genres(movies)
    if selected_genres:
        line_genres = [g for g in selected_genres if g in movie_genres["genres"].unique()]
    else:
        line_genres = movie_genres["genres"].value_counts().head(5).index.tolist()
    movie_year_genre = (
        movie_genres[movie_genres["genres"].isin(line_genres)]
        .dropna(subset=["release_year"])
        .groupby(["release_year", "genres"], as_index=False)["title"].nunique()
        .rename(columns={"title": "peliculas"}).sort_values("release_year")
    )
    if movie_year_genre.empty:
        st.info("No hay películas suficientes para construir la evolución por género con los filtros actuales.")
    else:
        fig_genre = px.line(
            movie_year_genre, x="release_year", y="peliculas", color="genres", markers=False,
            labels={"release_year": "Año de estreno", "peliculas": "Cantidad de películas", "genres": "Género"},
        )
        st.plotly_chart(fig_genre, use_container_width=True)

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
    st.caption("Diferencia clave: release_year indica cuándo se estrenó el contenido; date_added indica cuándo fue incorporado a la plataforma.")

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
    st.caption(
        "La relación presupuesto–ingresos muestra si las películas con mayor inversión también generan mayores ingresos. "
        "Cada punto representa una película; cuanto más arriba se ubica, mayores son sus ingresos. Las escalas son logarítmicas para hacer comparables montos muy distintos."
    )
    fin = get_financial_subset(df_filtered).copy()
    if len(fin) < 2:
        st.warning("No hay suficientes películas con presupuesto e ingresos disponibles para el filtro actual.")
    else:
        corr = fin["budget"].corr(fin["revenue"])
        fin["ganancia"] = fin["revenue"] - fin["budget"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📈 Correlación presupuesto-ingresos", f"{corr:.2f}")
        c2.metric("💵 Presupuesto promedio", f"${fin['budget'].mean():,.0f}")
        c3.metric("💰 Ingresos promedio", f"${fin['revenue'].mean():,.0f}")
        c4.metric("📊 Ganancia total", f"${fin['ganancia'].sum():,.0f}")
        fig = px.scatter(
            fin, x="budget", y="revenue", hover_name="title",
            hover_data={"budget": ":$,.0f", "revenue": ":$,.0f", "ganancia": ":$,.0f", "release_year": True, "popularity": ":.2f", "vote_average": ":.2f"},
            labels={"budget": "Presupuesto (USD)", "revenue": "Ingresos (USD)", "ganancia": "Ganancia/Pérdida (USD)"},
        )
        fig.update_xaxes(type="log")
        fig.update_yaxes(type="log")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Ingresos y ganancias atribuidos por género")
        st.caption(
            "Para evitar contar varias veces el ingreso de una película con múltiples géneros, su ingreso y ganancia se distribuyen proporcionalmente entre sus géneros. "
            "Así se puede comparar qué géneros aportan más o menos ingresos dentro de las películas con datos financieros disponibles."
        )
        genre_fin = financial_by_genre(df_filtered).sort_values("ingresos_atribuidos", ascending=False)
        if not genre_fin.empty:
            cg1, cg2 = st.columns(2)
            with cg1:
                top_rev = genre_fin.iloc[0]
                low_rev = genre_fin.iloc[-1]
                st.metric("🏆 Género con más ingresos atribuidos", top_rev["genres"], f"${top_rev['ingresos_atribuidos']:,.0f}")
                st.metric("📉 Género con menos ingresos atribuidos", low_rev["genres"], f"${low_rev['ingresos_atribuidos']:,.0f}")
            with cg2:
                best_profit = genre_fin.sort_values("ganancia_atribuida", ascending=False).iloc[0]
                worst_profit = genre_fin.sort_values("ganancia_atribuida", ascending=True).iloc[0]
                st.metric("💚 Mayor ganancia atribuida", best_profit["genres"], f"${best_profit['ganancia_atribuida']:,.0f}")
                st.metric("🔻 Menor ganancia atribuida", worst_profit["genres"], f"${worst_profit['ganancia_atribuida']:,.0f}")
            show_genres = pd.concat([genre_fin.head(8), genre_fin.tail(5)]).drop_duplicates("genres").sort_values("ingresos_atribuidos")
            fig_g = px.bar(
                show_genres, x="ingresos_atribuidos", y="genres", orientation="h",
                hover_data={"ganancia_atribuida": ":$,.0f", "peliculas": True},
                labels={"ingresos_atribuidos": "Ingresos atribuidos (USD)", "genres": "Género",
                        "ganancia_atribuida": "Ganancia atribuida", "peliculas": "Películas"},
            )
            st.plotly_chart(fig_g, use_container_width=True)
        st.caption("Budget y revenue están disponibles únicamente para películas; las series se excluyen de este análisis.")

elif seccion == "Valoración vs. popularidad":
    st.divider()
    st.header("⭐ Valoración vs. popularidad por género")
    st.caption(
        "Cada burbuja representa un género. Hacia la derecha significa mejor valoración promedio y hacia arriba mayor popularidad promedio; "
        "el tamaño de la burbuja representa la cantidad de contenidos. Los géneros ubicados en la zona superior derecha combinan mejor valoración y mayor popularidad."
    )
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
    catalog = df_filtered.copy()
    catalog["ganancia"] = catalog["revenue"] - catalog["budget"]
    catalog["resultado_financiero"] = catalog["ganancia"].apply(
        lambda x: "Ganancia" if pd.notna(x) and x > 0 else ("Pérdida" if pd.notna(x) and x < 0 else "Sin dato / equilibrio")
    )
    columns = ["title", "content_type", "release_year", "genres", "country", "language", "popularity", "vote_average", "vote_count", "budget", "revenue", "ganancia", "resultado_financiero"]

    valid_profit = catalog["ganancia"].dropna()
    max_abs = valid_profit.abs().max() if not valid_profit.empty else 1
    max_abs = max(max_abs, 1)

    def profit_color(v):
        if pd.isna(v):
            return ""
        intensity = min(abs(v) / max_abs, 1.0)
        # Fondo progresivo: rojo para pérdida y verde para ganancia.
        if v > 0:
            lightness = 96 - 42 * intensity
            return f"background-color: hsl(125, 55%, {lightness}%); color: black"
        if v < 0:
            lightness = 96 - 38 * intensity
            return f"background-color: hsl(0, 70%, {lightness}%); color: black"
        return "background-color: #f2f2f2; color: black"

    # Pandas Styler tiene un límite de celdas renderizadas. Para mantener el
    # coloreado financiero sin cargar decenas de miles de filas a la vez,
    # el catálogo se pagina y solo se estiliza la página visible.
    page_size = st.selectbox(
        "Filas por página", [50, 100, 250, 500], index=1, key="catalog_page_size"
    )
    total_rows = len(catalog)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page = st.number_input(
        "Página", min_value=1, max_value=total_pages, value=1, step=1, key="catalog_page"
    )
    start = (int(page) - 1) * page_size
    end = min(start + page_size, total_rows)
    catalog_page = catalog.iloc[start:end][columns]

    styled = (
        catalog_page.style
        .map(profit_color, subset=["ganancia"])
        .format({
            "popularity": "{:.2f}", "vote_average": "{:.2f}",
            "budget": lambda x: "" if pd.isna(x) else f"${x:,.0f}",
            "revenue": lambda x: "" if pd.isna(x) else f"${x:,.0f}",
            "ganancia": lambda x: "" if pd.isna(x) else f"${x:,.0f}",
        })
    )
    st.caption(f"Mostrando filas {start + 1:,}–{end:,} de {total_rows:,} · Página {int(page)} de {total_pages}")
    st.dataframe(styled, use_container_width=True, hide_index=True, height=650)
    st.caption(
        "🟢 Verde = ganancia (revenue − budget > 0); cuanto más intenso el verde, mayor ganancia. "
        "🔴 Rojo = pérdida; cuanto más intenso el rojo, mayor pérdida. Sin color = no hay datos financieros suficientes. "
        "Esta clasificación aplica a películas con budget y revenue disponibles."
    )
