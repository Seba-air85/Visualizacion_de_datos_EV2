"""
preprocessing.py
Carga, limpieza e integración de las fuentes de películas y series de StreamView Analytics.
"""
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
MOVIES_FILE = RAW_DIR / "netflix_movies_detailed_up_to_2025.csv"
TV_FILE = RAW_DIR / "netflix_tv_shows_detailed_up_to_2025.csv"

def _read(path):
    return pd.read_csv(path, na_values=["", "NULL", "null", "N/A", "n/a", "NaN"])

def load_clean_movies():
    df = _read(MOVIES_FILE).copy()
    df["content_type"] = "Movie"
    return _clean(df)

def load_clean_tv():
    df = _read(TV_FILE).copy()
    df["content_type"] = "TV Show"
    # La fuente de series no contiene variables financieras.
    df["budget"] = pd.NA
    df["revenue"] = pd.NA
    return _clean(df)

def _clean(df):
    # duration y rating no se usan: duration presenta información incompatible
    # entre fuentes y rating replica vote_average en el dataset de películas.
    df = df.drop(columns=["duration", "rating"], errors="ignore")
    df["budget"] = pd.to_numeric(df["budget"], errors="coerce").replace(0, pd.NA)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").replace(0, pd.NA)
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["is_duplicate_title_year"] = df.duplicated(
        subset=["title", "release_year"], keep=False
    )
    return df

def load_catalog():
    """Integra las dos fuentes corporativas en un catálogo común."""
    movies = load_clean_movies()
    tv = load_clean_tv()
    return pd.concat([movies, tv], ignore_index=True, sort=False)

def load_clean_catalog():
    return load_catalog()

def explode_genres(df):
    result = df.copy()
    result["genres"] = result["genres"].fillna("").str.split(",")
    result = result.explode("genres")
    result["genres"] = result["genres"].str.strip()
    return result[result["genres"] != ""]

def get_financial_subset(df):
    """Películas con presupuesto e ingresos disponibles."""
    return df.dropna(subset=["budget", "revenue"]).copy()

if __name__ == "__main__":
    df = load_catalog()
    financial = get_financial_subset(df)
    print(f"Registros integrados: {len(df):,}")
    print(df["content_type"].value_counts())
    print(f"Registros con datos financieros: {len(financial):,}")
