import dash
from dash import html, dcc, Input, Output
import pandas as pd

from Analysis.logica_p2 import cargar_datos, generar_boxplot_brecha

# =========================
# REGISTRO DE PÁGINA
# =========================
dash.register_page(__name__, path="/pregunta_2")

# =========================
# CARGAR DATOS
# =========================
df = cargar_datos()

# =========================
# OPCIONES FILTROS
# =========================
municipios = ["Todos"] + sorted(df["cole_mcpio_ubicacion"].dropna().unique())

periodos = sorted(df["periodo"].dropna().unique())

# =========================
# LAYOUT
# =========================
layout = html.Div([

    html.H1("Pregunta 2: Calidad Educativa Público vs Privado"),

    html.Label("Selecciona Municipio:"),
    dcc.Dropdown(
        id="filtro-municipio",
        options=[{"label": m, "value": m} for m in municipios],
        value="Todos"
    ),

    html.Br(),

    html.Label("Selecciona Periodo(s):"),
    dcc.Dropdown(
        id="filtro-periodo",
        options=[{"label": str(p), "value": p} for p in periodos],
        value=periodos,
        multi=True
    ),

    html.Br(),

    dcc.Graph(id="grafica-boxplot-brecha")

])

# =========================
# CALLBACK
# =========================
@dash.callback(
    Output("grafica-boxplot-brecha", "figure"),
    Input("filtro-municipio", "value"),
    Input("filtro-periodo", "value")
)
def actualizar_grafica(municipio, periodo):

    fig = generar_boxplot_brecha(
        df,
        municipio=municipio,
        periodo=periodo
    )

    return fig