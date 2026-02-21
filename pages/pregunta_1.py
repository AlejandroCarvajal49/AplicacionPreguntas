import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from Analysis.logica_p1 import analizar_brecha_rural_urbana, generar_reporte_p1

# Registrar página
dash.register_page(__name__, path='/pregunta1', name="Pregunta 1")

# Variable global para almacenar datos y resultados
datos_cargados = None
resultados_analisis = None

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("¿Existe brecha en desempeño Rural vs Urbana?", className="text-center my-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data-p1',
                children=dbc.Button("Cargar CSV", color="primary", className="w-100"),
                multiple=False,
            )
        ], md=6),
        dbc.Col([
            dbc.Button("🔍 Ejecutar Análisis", id='btn-analisis-p1', color="success", className="w-100")
        ], md=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.Div(id='output-analisis-p1')
        ])
    ]),
    
    dcc.Store(id='store-datos-p1'),
    dcc.Store(id='store-resultados-p1')
], fluid=True)


@callback(
    Output('store-datos-p1', 'data'),
    Input('upload-data-p1', 'contents'),
    prevent_initial_call=True
)
def cargar_datos(contents):
    if contents is None:
        return None
    
    import base64
    import io
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    return df.to_json(date_format='iso', orient='split')


@callback(
    [Output('store-resultados-p1', 'data'),
     Output('output-analisis-p1', 'children')],
    Input('btn-analisis-p1', 'n_clicks'),
    Input('store-datos-p1', 'data'),
    prevent_initial_call=True
)
def ejecutar_analisis(n_clicks, datos_json):
    if not datos_json or not n_clicks:
        return None, html.Div("Cargue datos primero", className="alert alert-warning")
    
    
    df = pd.read_json(datos_json, orient='split')
    resultados = analizar_brecha_rural_urbana(df)
    reporte = generar_reporte_p1(resultados)
        
    # Retornar datos para store y visualización
    salida = dbc.Container([
           dbc.Row([
                dbc.Col([
                    dcc.Graph(figure=resultados['fig_global'])
                ], md=6),
                dbc.Col([
                    dcc.Graph(figure=resultados['fig_por_dept']) if resultados['fig_por_dept'] else html.Div()
                ], md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.Pre(reporte, className="bg-light p-3 rounded", style={"fontSize": "12px"})
                ])
            ]),
        ])
        
    return resultados, salida
