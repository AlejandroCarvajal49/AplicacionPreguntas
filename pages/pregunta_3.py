import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import statsmodels.api as sm
from Analysis.logica_p3 import (
    cargar_datos_p3, 
    generar_mapa_antioquia, 
    generar_histograma_tic, 
    generar_dispersion_regresion, 
    obtener_lista_municipios
)

dash.register_page(__name__, path='/pregunta_3', name="Competitividad / Bilingüismo")

df_p3 = cargar_datos_p3()
lista_municipios = obtener_lista_municipios(df_p3)

layout = dbc.Container([
    html.H2("Competitividad y Bilingüismo: Impacto TIC", className="my-4"),
    html.Hr(),
    
    dbc.Row([
        dbc.Col([
            html.Label("Filtrar Análisis por Municipio:", className="fw-bold"),
            dcc.Dropdown(
                id='filtro-municipio',
                options=[{'label': m, 'value': m} for m in lista_municipios],
                value='TODOS',
                clearable=False,
                className="mb-3 shadow-sm"
            )
        ], md=4)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([dcc.Graph(id='grafica-mapa')])
            ], className="mb-4 shadow-sm")
        ], md=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([dcc.Graph(id='grafica-histograma')])
            ], className="mb-4 shadow-sm")
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([dcc.Graph(id='grafica-dispersion')])
            ], className="mb-4 shadow-sm")
        ], md=6)
    ])
], fluid=True)

@callback(
    [Output('grafica-mapa', 'figure'),
     Output('grafica-histograma', 'figure'),
     Output('grafica-dispersion', 'figure')],
    [Input('filtro-municipio', 'value')]
)
def actualizar_tablero(municipio_seleccionado):
    mapa = generar_mapa_antioquia(df_p3, municipio_seleccionado)
    histograma = generar_histograma_tic(df_p3, municipio_seleccionado)
    dispersion = generar_dispersion_regresion(df_p3, municipio_seleccionado)
    return mapa, histograma, dispersion