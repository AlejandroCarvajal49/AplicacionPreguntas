import dash
from dash import html, dcc
from Analysis.logica_p2 import analizar_publico_vs_privado

dash.register_page(__name__, path="/pregunta_2")

# Llamar backend
resultados = analizar_publico_vs_privado()

layout = html.Div([
    
    html.H1("Pregunta 2: Público vs Privado"),
    
    html.H3("Comparación general por área"),
    
    dcc.Graph(
        figure=resultados["fig"]
    ),
    
    html.H3("Comparación controlando por estrato"),
    
    dcc.Graph(
        figure=resultados["fig_estrato"]
    )
    
])