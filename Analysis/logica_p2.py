import pandas as pd
import plotly.express as px


def analizar_publico_vs_privado():
    
    # 1. Cargar datos
    df = pd.read_csv("Data/saber11_Antioquia_clean.csv")
    
    # 2. Limpiar variable clave
    df["cole_naturaleza"] = df["cole_naturaleza"].str.lower()
    
    df = df[df["cole_naturaleza"].isin(["oficial", "no oficial"])]
    
    df["cole_naturaleza"] = df["cole_naturaleza"].replace({
        "oficial": "Oficial",
        "no oficial": "Privado"
    })
    
    # 3. Agrupar (solo matemáticas por ahora)
    resumen = df.groupby("cole_naturaleza")["punt_matematicas"].mean().reset_index()
    
    # 4. Gráfico
    fig = px.bar(
        resumen,
        x="cole_naturaleza",
        y="punt_matematicas",
        title="Promedio Matemáticas: Público vs Privado"
    )
    
    return {
        "fig": fig
    }