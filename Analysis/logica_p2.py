import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================
# CARGAR DATOS
# =========================
def cargar_datos(path="data/icfes_antioquia.csv"):
    df = pd.read_csv(path)
    return df


# =========================
# LIMPIAR VARIABLES CLAVE
# =========================
def preparar_datos(df):
    df = df.copy()

    # Normalizar nombres de colegio
    df["tipo_colegio"] = df["cole_naturaleza"].replace({
        "OFICIAL": "Público",
        "Oficial": "Público",
        "oficial": "Público",
        "PRIVADO": "Privado",
        "Privado": "Privado",
        "privado": "Privado"
    })

    return df


# =========================
# GRAFICA PRINCIPAL (BOXPLOT + BRECHA)
# =========================
def generar_boxplot_brecha(df, municipio=None, rango_anios=None):
    
    df = preparar_datos(df)

    # FILTRO MUNICIPIO
    if municipio and municipio != "Todos":
        df = df[df["cole_municipio"] == municipio]

    # FILTRO AÑOS (si existe columna)
    if rango_anios and "periodo" in df.columns:
        df = df[df["periodo"].between(rango_anios[0], rango_anios[1])]

    materias = {
        "punt_matematicas": "Matemáticas",
        "punt_lectura_critica": "Lectura Crítica",
        "punt_c_naturales": "Ciencias Naturales"
    }

    df_long = df.melt(
        id_vars=["tipo_colegio"],
        value_vars=list(materias.keys()),
        var_name="materia",
        value_name="puntaje"
    )

    df_long["materia"] = df_long["materia"].map(materias)

    # =========================
    # BOXPLOT
    # =========================
    fig = px.box(
        df_long,
        x="materia",
        y="puntaje",
        color="tipo_colegio",
        color_discrete_map={
            "Público": "blue",
            "Privado": "red"
        },
        points="outliers",
        title="Distribución + Brecha (Privado vs Público)"
    )

    # =========================
    # CALCULO DE BRECHA
    # =========================
    pivot = df_long.groupby(["materia", "tipo_colegio"])["puntaje"].mean().unstack()

    # 👉 MANEJO SEGURO (CLAVE DEL ERROR)
    pivot["Público"] = pivot.get("Público", 0)
    pivot["Privado"] = pivot.get("Privado", 0)

    pivot["brecha"] = pivot["Privado"] - pivot["Público"]

    # Si no hay datos suficientes
    if pivot["brecha"].isna().all():
        return px.box(title="No hay datos suficientes para comparar")

    # =========================
    # ANOTAR BRECHA EN GRAFICA
    # =========================
    for i, materia in enumerate(pivot.index):
        fig.add_annotation(
            x=materia,
            y=max(df_long["puntaje"]),
            text=f"Brecha: {pivot.loc[materia, 'brecha']:.2f}",
            showarrow=False,
            font=dict(size=12, color="black")
        )

    return fig