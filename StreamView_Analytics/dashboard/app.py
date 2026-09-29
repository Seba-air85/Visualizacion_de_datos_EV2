import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from src.preprocessing import load_clean_catalog, get_financial_subset

st.set_page_config(page_title="StreamView Analytics", page_icon="🎬", layout="wide")

@st.cache_data
def load_data():
    return load_clean_catalog()

df = load_data()

st.title("🎬 StreamView Analytics")
st.caption("Dashboard integrado de películas y series para analizar catálogo, popularidad, valoración y desempeño financiero.")

# Sidebar
st.sidebar.header("🧭 Navegación")
section = st.sidebar.radio("Ir a:", [
    "Resumen ejecutivo", "Análisis por género", "Evolución del catálogo",
    "Insights ejecutivos", "Desempeño financiero", "Valoración vs. popularidad", "Catálogo"
])

st.sidebar.header("🔎 Filtros")
types = st.sidebar.multiselect("Tipo de contenido", sorted(df["content_type"].dropna().unique()),
                               default=sorted(df["content_type"].dropna().unique()))
years = sorted(df["release_year"].dropna().unique(), reverse=True)
selected_year = st.sidebar.selectbox("Año de estreno", ["Todos"] + years)
genres = sorted({g.strip() for v in df["genres"].dropna() for g in str(v).split(",") if g.strip()})
selected_genres = st.sidebar.multiselect("Géneros", genres)

if st.sidebar.button("🔄 Restablecer filtros"):
    st.rerun()

df_filtered = df[df["content_type"].isin(types)].copy()
if selected_year != "Todos":
    df_filtered = df_filtered[df_filtered["release_year"] == selected_year]
if selected_genres:
    df_filtered = df_filtered[df_filtered["genres"].fillna("").apply(
        lambda x: any(g in [z.strip() for z in str(x).split(",")] for g in selected_genres)
    )]

if df_filtered.empty:
    st.warning("No existen registros que coincidan con los filtros seleccionados.")
    st.stop()

df_ratings = df_filtered[df_filtered["vote_count"].fillna(0) > 0]
df_financial = get_financial_subset(df_filtered)
avg_rating = df_ratings["vote_average"].mean()
avg_pop = df_filtered["popularity"].mean()
avg_rev = df_financial["revenue"].mean()

# KPIs always visible
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("🎬 Contenidos", f"{len(df_filtered):,}")
c2.metric("🎞️ Películas", f"{(df_filtered.content_type=='Movie').sum():,}")
c3.metric("📺 Series", f"{(df_filtered.content_type=='TV Show').sum():,}")
c4.metric("🔥 Popularidad promedio", f"{avg_pop:.2f}" if pd.notna(avg_pop) else "N/A")
c5.metric("⭐ Valoración promedio", f"{avg_rating:.2f}" if pd.notna(avg_rating) else "N/A")
st.caption(f"Los indicadores financieros consideran {len(df_financial):,} registros con presupuesto e ingresos disponibles; estos campos existen en la fuente de películas.")

# Common exploded genres
df_genres = df_filtered.dropna(subset=["genres"]).copy()
df_genres["genres"] = df_genres["genres"].str.split(",")
df_genres = df_genres.explode("genres")
df_genres["genres"] = df_genres["genres"].str.strip()

if section == "Resumen ejecutivo":
    st.header("📌 Resumen ejecutivo")
    st.write("La solución integra las fuentes de películas y series en un catálogo común, manteniendo el análisis financiero únicamente donde existen datos de presupuesto e ingresos.")
    by_type = df_filtered.groupby("content_type", as_index=False).agg(
        contenidos=("title","count"), popularidad=("popularity","mean"), valoracion=("vote_average","mean")
    )
    fig = px.bar(by_type, x="content_type", y="contenidos", text="contenidos",
                 labels={"content_type":"Tipo de contenido","contenidos":"Cantidad"})
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(by_type.round(2), use_container_width=True)

