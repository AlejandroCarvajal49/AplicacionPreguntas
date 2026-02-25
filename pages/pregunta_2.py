import dash
from dash import html, dcc, Input, Output
import pandas as pd

from Analysis.logica_p2 import cargar_datos, generar_boxplot_brecha

dash.register_page(__name__, path="/pregunta_2")

# =========================
# CARGAR DATA
# =========================
df = cargar_datos()

municipios = ["Todos"] + sorted(df["cole_municipio"].dropna().unique())

# Slider años (si existe)
if "periodo" in df.columns:
    min_year = int(df["periodo"].min())
    max_year = int(df["periodo"].max())
else:
    min_year, max_year = 2010, 2020


# =========================
# LAYOUT
# =========================
layout = html.Div([

    html.H2("PREGUNTA 2: PÚBLICO VS PRIVADO"),

    # FILTRO MUNICIPIO
    html.Label("Selecciona un municipio:"),
    dcc.Dropdown(
        id="dropdown-municipio",
        options=[{"label": m, "value": m} for m in municipios],
        value="Todos"
    ),

    html.Br(),

    # FILTRO AÑOS
    html.Label("Selecciona rango de años:"),
    dcc.RangeSlider(
        id="slider-anios",
        min=min_year,
        max=max_year,
        step=1,
        value=[min_year, max_year],
        marks={i: str(i) for i in range(min_year, max_year + 1)}
    ),

    html.Br(),

    # GRAFICA
    dcc.Graph(id="grafica-boxplot-brecha")

])


# =========================
# CALLBACK
# =========================
@dash.callback(
    Output("grafica-boxplot-brecha", "figure"),
    Input("dropdown-municipio", "value"),
    Input("slider-anios", "value")
)
def actualizar_grafica(municipio, rango_anios):

    fig = generar_boxplot_brecha(
        df,
        municipio=municipio,
        rango_anios=rango_anios
    )

    return fig