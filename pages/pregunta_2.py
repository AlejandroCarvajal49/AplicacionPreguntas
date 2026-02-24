import dash
from dash import html, dcc, Input, Output
from Analysis.logica_p2 import obtener_datos, generar_grafica

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
    
    dcc.Graph(id="grafica-municipio")
])


@dash.callback(
    Output("grafica-municipio", "figure"),
    Input("dropdown-municipio", "value")
)
def actualizar_grafica(municipio):
    return generar_grafica(df, municipio)