elif section == "Análisis por género":
    st.header("📊 Análisis por género")
    col1,col2 = st.columns(2)
    with col1:
        g = df_genres.groupby("genres", as_index=False).agg(
            popularidad_promedio=("popularity","mean"), contenidos=("title","nunique")
        ).sort_values("popularidad_promedio", ascending=False)
        fig = px.bar(g, x="popularidad_promedio", y="genres", orientation="h",
                     labels={"popularidad_promedio":"Popularidad promedio","genres":"Género"},
                     hover_data=["contenidos"])
        fig.update_layout(yaxis={"categoryorder":"total ascending"}, height=650)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        g2 = g.sort_values("contenidos", ascending=False)
        fig2 = px.scatter(g2, x="contenidos", y="popularidad_promedio", size="contenidos",
                          text="genres", hover_name="genres",
                          labels={"contenidos":"Cantidad de contenidos","popularidad_promedio":"Popularidad promedio"})
        fig2.update_traces(textposition="top center")
        st.plotly_chart(fig2, use_container_width=True)

elif section == "Evolución del catálogo":
    st.header("📈 Evolución del catálogo")
    yearly = df_filtered.dropna(subset=["release_year"]).groupby(
        ["release_year","content_type"], as_index=False).size().rename(columns={"size":"contenidos"})
    fig = px.line(yearly, x="release_year", y="contenidos", color="content_type", markers=True,
                  labels={"release_year":"Año de estreno","contenidos":"Cantidad de contenidos","content_type":"Tipo"})
    st.plotly_chart(fig, use_container_width=True)

elif section == "Insights ejecutivos":
    st.header("💡 Insights ejecutivos")
    g = df_genres.groupby("genres", as_index=False).agg(
        popularidad=("popularity","mean"), volumen=("title","nunique")
    )
    top_pop = g.loc[g["popularidad"].idxmax()]
    top_vol = g.loc[g["volumen"].idxmax()]
    st.info(f"🔥 Mayor popularidad promedio: **{top_pop.genres}** ({top_pop.popularidad:.2f}).")
    st.info(f"📚 Mayor volumen de catálogo: **{top_vol.genres}** ({int(top_vol.volumen):,} contenidos).")
    if len(df_financial) >= 2:
        corr = df_financial["budget"].corr(df_financial["revenue"])
        st.info(f"💰 Correlación presupuesto–ingresos en el subconjunto financiero: **{corr:.2f}**.")

elif section == "Desempeño financiero":
    st.header("💰 Desempeño financiero")
    if df_financial.empty:
        st.warning("Los filtros actuales no dejan registros con presupuesto e ingresos disponibles.")
    else:
        corr = df_financial["budget"].corr(df_financial["revenue"])
        c1,c2 = st.columns(2)
        c1.metric("💵 Ingreso promedio", f"${df_financial.revenue.mean():,.0f}")
        c2.metric("📈 Correlación presupuesto–ingresos", f"{corr:.2f}")
        fig = px.scatter(df_financial, x="budget", y="revenue", hover_name="title",
                         hover_data=["content_type","release_year","popularity","vote_average"],
                         labels={"budget":"Presupuesto (USD)","revenue":"Ingresos (USD)"})
        fig.update_xaxes(type="log"); fig.update_yaxes(type="log")
        st.plotly_chart(fig, use_container_width=True)

elif section == "Valoración vs. popularidad":
    st.header("⭐ Valoración vs. popularidad")
    q = df_filtered[df_filtered["vote_count"].fillna(0) > 0].copy()
    q["genres"] = q["genres"].fillna("").str.split(",")
    q = q.explode("genres"); q["genres"] = q["genres"].str.strip()
    q = q[q["genres"] != ""]
    g = q.groupby("genres", as_index=False).agg(
        valoracion=("vote_average","mean"), popularidad=("popularity","mean"), contenidos=("title","nunique")
    )
    fig = px.scatter(g, x="valoracion", y="popularidad", size="contenidos", text="genres",
                     hover_data=["contenidos"],
                     labels={"valoracion":"Valoración promedio","popularidad":"Popularidad promedio"})
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.header("📚 Catálogo filtrado")
    st.caption(f"Mostrando {len(df_filtered):,} contenidos según los filtros.")
    st.dataframe(df_filtered[["title","content_type","release_year","genres","language","popularity","vote_average","vote_count"]].head(100),
                 use_container_width=True)
