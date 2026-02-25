import pandas as pd
import plotly.express as px


def obtener_datos():
    df = pd.read_csv("data/saber11_Antioquia_clean.csv")

    # Limpiar naturaleza
    df["cole_naturaleza"] = df["cole_naturaleza"].astype(str).str.lower()
    df = df[df["cole_naturaleza"].isin(["oficial", "no oficial"])]

    df["cole_naturaleza"] = df["cole_naturaleza"].replace({
        "oficial": "Público",
        "no oficial": "Privado"
    })

    return df


# 🎨 Colores consistentes (como tu gráfica 1)
COLORES = {
    "Público": "#1f77b4",   # azul
    "Privado": "#d62728"    # rojo
}


def _preparar_long(df):
    """Convierte a formato largo y renombra materias."""
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

    df_melt["materia"] = df_melt["materia"].replace({
        "punt_matematicas": "Matemáticas",
        "punt_lectura_critica": "Lectura Crítica",
        "punt_c_naturales": "Ciencias Naturales"
    })

    return df_melt


def generar_grafica(df, municipio=None):

    # Filtrar por municipio
    if municipio and municipio != "Todos":
        df = df[df["cole_mcpio_ubicacion"] == municipio]

    df_melt = _preparar_long(df)

    resumen = df_melt.groupby(
        ["cole_naturaleza", "materia"]
    )["puntaje"].mean().reset_index()

    fig = px.bar(
        resumen,
        x="materia",
        y="puntaje",
        color="cole_naturaleza",
        color_discrete_map=COLORES,
        barmode="group",
        title=f"Desempeño por área - {municipio if municipio else 'Todos'}",
        labels={
            "cole_naturaleza": "Tipo de colegio",
            "materia": "Área",
            "puntaje": "Puntaje promedio"
        }
    )

    return fig


def generar_boxplot(df, municipio=None):

    # Filtrar por municipio
    if municipio and municipio != "Todos":
        df = df[df["cole_mcpio_ubicacion"] == municipio]

    df_melt = _preparar_long(df)

    fig_box = px.box(
        df_melt,
        x="materia",
        y="puntaje",
        color="cole_naturaleza",
        color_discrete_map=COLORES,
        title=f"Distribución de puntajes - {municipio if municipio else 'Todos'}",
        labels={
            "cole_naturaleza": "Tipo de colegio",
            "materia": "Área",
            "puntaje": "Puntaje"
        }
    )

    return fig_box

def generar_brecha(df, municipio=None):

    # Filtrar por municipio
    if municipio and municipio != "Todos":
        df = df[df["cole_mcpio_ubicacion"] == municipio]

    # Formato largo
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

    # Renombrar materias
    df_melt["materia"] = df_melt["materia"].replace({
        "punt_matematicas": "Matemáticas",
        "punt_lectura_critica": "Lectura Crítica",
        "punt_c_naturales": "Ciencias Naturales"
    })

    # Promedios
    resumen = df_melt.groupby(
        ["cole_naturaleza", "materia"]
    )["puntaje"].mean().reset_index()

    # Convertir a formato ancho
    pivot = resumen.pivot(
        index="materia",
        columns="cole_naturaleza",
        values="puntaje"
    ).reset_index()

    # Calcular brecha
    pivot["Brecha (Privado - Público)"] = pivot["Privado"] - pivot["Público"]

    # Gráfico
    fig_gap = px.bar(
        pivot,
        x="materia",
        y="Brecha (Privado - Público)",
        title=f"Brecha de desempeño - {municipio if municipio else 'Todos'}",
        labels={
            "materia": "Área",
            "Brecha (Privado - Público)": "Diferencia de puntaje"
        }
    )

    return fig_gap