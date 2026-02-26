import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

from Analysis.logica_p2 import (
    cargar_datos, filtrar_datos, calcular_brechas,
    generar_boxplots_materias, generar_mapa_brecha,
    formato_periodo, MATERIAS
)

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
# HELPER: Tarjeta de brecha
# =========================
def crear_tarjeta_brecha(nombre_materia):
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.H5(nombre_materia, className="text-center mb-2",
                         style={"fontWeight": "bold"}),
                html.Div(id=f"brecha-{nombre_materia}", children=[
                    html.P("Cargando...", className="text-center text-muted")
                ])
            ])
        ], className="shadow-sm", style={"borderRadius": "12px"}),
        width=4
    )


# =========================
# LAYOUT
# =========================
layout = html.Div([

    html.H1("Pregunta 2: Calidad Educativa Público vs Privado",
            className="text-center my-4"),

    # ---------- FILTRO MUNICIPIO ----------
    dbc.Row([
        dbc.Col([
            html.Label("Selecciona Municipio:", className="fw-bold"),
            dcc.Dropdown(
                id="filtro-municipio",
                options=[{"label": m, "value": m} for m in municipios],
                value="Todos",
                clearable=False
            ),
        ], width=6)
    ], justify="center", className="mb-4"),

    # ---------- FILTRO PERIODO COMO TIMELINE ----------
    dbc.Row([
        dbc.Col([
            html.Label("Línea de Tiempo - Periodos:", className="fw-bold"),
            html.Div([
                dcc.RangeSlider(
                    id="filtro-periodo-timeline",
                    min=0,
                    max=len(periodos) - 1,
                    step=1,
                    marks={i: {"label": formato_periodo(p),
                               "style": {"fontSize": "12px", "transform": "rotate(-45deg)"}}
                           for i, p in enumerate(periodos)},
                    value=[0, len(periodos) - 1],
                    tooltip={"placement": "top", "always_visible": False},
                    allowCross=False,
                    className="mt-2"
                )
            ], style={"padding": "10px 20px 30px 20px"})
        ], width=10)
    ], justify="center", className="mb-4"),

    # ---------- TARJETAS DE BRECHA ----------
    html.H4("Brecha Privado − Público por Materia", className="text-center mt-2 mb-3"),
    dbc.Row(
        [crear_tarjeta_brecha(nombre) for nombre in MATERIAS.keys()],
        justify="center",
        className="mb-4"
    ),

    # ---------- GRÁFICA BOXPLOT ----------
    html.H4("📦 Distribución por Materia", className="text-center mt-3 mb-2"),
    dcc.Graph(id="grafica-boxplot-brecha"),

    html.Hr(),

    # ---------- MAPA GEOGRÁFICO DE BRECHA ----------
    html.H4("🗺️ Mapa de Brecha por Municipio",
            className="text-center mt-3 mb-2"),
    html.P("Azul = Público supera a Privado | Rojo = Privado supera a Público",
           className="text-center text-muted", style={"fontSize": "13px"}),

    dbc.Row([
        dbc.Col([
            html.Label("Selecciona Materia:", className="fw-bold"),
            dcc.Dropdown(
                id="filtro-materia-mapa",
                options=[{"label": nombre, "value": col}
                         for nombre, col in MATERIAS.items()],
                value="punt_matematicas",
                clearable=False
            ),
        ], width=4)
    ], justify="center", className="mb-3"),

    dcc.Graph(id="grafica-mapa-brecha"),

    html.Br(),

])

# =========================
# CALLBACK BOXPLOT + BRECHAS
# =========================
@dash.callback(
    Output("grafica-boxplot-brecha", "figure"),
    *[Output(f"brecha-{nombre}", "children") for nombre in MATERIAS.keys()],
    Input("filtro-municipio", "value"),
    Input("filtro-periodo-timeline", "value")
)
def actualizar_boxplot(municipio, rango_periodo):

    idx_min, idx_max = rango_periodo
    periodos_seleccionados = periodos[idx_min:idx_max + 1]

    df_filtrado = filtrar_datos(df, municipio=municipio, periodo=periodos_seleccionados)

    fig_boxplot = generar_boxplots_materias(df_filtrado)

    brechas = calcular_brechas(df_filtrado)

    tarjetas = []
    for nombre in MATERIAS.keys():
        info = brechas.get(nombre, {})
        brecha_val = info.get("brecha")
        media_pub = info.get("media_publico")
        media_priv = info.get("media_privado")

        if brecha_val is not None:
            if brecha_val > 0:
                color_brecha = "#d62728"
                icono = "▲"
            elif brecha_val < 0:
                color_brecha = "#2ca02c"
                icono = "▼"
            else:
                color_brecha = "#888"
                icono = "="

            contenido = html.Div([
                html.H3(f"{icono} {brecha_val:+.1f} pts",
                         className="text-center mb-1",
                         style={"color": color_brecha, "fontWeight": "bold"}),
                html.P(
                    [
                        html.Span(f"Público: {media_pub}", style={"color": "#1f77b4"}),
                        html.Span(" | "),
                        html.Span(f"Privado: {media_priv}", style={"color": "#d62728"}),
                    ],
                    className="text-center",
                    style={"fontSize": "13px", "marginBottom": "0"}
                ),
            ])
        else:
            contenido = html.P("Sin datos", className="text-center text-muted")

        tarjetas.append(contenido)

    return fig_boxplot, *tarjetas


# =========================
# CALLBACK MAPA (filtros globales + materia)
# =========================
@dash.callback(
    Output("grafica-mapa-brecha", "figure"),
    Input("filtro-municipio", "value"),
    Input("filtro-periodo-timeline", "value"),
    Input("filtro-materia-mapa", "value")
)
def actualizar_mapa(municipio, rango_periodo, columna_materia):

    idx_min, idx_max = rango_periodo
    periodos_seleccionados = periodos[idx_min:idx_max + 1]

    df_filtrado = filtrar_datos(df, municipio="Todos", periodo=periodos_seleccionados)

    fig_mapa = generar_mapa_brecha(df_filtrado, columna_materia, municipio_seleccionado=municipio)

    return fig_mapa