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


# =========================
# BOXPLOTS + BRECHAS POR MATERIA
# =========================
def generar_boxplots_materias(df, municipio="Todos", periodo=None):

    df = df.copy()

    # FILTROS
    if municipio != "Todos":
        df = df[df["cole_mcpio_ubicacion"] == municipio]

    if periodo:
        df = df[df["periodo"].isin(periodo)]

    if df.empty:
        return go.Figure().update_layout(title="No hay datos")

    materias = {
        "Matemáticas": "punt_matematicas",
        "Lectura Crítica": "punt_lectura_critica",
        "Ciencias Naturales": "punt_c_naturales"
    }

    fig = make_subplots(rows=1, cols=3, subplot_titles=list(materias.keys()))

    brechas = {}

    for i, (nombre, col) in enumerate(materias.items(), 1):

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

        # BRECHA
        if len(public) > 0 and len(private) > 0:
            brecha = private.mean() - public.mean()
            brechas[nombre] = brecha

            fig.add_annotation(
                x=i - 1,
                y=max(df_temp[col]),
                text=f"Δ {brecha:.1f}",
                showarrow=False,
                font=dict(size=13),
                xref="x domain",
                yref="y"
            )

    fig.update_layout(
        title="Distribución y Brecha por Materia (Público vs Privado)",
        height=500
    )

    return fig