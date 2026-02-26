import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

from Analysis.logica_p2 import (
    cargar_datos, filtrar_datos, calcular_brechas,
    generar_boxplots_materias, generar_mapa_brecha,
    generar_brecha_por_estrato,
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
                html.H6(nombre_materia, className="text-center mb-2",
                         style={"fontWeight": "600", "fontSize": "13px", "color": "#444"}),
                html.Div(id=f"brecha-{nombre_materia}", children=[
                    html.P("Cargando...", className="text-center text-muted",
                           style={"fontSize": "12px"})
                ])
            ], style={"padding": "12px 8px"})
        ], className="shadow-sm", style={"borderRadius": "8px", "border": "1px solid #e0e0e0"}),
        width=4, className="mb-3"
    )


# =========================
# LAYOUT
# =========================
layout = html.Div([

    # ---------- TÍTULO ----------
    html.H2("Calidad Educativa: Colegios Públicos vs Privados",
            className="text-center mt-4 mb-1",
            style={"fontWeight": "bold", "color": "#222"}),
    html.P("Análisis de brechas en puntajes Saber 11 en Antioquia",
           className="text-center mb-4",
           style={"fontSize": "14px", "color": "#666"}),

    # ---------- FILTROS ----------
    dbc.Row([
        dbc.Col([
            html.Label("Municipio", className="fw-bold",
                       style={"fontSize": "13px"}),
            dcc.Dropdown(
                id="filtro-municipio",
                options=[{"label": m, "value": m} for m in municipios],
                value="Todos",
                clearable=False
            ),
        ], width=4),
        dbc.Col([
            html.Label("Periodo", className="fw-bold",
                       style={"fontSize": "13px"}),
            html.Div([
                dcc.RangeSlider(
                    id="filtro-periodo-timeline",
                    min=0,
                    max=len(periodos) - 1,
                    step=1,
                    marks={i: {"label": formato_periodo(p),
                               "style": {"fontSize": "11px", "transform": "rotate(-45deg)"}}
                           for i, p in enumerate(periodos)},
                    value=[0, len(periodos) - 1],
                    tooltip={"placement": "top", "always_visible": False},
                    allowCross=False,
                )
            ], style={"padding": "5px 10px 25px 10px"})
        ], width=7),
    ], justify="center", className="mb-4"),

    html.Hr(style={"borderColor": "#ddd"}),

    # ---------- TARJETAS DE BRECHA ----------
    html.H5("Brecha por materia (Privado - Público)",
            className="text-center mt-3 mb-3",
            style={"fontWeight": "600", "color": "#333"}),
    dbc.Row(
        [crear_tarjeta_brecha(nombre) for nombre in list(MATERIAS.keys())[:3]],
        justify="center",
    ),
    dbc.Row(
        [crear_tarjeta_brecha(nombre) for nombre in list(MATERIAS.keys())[3:]],
        justify="center",
        className="mb-3"
    ),

    html.Hr(style={"borderColor": "#ddd"}),

    # ---------- BOXPLOTS ----------
    dcc.Graph(id="grafica-boxplot-brecha"),

    html.Hr(style={"borderColor": "#ddd"}),

    # ---------- BRECHA POR ESTRATO ----------
    dbc.Row([
        dbc.Col([
            html.Label("Materia", className="fw-bold",
                       style={"fontSize": "13px"}),
            dcc.Dropdown(
                id="filtro-materia-estrato",
                options=[{"label": nombre, "value": col}
                         for nombre, col in MATERIAS.items()],
                value="punt_global",
                clearable=False
            ),
        ], width=3)
    ], justify="center", className="mb-3"),

    dcc.Graph(id="grafica-brecha-estrato"),

    html.Hr(style={"borderColor": "#ddd"}),

    # ---------- MAPA ----------
    dbc.Row([
        dbc.Col([
            html.Label("Materia", className="fw-bold",
                       style={"fontSize": "13px"}),
            dcc.Dropdown(
                id="filtro-materia-mapa",
                options=[{"label": nombre, "value": col}
                         for nombre, col in MATERIAS.items()],
                value="punt_global",
                clearable=False
            ),
        ], width=3)
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
def actualizar_principales(municipio, rango_periodo):

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
                color_brecha = "#c0392b"
                signo = "+"
            elif brecha_val < 0:
                color_brecha = "#2166ac"
                signo = ""
            else:
                color_brecha = "#888"
                signo = ""

            contenido = html.Div([
                html.H4(f"{signo}{brecha_val:.1f} pts",
                         className="text-center mb-1",
                         style={"color": color_brecha, "fontWeight": "bold",
                                "fontSize": "18px", "marginBottom": "4px"}),
                html.P(
                    [
                        html.Span(f"Púb: {media_pub}",
                                  style={"color": "#1f77b4", "fontSize": "11px"}),
                        html.Span(" | ", style={"color": "#999", "fontSize": "11px"}),
                        html.Span(f"Priv: {media_priv}",
                                  style={"color": "#c0392b", "fontSize": "11px"}),
                    ],
                    className="text-center",
                    style={"marginBottom": "0"}
                ),
            ])
        else:
            contenido = html.P("Sin datos", className="text-center text-muted",
                               style={"fontSize": "12px"})

        tarjetas.append(contenido)

    return fig_boxplot, *tarjetas


# =========================
# CALLBACK BRECHA POR ESTRATO
# =========================
@dash.callback(
    Output("grafica-brecha-estrato", "figure"),
    Input("filtro-municipio", "value"),
    Input("filtro-periodo-timeline", "value"),
    Input("filtro-materia-estrato", "value")
)
def actualizar_estrato(municipio, rango_periodo, columna_materia):

    idx_min, idx_max = rango_periodo
    periodos_seleccionados = periodos[idx_min:idx_max + 1]

    df_filtrado = filtrar_datos(df, municipio=municipio, periodo=periodos_seleccionados)

    return generar_brecha_por_estrato(df_filtrado, columna_materia)


# =========================
# CALLBACK MAPA
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