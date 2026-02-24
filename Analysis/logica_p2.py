import pandas as pd
import plotly.express as px


def analizar_publico_vs_privado():
    
    # 1. Cargar datos
    df = pd.read_csv("data/saber11_Antioquia_clean.csv")
    
    # 2. Limpiar variable cole_naturaleza
    df["cole_naturaleza"] = df["cole_naturaleza"].astype(str).str.lower()
    
    df = df[df["cole_naturaleza"].isin(["oficial", "no oficial"])]
    
    df["cole_naturaleza"] = df["cole_naturaleza"].replace({
        "oficial": "Oficial",
        "no oficial": "Privado"
    })
    
    # =========================
    # GRÁFICO 1: GENERAL
    # =========================
    
    df_melt = df.melt(
        id_vars=["cole_naturaleza"],
        value_vars=[
            "punt_matematicas",
            "punt_lectura_critica",
            "punt_c_naturales"
        ],
        var_name="materia",
        value_name="puntaje"
    )
    
    resumen = df_melt.groupby(
        ["cole_naturaleza", "materia"]
    )["puntaje"].mean().reset_index()
    
    fig = px.bar(
        resumen,
        x="materia",
        y="puntaje",
        color="cole_naturaleza",
        barmode="group",
        title="Comparación de desempeño por área: Público vs Privado"
    )
    
    # =========================
    # GRÁFICO 2: POR ESTRATO
    # =========================
    
    df = df[df["fami_estratovivienda"].notna()]
    
    df_melt_estrato = df.melt(
        id_vars=["cole_naturaleza", "fami_estratovivienda"],
        value_vars=[
            "punt_matematicas",
            "punt_lectura_critica",
            "punt_c_naturales"
        ],
        var_name="materia",
        value_name="puntaje"
    )
    
    resumen_estrato = df_melt_estrato.groupby(
        ["cole_naturaleza", "materia", "fami_estratovivienda"]
    )["puntaje"].mean().reset_index()
    
    fig_estrato = px.bar(
        resumen_estrato,
        x="materia",
        y="puntaje",
        color="cole_naturaleza",
        barmode="group",
        facet_col="fami_estratovivienda",
        title="Comparación por área controlando por estrato"
    )
    
    return {
        "fig": fig,
        "fig_estrato": fig_estrato
    }