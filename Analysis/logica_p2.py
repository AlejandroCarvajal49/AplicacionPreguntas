import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

    # Cargar coordenadas
    coord_path = os.path.join(base_path, "..", "data", "municipios_unicos.csv")
    coord_path = os.path.abspath(coord_path)
    df_coord = pd.read_csv(coord_path)
    df = pd.merge(df, df_coord, on="cole_mcpio_ubicacion", how="left")

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
# BOXPLOTS POR MATERIA
# =========================
def generar_boxplots_materias(df):

    if df.empty:
        return go.Figure().update_layout(title="No hay datos")

    fig = make_subplots(rows=1, cols=3, subplot_titles=list(MATERIAS.keys()))

    for i, (nombre, col) in enumerate(MATERIAS.items(), 1):

        df_temp = df[[col, "cole_naturaleza"]].dropna()

        public = df_temp[df_temp["cole_naturaleza"] == "Público"][col]
        private = df_temp[df_temp["cole_naturaleza"] == "Privado"][col]

        fig.add_trace(
            go.Box(
                y=public,
                name="Público",
                marker_color="#1f77b4",
                showlegend=(i == 1)
            ),
            row=1, col=i
        )

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


# Helper para formatear periodo
def formato_periodo(p):
    """Convierte 20151 -> '2015-1', 20202 -> '2020-2', etc."""
    s = str(p)
    if len(s) >= 5:
        return f"{s[:4]}-{s[4:]}"
    return s


# =========================
# MAPA DE CALOR GEOGRÁFICO: Brecha por Municipio
# =========================
def generar_mapa_brecha(df, columna_materia, municipio_seleccionado="Todos"):
    """
    Mapa de Antioquia con puntos por municipio.
    Color = brecha (Privado - Público) en la materia seleccionada.
    Azul = público mejor, Rojo = privado mejor.
    Si no hay datos de ambos tipos, muestra el puntaje promedio general.
    """

    if df.empty or columna_materia not in df.columns:
        return go.Figure().update_layout(title="No hay datos")

    df_temp = df[["cole_mcpio_ubicacion", "lat", "lon", columna_materia, "cole_naturaleza"]].dropna()

    if df_temp.empty:
        return go.Figure().update_layout(title="No hay datos")

    # Calcular brecha por municipio
    medias = df_temp.groupby(
        ["cole_mcpio_ubicacion", "lat", "lon", "cole_naturaleza"]
    )[columna_materia].mean().reset_index()

    pivot = medias.pivot_table(
        index=["cole_mcpio_ubicacion", "lat", "lon"],
        columns="cole_naturaleza",
        values=columna_materia
    ).reset_index()

    if "Privado" in pivot.columns and "Público" in pivot.columns:
        pivot["brecha"] = pivot["Privado"] - pivot["Público"]
        pivot["brecha"] = pivot["brecha"].round(1)
        pivot["media_pub"] = pivot["Público"].round(1)
        pivot["media_priv"] = pivot["Privado"].round(1)
        # Solo municipios con ambos tipos
        pivot = pivot.dropna(subset=["brecha"])
        color_col = "brecha"
        color_label = "Brecha (Priv−Púb)"
    else:
        # Si no hay ambos tipos, mostrar promedio general
        pivot["promedio"] = df_temp.groupby(
            ["cole_mcpio_ubicacion", "lat", "lon"]
        )[columna_materia].mean().values
        color_col = "promedio"
        color_label = "Puntaje Promedio"

    if pivot.empty:
        return go.Figure().update_layout(title="No hay datos suficientes")

    # Tamaño y opacidad según filtro de municipio
    if municipio_seleccionado != "Todos":
        pivot["tamano"] = pivot["cole_mcpio_ubicacion"].apply(
            lambda x: 18 if x == municipio_seleccionado else 6
        )
        pivot["opacidad"] = pivot["cole_mcpio_ubicacion"].apply(
            lambda x: 1.0 if x == municipio_seleccionado else 0.15
        )
    else:
        pivot["tamano"] = 10
        pivot["opacidad"] = 0.85

    # Nombre de materia para el título
    nombre_materia = [k for k, v in MATERIAS.items() if v == columna_materia]
    nombre_materia = nombre_materia[0] if nombre_materia else columna_materia

    # Determinar rango simétrico para la escala de colores
    max_abs = max(abs(pivot[color_col].min()), abs(pivot[color_col].max()))
    if max_abs == 0:
        max_abs = 1

    fig = px.scatter_mapbox(
        pivot,
        lat="lat",
        lon="lon",
        color=color_col,
        hover_name="cole_mcpio_ubicacion",
        hover_data={
            "lat": False,
            "lon": False,
            "tamano": False,
            "opacidad": False,
            color_col: ":.1f",
            "media_pub": ":.1f" if "media_pub" in pivot.columns else False,
            "media_priv": ":.1f" if "media_priv" in pivot.columns else False,
        },
        color_continuous_scale=[
            [0, "#2166ac"],       # Azul fuerte (público mejor)
            [0.5, "#f7f7f7"],     # Blanco (sin brecha)
            [1, "#b2182b"]        # Rojo fuerte (privado mejor)
        ],
        range_color=[-max_abs, max_abs],
        size="tamano",
        size_max=18,
        mapbox_style="carto-positron",
        zoom=6.0,
        center={"lat": 6.85, "lon": -75.56},
        title=f"Brecha Público vs Privado — {nombre_materia} ({municipio_seleccionado})"
    )

    fig.update_traces(marker=dict(opacity=pivot["opacidad"].tolist()))

    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=600,
        coloraxis_colorbar=dict(
            title=dict(text=color_label)
        )
    )

    return fig