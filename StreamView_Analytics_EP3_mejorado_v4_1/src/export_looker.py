"""
export_looker.py
----------------
Genera el archivo que se sube a Looker Studio a partir del catálogo integrado.

Entrada : data/processed/catalogo_integrado.csv   (ya existe en el proyecto)
Salida  : data/looker/streamview_generos_looker.csv

Qué hace:
  1. Separa los géneros: una fila por cada combinación título x género
     (Looker Studio no puede separar "Comedy, Drama" en una celda).
  2. Quita columnas con saltos de línea (description, cast, director),
     que el conector de CSV de Looker Studio no acepta.
  3. Calcula columnas de ayuda (ganancia, pesos, valores atribuidos por género)
     para que los totales no se cuenten doble.

Cómo ejecutarlo (desde la carpeta raíz del proyecto):
    python src/export_looker.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "catalogo_integrado.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "looker" / "streamview_generos_looker.csv"

OUTPUT_COLUMNS = [
    "content_key", "title", "content_type", "release_year", "anio_incorporacion",
    "genero", "generos_titulo", "pais_principal", "language",
    "popularity", "vote_count", "vote_average", "vote_average_valida",
    "budget", "revenue", "ganancia", "resultado_financiero", "tiene_financiero",
    "n_generos", "peso", "peso_valoracion", "valoracion_x_peso", "popularidad_x_peso",
    "ingreso_atribuido", "presupuesto_atribuido", "ganancia_atribuida",
    "es_pelicula_valorada",
]


def build_looker_table(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    # Limpieza de texto: sin saltos de línea y sin espacios sobrantes.
    for col in ["title", "genres", "country", "language"]:
        d[col] = d[col].astype("string").str.replace(r"[\r\n]+", " ", regex=True).str.strip()

    d["date_added"] = pd.to_datetime(d["date_added"], errors="coerce")
    d["anio_incorporacion"] = d["date_added"].dt.year.astype("Int64")
    d["pais_principal"] = d["country"].str.split(",").str[0].str.strip().fillna("Sin dato")
    d["language"] = d["language"].fillna("Sin dato")

    # Valoración válida: solo títulos con al menos 1 voto.
    d["vote_average_valida"] = d["vote_average"].where(d["vote_count"] > 0)

    # Desempeño financiero (solo películas con budget y revenue).
    d["ganancia"] = d["revenue"] - d["budget"]
    d["resultado_financiero"] = np.where(
        d["ganancia"].isna(), "Sin dato financiero",
        np.where(d["ganancia"] > 0, "Ganancia",
                 np.where(d["ganancia"] < 0, "Pérdida", "Equilibrio")),
    )
    d["tiene_financiero"] = d["ganancia"].notna().astype(int)

    # Géneros: lista por título ("Sin género" si no tiene).
    d["genre_list"] = d["genres"].fillna("").apply(
        lambda x: [g.strip() for g in x.split(",") if g.strip()] or ["Sin género"]
    )
    d["n_generos"] = d["genre_list"].apply(len)

    # Pesos y valores atribuidos: cada título suma 1 en total entre sus géneros.
    d["peso"] = 1 / d["n_generos"]
    d["ingreso_atribuido"] = d["revenue"] / d["n_generos"]
    d["presupuesto_atribuido"] = d["budget"] / d["n_generos"]
    d["ganancia_atribuida"] = d["ganancia"] / d["n_generos"]
    d["peso_valoracion"] = d["peso"].where(d["vote_average_valida"].notna())
    d["valoracion_x_peso"] = d["vote_average_valida"] * d["peso"]
    d["popularidad_x_peso"] = d["popularity"] * d["peso"]
    d["es_pelicula_valorada"] = ((d["content_type"] == "Movie") & (d["vote_count"] > 0)).astype(int)

    # Una fila por título x género.
    out = d.explode("genre_list").rename(columns={"genre_list": "genero"})
    out["genero"] = out["genero"].str.strip()
    out = out.rename(columns={"genres": "generos_titulo"})
    return out[OUTPUT_COLUMNS]


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró {INPUT_PATH}. Ejecuta primero el preprocesamiento "
            "(src/preprocessing.py) para generar el catálogo integrado."
        )
    df = pd.read_csv(INPUT_PATH)
    table = build_looker_table(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"Archivo generado: {OUTPUT_PATH}")
    print(f"Filas: {len(table):,} | Títulos únicos: {table['content_key'].nunique():,} "
          f"| Géneros: {table['genero'].nunique()}")


if __name__ == "__main__":
    main()

