import dash
from dash import html, dcc, Input, Output
from Analysis.logica_p2 import obtener_datos, generar_grafica, generar_boxplot

dash.register_page(__name__, path="/pregunta_2")

# Cargar datos una vez
df = obtener_datos()

# Lista de municipios
municipios = sorted(df["cole_mcpio_ubicacion"].dropna().unique())

layout = html.Div([

    html.H1("Pregunta 2: Público vs Privado"),

    html.Label("Selecciona un municipio:"),

    dcc.Dropdown(
        id="dropdown-municipio",
        options=[{"label": "Todos", "value": "Todos"}] +
                [{"label": m, "value": m} for m in municipios],
        value="Todos"
    ),

    html.H3("Comparación de desempeño promedio"),

    dcc.Graph(id="grafica-municipio"),

    html.H3("Distribución de puntajes (Boxplot)"),

    dcc.Graph(id="grafica-boxplot")
])


@dash.callback(
    Output("grafica-municipio", "figure"),
    Output("grafica-boxplot", "figure"),
    Input("dropdown-municipio", "value")
)
def actualizar_graficas(municipio):
    fig1 = generar_grafica(df, municipio)
    fig2 = generar_boxplot(df, municipio)
    return fig1, fig2