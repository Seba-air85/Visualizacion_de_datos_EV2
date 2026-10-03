"""
analysis.py

Funciones de análisis que reproducen los hallazgos y gráficos del
informe ejecutivo EP1 (sección 5. "Análisis exploratorio mediante
visualizaciones" y sección 6. "Selección y justificación de los gráficos").

Géneros de alto desempeño (definidos en el informe): Adventure, Science
Fiction, Animation, Family, Fantasy — los 5 géneros con mayor popularidad
promedio detectados en el análisis.

Uso:
    from src.preprocessing import load_clean_movies, explode_genres
    from src.analysis import popularity_by_genre, genre_distribution, ...
"""

import pandas as pd

HIGH_PERFORMANCE_GENRES = [
    "Adventure", "Science Fiction", "Animation", "Family", "Fantasy"
]


def popularity_by_genre(df_exploded: pd.DataFrame, top_n: int = 10) -> pd.Series:
    """
    Popularidad promedio por género (Fig. 1 del informe: barras horizontales).
    df_exploded: dataframe ya procesado con explode_genres().
    """
    return (
        df_exploded.groupby("genres")["popularity"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
    )


def genre_distribution(df_exploded: pd.DataFrame, top_n: int = 12) -> pd.Series:
    """
    Cantidad de títulos por género (Fig. 2 del informe: treemap).
    Nota: la suma supera el 100% del catálogo porque una película
    puede pertenecer a más de un género.
    """
    return df_exploded["genres"].value_counts().head(top_n)


def popularity_vs_revenue(df_financial: pd.DataFrame) -> pd.DataFrame:
    """
    Relación entre popularidad e ingresos (Fig. 3 del informe: dispersión).
    df_financial: dataframe filtrado con get_financial_subset() —
    solo películas con budget y revenue disponibles (n=3.540, 22,1%).
    Devuelve las columnas necesarias más la correlación de Pearson.
    """
    subset = df_financial[["title", "popularity", "revenue"]].dropna()
    correlation = subset["popularity"].corr(subset["revenue"])
    return subset, correlation


def catalog_evolution_by_year(df_exploded: pd.DataFrame) -> pd.DataFrame:
    """
    Evolución de la composición del catálogo por año de estreno
    (Fig. 4 del informe: líneas). Compara el % de estrenos que
    corresponden a géneros de alto desempeño vs. el resto del catálogo.
    """
    df_exploded = df_exploded.copy()
    df_exploded["is_high_performance"] = df_exploded["genres"].isin(
        HIGH_PERFORMANCE_GENRES
    )

    yearly = (
        df_exploded.groupby(["release_year", "is_high_performance"])["show_id"]
        .nunique()
        .unstack(fill_value=0)
    )
    yearly_pct = yearly.div(yearly.sum(axis=1), axis=0) * 100
    yearly_pct.columns = ["resto_catalogo_pct", "alto_desempeno_pct"]
    return yearly_pct


def revenue_by_genre(df_financial_exploded: pd.DataFrame) -> pd.Series:
    """
    Ingreso promedio por género, usando solo el subconjunto con datos
    financieros completos. Respalda la cifra clave del informe:
    "los géneros minoritarios generan hasta 5 veces más ingresos por
    título que Drama y Comedy".
    """
    return (
        df_financial_exploded.groupby("genres")["revenue"]
        .mean()
        .sort_values(ascending=False)
    )


def kpi_summary(df: pd.DataFrame, df_exploded: pd.DataFrame, df_financial: pd.DataFrame) -> dict:
    """KPIs resumen para el Anexo del informe / vista ejecutiva del dashboard."""
    pop_genre = popularity_by_genre(df_exploded, top_n=1)
    rev_genre = revenue_by_genre(
        df_financial.pipe(lambda d: d.assign(genres=d["genres"]))
        if "genres" in df_financial.columns
        else df_financial
    )
    _, corr = popularity_vs_revenue(df_financial)

    return {
        "total_peliculas": len(df),
        "peliculas_con_datos_financieros": len(df_financial),
        "pct_datos_financieros": round(len(df_financial) / len(df) * 100, 1),
        "top_genero_popularidad": pop_genre.index[0] if len(pop_genre) else None,
        "correlacion_popularidad_ingresos": round(corr, 2) if corr == corr else None,
    }


if __name__ == "__main__":
    from preprocessing import load_clean_movies, explode_genres, get_financial_subset

    df = load_clean_movies()
    df_exp = explode_genres(df)
    df_fin = get_financial_subset(df)
    df_fin_exp = explode_genres(df_fin)

    print("=== Popularidad promedio por género (Top 10) ===")
    print(popularity_by_genre(df_exp))
    print()
    print("=== Distribución del catálogo por género (Top 12) ===")
    print(genre_distribution(df_exp))
    print()
    _, corr = popularity_vs_revenue(df_fin)
    print(f"=== Correlación popularidad-ingresos: r = {corr:.2f} ===")
    print()
    print("=== Ingreso promedio por género ===")
    print(revenue_by_genre(df_fin_exp))
