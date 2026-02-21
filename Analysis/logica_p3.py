import pandas as pd
import plotly.express as px
import statsmodels.api as sm
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import numpy as np

def cargar_datos_p3():
    df = pd.read_csv('Data/saber11_Antioquia_clean.csv', dtype={'cole_cod_mcpio_ubicacion': str})
    df['cole_mcpio_ubicacion'] = df['cole_mcpio_ubicacion'].str.upper().str.strip()
    
    # Ingeniería de características: Acceso TIC
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
    # Ahora generamos un barplot de ranking por municipio (no filtrado por selección)
    dff = df.copy()
    dff = dff.dropna(subset=['cole_cod_mcpio_ubicacion'])
    # Normalizar código municipal (eliminar caracteres no numéricos y rellenar a 5 dígitos)
    dff['MPIO_ID'] = dff['cole_cod_mcpio_ubicacion'].astype(str).str.replace(r'[^0-9]', '', regex=True).str.zfill(5)

    # Agrupar por municipio y calcular promedio de puntaje en inglés
    df_rank = dff.groupby(['MPIO_ID', 'cole_mcpio_ubicacion'], as_index=False)['punt_ingles'].mean()
    df_rank = df_rank.sort_values('punt_ingles', ascending=False)

    # Crear figura de barras horizontal (ranking)
    fig = px.bar(
        df_rank,
        x='punt_ingles',
        y='cole_mcpio_ubicacion',
        orientation='h',
        hover_data={'MPIO_ID': True, 'punt_ingles': ':.2f'},
        labels={'punt_ingles': 'Promedio Puntaje Inglés', 'cole_mcpio_ubicacion': 'Municipio'},
        title='Ranking de Municipios por Promedio de Puntaje en Inglés (Antioquia)'
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin={"r":0,"t":40,"l":0,"b":0}, height=900)
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