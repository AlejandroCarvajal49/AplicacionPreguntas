import dash
from dash import html, dcc
from Analysis.logica_p2 import analizar_publico_vs_privado

dash.register_page(__name__, path="/pregunta_2")

# Llamar al backend
resultados = analizar_publico_vs_privado()

layout = html.Div([
    
    html.H1("Pregunta 2: Público vs Privado"),
    
    dcc.Graph(
        figure=resultados["fig"]
    )
    
])