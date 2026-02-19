import os
import numpy as np
import pandas as pd

RAW_PATH   = os.path.join("Data", "saber11_Antioquia_raw.csv")
CLEAN_PATH = os.path.join("Data", "saber11_Antioquia_clean.csv")

SCORE_COLS = [
    "punt_ingles", "punt_matematicas", "punt_sociales_ciudadanas",
    "punt_c_naturales", "punt_lectura_critica", "punt_global",
]

SCORE_RANGE = (0, 500)

def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    obj_cols = df.select_dtypes(include="object").columns
    if len(obj_cols) > 0:
        df[obj_cols] = df[obj_cols].apply(
            lambda col: (
                col.astype("string")
                   .str.strip()
                   .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
                   .str.replace('^"(.*)"$', r"\1", regex=True)
            )
        )
    return df

def run(in_path: str = RAW_PATH, out_path: str = CLEAN_PATH) -> pd.DataFrame:
    df = pd.read_csv(in_path, low_memory=False)
    print(f"[load] {df.shape[0]:,} filas × {df.shape[1]} columnas")

    # 1) Limpieza general de texto
    df = clean_text(df)

    # 2) Regla negocio: cole_bilingue vacío -> 'Y'
    if "cole_bilingue" in df.columns:
        df["cole_bilingue"] = df["cole_bilingue"].fillna("Y")

    # 3) Convertir puntajes a numérico
    for c in SCORE_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # 4) Puntajes fuera de rango -> NaN
    lo, hi = SCORE_RANGE
    for c in SCORE_COLS:
        if c in df.columns:
            df.loc[(df[c] < lo) | (df[c] > hi), c] = np.nan

    # 5) Eliminar filas si falta algún puntaje
    before = len(df)
    df = df.dropna(subset=[c for c in SCORE_COLS if c in df.columns])
    print(f"[drop_scores] Eliminadas {before - len(df):,} filas por puntajes faltantes")

    # 6) Duplicados (opcional)
    before = len(df)
    df = df.drop_duplicates()
    print(f"[dedup] Eliminadas {before - len(df):,} filas duplicadas")

    # 7) Guardar
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"[save] Guardado en: {out_path}")
    print(f"[done] {df.shape[0]:,} filas × {df.shape[1]} columnas")

    return df

if __name__ == "__main__":
    run()
    
    