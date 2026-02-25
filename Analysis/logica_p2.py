import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# =========================
# CARGA DE DATOS
# =========================
def cargar_datos(path="data/saber11_Antioquia_clean.csv"):
    base_path = os.path.dirname(__file__)
    full_path = os.path.join(base_path, "..", path)
    full_path = os.path.abspath(full_path)

    df = pd.read_csv(full_path)

    df["cole_naturaleza"] = df["cole_naturaleza"].replace({
        "OFICIAL": "Público",
        "NO OFICIAL": "Privado"
    })

    return df


MATERIAS = {
    "Matemáticas": "punt_matematicas",
    "Lectura Crítica": "punt_lectura_critica",
    "Ciencias Naturales": "punt_c_naturales"
}


# =========================
# FILTRAR DATOS
# =========================
def filtrar_datos(df, municipio="Todos", periodo=None):
    df = df.copy()
    if municipio != "Todos":
        df = df[df["cole_mcpio_ubicacion"] == municipio]
    if periodo:
        df = df[df["periodo"].isin(periodo)]
    return df


# =========================
# CALCULAR BRECHAS
# =========================
def calcular_brechas(df):
    brechas = {}
    for nombre, col in MATERIAS.items():
        df_temp = df[[col, "cole_naturaleza"]].dropna()
        public = df_temp[df_temp["cole_naturaleza"] == "Público"][col]
        private = df_temp[df_temp["cole_naturaleza"] == "Privado"][col]
        if len(public) > 0 and len(private) > 0:
            brecha = private.mean() - public.mean()
            media_pub = public.mean()
            media_priv = private.mean()
            brechas[nombre] = {
                "brecha": round(brecha, 1),
                "media_publico": round(media_pub, 1),
                "media_privado": round(media_priv, 1)
            }
        else:
            brechas[nombre] = {
                "brecha": None,
                "media_publico": None,
                "media_privado": None
            }
    return brechas


# =========================
# BOXPLOTS POR MATERIA (sin anotación de brecha, ahora va aparte)
# =========================
def generar_boxplots_materias(df):

    if df.empty:
        return go.Figure().update_layout(title="No hay datos")

    fig = make_subplots(rows=1, cols=3, subplot_titles=list(MATERIAS.keys()))

    for i, (nombre, col) in enumerate(MATERIAS.items(), 1):

        df_temp = df[[col, "cole_naturaleza"]].dropna()

        public = df_temp[df_temp["cole_naturaleza"] == "Público"][col]
        private = df_temp[df_temp["cole_naturaleza"] == "Privado"][col]

        # BOX PUBLICO
        fig.add_trace(
            go.Box(
                y=public,
                name="Público",
                marker_color="#1f77b4",
                showlegend=(i == 1)
            ),
            row=1, col=i
        )

        # BOX PRIVADO
        fig.add_trace(
            go.Box(
                y=private,
                name="Privado",
                marker_color="#d62728",
                showlegend=(i == 1)
            ),
            row=1, col=i
        )

    fig.update_layout(
        title="Distribución por Materia (Público vs Privado)",
        height=500
    )

    return fig