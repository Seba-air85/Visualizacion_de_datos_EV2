"""
preprocessing.py

Carga y limpieza del dataset de películas (Netflix Movies Detailed up to 2025).
Aplica las decisiones de calidad de datos documentadas en el informe EP1
(sección 4.1 "Calidad de los datos y limitaciones detectadas").

Uso:
    from src.preprocessing import load_clean_movies
    df = load_clean_movies()
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
MOVIES_FILE = RAW_DIR / "netflix_movies_detailed_up_to_2025.csv"
TV_SHOWS_FILE = RAW_DIR / "netflix_tv_shows_detailed_up_to_2025.csv"


def load_raw_movies() -> pd.DataFrame:
    """
    Carga el dataset de películas sin transformaciones de limpieza.

    Se usa na_values para que strings como '', 'NULL', 'null', 'N/A' sean
    interpretados correctamente por pandas como valores faltantes (NaN),
    en caso de que existan en el archivo original con ese formato.
    """
    return pd.read_csv(
        MOVIES_FILE,
        na_values=["", "NULL", "null", "N/A", "n/a", "NaN"],
    )


def load_clean_movies() -> pd.DataFrame:
    """
    Carga y limpia el dataset de películas.

    Decisiones aplicadas (documentadas en el informe, sección 4.1):
    - 'duration' se descarta: está vacía en el 100% de los registros.
    - 'rating' se descarta: es idéntica a 'vote_average' en el 100% de los
      casos, no es la clasificación por edad que describe el diccionario
      de datos del caso.
    - budget/revenue == 0 se tratan como NaN (nulos disfrazados). Los KPIs
      financieros solo deben calcularse sobre el subconjunto con ambos
      valores disponibles (~3.540 de 16.000 películas, 22,1%), según la
      Regla de Negocio N°6 del caso.
    - 'date_added' se convierte a fecha.
    - Duplicados por título + año de estreno se marcan (no se eliminan
      automáticamente porque el informe indica que no tienen impacto
      relevante en los indicadores agregados; se dejan visibles para
      quien quiera excluirlos).
    """
    df = load_raw_movies().copy()

    df = df.drop(columns=["duration", "rating"], errors="ignore")

    df["budget"] = df["budget"].replace(0, pd.NA)
    df["revenue"] = df["revenue"].replace(0, pd.NA)

    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")

    df["is_duplicate_title_year"] = df.duplicated(
        subset=["title", "release_year"], keep=False
    )

    return df



def load_raw_tv_shows() -> pd.DataFrame:
    """Carga el dataset de series sin transformaciones de limpieza."""
    return pd.read_csv(
        TV_SHOWS_FILE,
        na_values=["", "NULL", "null", "N/A", "n/a", "NaN"],
    )


def load_clean_tv_shows() -> pd.DataFrame:
    """
    Carga y limpia el dataset de series usando la misma metodología general
    aplicada al dataset de películas.

    - 'rating' se descarta porque es idéntica a 'vote_average'.
    - 'duration' se descarta porque todos los registros tienen el mismo valor
      ('1 Seasons') y no aporta variación al análisis.
    - 'date_added' se convierte a fecha.
    - Se marca, sin eliminar automáticamente, la duplicación por título+año.
    - Los valores faltantes se mantienen como NaN; no se imputan cuando no
      existe información suficiente para hacerlo sin inventar datos.
    """
    df = load_raw_tv_shows().copy()
    df = df.drop(columns=["rating", "duration"], errors="ignore")
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["is_duplicate_title_year"] = df.duplicated(
        subset=["title", "release_year"], keep=False
    )
    return df

def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    """
    'genres' es multivalor (separado por coma). Esta función devuelve una
    fila por cada combinación película-género, para poder agrupar por
    género. Una misma película puede aparecer en más de una fila
    (por eso la suma de participación por género supera el 100% del
    catálogo, como se indica en el informe).
    """
    result = df.copy()
    result["genres"] = result["genres"].str.split(",")
    result = result.explode("genres")
    result["genres"] = result["genres"].str.strip()
    return result


def get_financial_subset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve solo las películas con budget y revenue disponibles
    simultáneamente (subconjunto usado para todo KPI financiero,
    Regla de Negocio N°6 del caso).
    """
    return df.dropna(subset=["budget", "revenue"]).copy()


if __name__ == "__main__":
    df = load_clean_movies()
    print(f"Películas cargadas: {len(df)}")
    print(f"Con datos financieros completos: {len(get_financial_subset(df))}")
    print(f"Duplicados título+año detectados: {df['is_duplicate_title_year'].sum()}")
