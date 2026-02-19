import pandas as pd
import plotly.express as px
import statsmodels.api as sm

def cargar_datos_p3():
    df = pd.read_csv('Data\saber11_Antioquia_clean.csv', dtype={'cole_cod_mcpio_ubicacion': str})
    df['cole_mcpio_ubicacion'] = df['cole_mcpio_ubicacion'].str.upper().str.strip()
    
    df['Acceso_TIC'] = df.apply(
        lambda x: 'Internet y Computador' if x['fami_tieneinternet'] == 'Si' and x['fami_tienecomputador'] == 'Si'
        else ('Solo Internet' if x['fami_tieneinternet'] == 'Si'
              else ('Solo Computador' if x['fami_tienecomputador'] == 'Si' else 'Sin Acceso TIC')),
        axis=1
    )
    return df

def obtener_lista_municipios(df):
    municipios = df['cole_mcpio_ubicacion'].dropna().unique().tolist()
    municipios.sort()
    return ['TODOS'] + municipios

def generar_mapa_antioquia(df, municipio):
    dff = df.copy()
    
    # Formateo estricto para cruce topológico GeoJSON
    dff['cole_cod_mcpio_ubicacion'] = dff['cole_cod_mcpio_ubicacion'].astype(str).str.replace('.0', '', regex=False).str.zfill(5)
    
    if municipio != 'TODOS':
        dff = dff[dff['cole_mcpio_ubicacion'] == municipio]

    df_mapa = dff.groupby(['cole_cod_mcpio_ubicacion', 'cole_mcpio_ubicacion'])['punt_ingles'].mean().reset_index()
    url_geojson = "https://raw.githubusercontent.com/mcd-unab/DANE-geo/master/json/MPIO.json"
    
    fig = px.choropleth(
        df_mapa,
        geojson=url_geojson,
        locations='cole_cod_mcpio_ubicacion',
        featureidkey='properties.MPIO_CCNCT',
        color='punt_ingles',
        hover_name='cole_mcpio_ubicacion',
        color_continuous_scale='Viridis',
        title=f'Promedio de Puntaje en Inglés ({municipio})'
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig

def generar_histograma_tic(df, municipio):
    dff = df.copy()
    if municipio != 'TODOS':
        dff = dff[dff['cole_mcpio_ubicacion'] == municipio]

    fig = px.histogram(
        dff,
        x='desemp_ingles',
        color='Acceso_TIC',
        barmode='group',
        category_orders={"desemp_ingles": ["A-", "A1", "A2", "B1", "B+"]},
        title=f'Distribución del Nivel de Inglés vs. Acceso TIC ({municipio})',
        labels={'desemp_ingles': 'Nivel de Inglés', 'count': 'Frecuencia'},
        color_discrete_map={
            'Internet y Computador': '#2ca02c',
            'Solo Internet': '#1f77b4',
            'Solo Computador': '#ff7f0e',
            'Sin Acceso TIC': '#d62728'
        }
    )
    return fig

def generar_dispersion_regresion(df, municipio):
    dff = df.copy()
    if municipio != 'TODOS':
        dff = dff[dff['cole_mcpio_ubicacion'] == municipio]

    fig = px.scatter(
        dff,
        x='punt_ingles',
        y='punt_global',
        color='Acceso_TIC',
        trendline='ols',
        opacity=0.5,
        title=f'Regresión: Puntaje de Inglés vs Puntaje Global ICFES ({municipio})',
        labels={'punt_ingles': 'Puntaje Inglés', 'punt_global': 'Puntaje Global'}
    )
    return fig