import pandas as pd
import plotly.express as px
from scipy import stats
import numpy as np

def cargar_datos_p1():
    # 1. Cargar datos de Saber 11
    df = pd.read_csv('Data/saber11_Antioquia_clean.csv', dtype={'cole_cod_mcpio_ubicacion': str})
    df['cole_mcpio_ubicacion'] = df['cole_mcpio_ubicacion'].str.upper().str.strip()
    
    # Manejar el nombre de la columna de área de residencia (puede variar según el dataset de ICFES)
    col_area = 'estu_areareside' if 'estu_areareside' in df.columns else 'cole_area_ubicacion'
    
    # Limpieza: Filtrar 'Sin Información' y estandarizar a Urbano/Rural
    if col_area in df.columns:
        df = df[~df[col_area].astype(str).str.upper().isin(['SIN INFORMACIÓN', 'SIN INFORMACION', 'NAN'])]
        df['Area'] = df[col_area].apply(
            lambda x: 'Urbano' if 'CABECERA' in str(x).upper() or 'URBAN' in str(x).upper() else 'Rural'
        )
    else:
        df['Area'] = 'Desconocido'

    # Limpieza: Tratamiento de nulos en estrato socioeconómico
    col_estrato = 'fami_estratovivienda'
    if col_estrato in df.columns:
        df = df.dropna(subset=[col_estrato])
        df = df[~df[col_estrato].astype(str).str.upper().isin(['SIN INFORMACION', 'SIN INFORMACIÓN'])]

    # 2. Cargar y cruzar datos de PIB
    try:
        # 1. Usamos sep=';' o ',' (pandas puede auto-detectarlo con sep=None y engine='python')
        # 2. encoding='utf-8-sig' elimina los caracteres invisibles (BOM) de Excel
        df_pib = pd.read_csv('Data/PIB_municipios.csv', sep=None, engine='python', encoding='utf-8-sig')
        
        # 3. Limpiamos los nombres de TODAS las columnas por si tienen espacios accidentales
        df_pib.columns = df_pib.columns.str.strip()
        
        # 4. Ahora sí, estandarizamos los datos de la columna
        df_pib['Municipio'] = df_pib['Municipio'].str.upper().str.strip()
        
        # Cruzar los datos
        df = pd.merge(df, df_pib, left_on='cole_mcpio_ubicacion', right_on='Municipio', how='left')
        
    except KeyError as e:
        print(f"Error de columna en PIB_municipios.csv. Las columnas detectadas son: {df_pib.columns.tolist()}")
        df['PIB miles de millones'] = np.nan
    except FileNotFoundError:
        print("Advertencia: No se encontró 'PIB_municipios.csv'. Verifica la ruta.")
        df['PIB miles de millones'] = np.nan

    return df

def obtener_lista_municipios_p1(df):
    municipios = df['cole_mcpio_ubicacion'].dropna().unique().tolist()
    municipios.sort()
    return ['TODOS'] + municipios

def generar_boxplot_brecha(df, municipio):
    dff = df.copy()
    if municipio != 'TODOS':
        dff = dff[dff['cole_mcpio_ubicacion'] == municipio]

    fig = px.box(
        dff,
        x='Area',
        y='punt_global',
        color='Area',
        title=f'Distribución del Puntaje Global: Urbano vs Rural ({municipio})',
        labels={'punt_global': 'Puntaje Global', 'Area': 'Zona de Residencia'},
        color_discrete_map={'Urbano': '#1f77b4', 'Rural': '#2ca02c'}
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    return fig

def generar_dispersion_pib_brecha(df):
    # Agrupar para calcular la brecha promedio por municipio
    agrupado = df.groupby(['cole_mcpio_ubicacion', 'Area'])['punt_global'].mean().unstack()
    
    # Si falta alguna de las zonas en un municipio, no se puede calcular la brecha
    if 'Urbano' in agrupado.columns and 'Rural' in agrupado.columns:
        agrupado['Brecha_Puntos'] = agrupado['Urbano'] - agrupado['Rural']
    else:
        agrupado['Brecha_Puntos'] = np.nan
        
    agrupado = agrupado.reset_index()

    # Extraer el PIB correspondiente
    if 'PIB miles de millones' in df.columns:
        pib_df = df[['cole_mcpio_ubicacion', 'PIB miles de millones']].drop_duplicates()
        agrupado = pd.merge(agrupado, pib_df, on='cole_mcpio_ubicacion', how='left')

        fig = px.scatter(
            agrupado,
            x='PIB miles de millones',
            y='Brecha_Puntos',
            hover_name='cole_mcpio_ubicacion',
            trendline='ols',
            title='Correlación: Brecha Urbano-Rural vs PIB Municipal',
            labels={
                'Brecha_Puntos': 'Brecha (Puntos Urbano - Rural)', 
                'PIB miles de millones': 'PIB (Miles de Millones)'
            },
            opacity=0.7
        )
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        return fig
        
    return px.scatter(title="Datos de PIB no disponibles para graficar")

def calcular_estadisticas_brecha(df, municipio):
    dff = df.copy()
    if municipio != 'TODOS':
        dff = dff[dff['cole_mcpio_ubicacion'] == municipio]

    urbano = dff[dff['Area'] == 'Urbano']['punt_global'].dropna()
    rural = dff[dff['Area'] == 'Rural']['punt_global'].dropna()

    if len(urbano) < 2 or len(rural) < 2:
        return "Insight: No hay suficientes datos en ambas zonas para calcular la brecha estadística en este municipio."

    brecha = urbano.mean() - rural.mean()
    
    # T-test asumiendo varianzas distintas (Welch's t-test)
    t_stat, p_val = stats.ttest_ind(urbano, rural, equal_var=False)

    significancia = "SIGNIFICATIVA" if p_val < 0.05 else "NO significativa"

    return f"Insight: Se evidencia una diferencia de {brecha:.1f} puntos promedio a favor de las zonas urbanas. La brecha es estadísticamente {significancia} (p-valor: {p_val:.4f})."