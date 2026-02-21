import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def _find_col(df, candidates):
    """Busca la primera columna que existe en df entre los candidatos."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def cohen_d(x, y):
    """Calcula d de Cohen para medir tamaño del efecto."""
    x = pd.Series(x).dropna()
    y = pd.Series(y).dropna()
    
    if len(x) < 2 or len(y) < 2:
        return np.nan
    
    sx = x.std(ddof=1)
    sy = y.std(ddof=1)
    nx = len(x)
    ny = len(y)
    
    pooled_std = np.sqrt(((nx - 1) * sx ** 2 + (ny - 1) * sy ** 2) / (nx + ny - 2))
    
    if pooled_std == 0:
        return np.nan
    
    return (x.mean() - y.mean()) / pooled_std


def safe_ttest(a, b):
    """Realiza t-test de Welch de forma segura."""
    a = pd.Series(a).dropna()
    b = pd.Series(b).dropna()
    
    if len(a) < 2 or len(b) < 2:
        return np.nan, np.nan
    
    try:
        t, p = stats.ttest_ind(a, b, equal_var=False)
        return float(t), float(p)
    except:
        return np.nan, np.nan


def analizar_brecha_rural_urbana(
    df,
    umbral_gdp_quantile=0.25,
    dept_candidates=['DEPARTAMENTO', 'departamento', 'DEPT', 'dept', 'Departamento'],
    area_candidates=['AREA', 'area', 'ZONA', 'zona', 'area_residencia', 'tipo_zona', 'Area', 'Zona'],
    rural_labels=['Rural', 'RURAL', 'rural', 'R'],
    urban_labels=['Urbana', 'URBANA', 'urbana', 'Urbano', 'URBANO', 'urbano', 'U'],
    gdp_candidates=['PIB', 'pib', 'PIB_percapita', 'pib_percapita', 'gdp', 'GDP', 'pib_per_capita'],
    score_candidates=['PUNTAJE_GLOBAL', 'puntaje_global', 'puntaje_total', 'puntaje', 'score', 'global_score', 'PUNTAJE', 'Puntaje']
):
    """
    Analiza la brecha de desempeño entre estudiantes de zonas rurales y urbanas.
    
    Parameters:
    -----------
    df : DataFrame
        Datos con información de estudiantes, área de residencia y puntajes
    umbral_gdp_quantile : float
        Quantil para identificar departamentos con bajo PIB (default 0.25)
    
    Returns:
    --------
    dict con:
        - resumen_global: estadísticas globales (Rural vs Urbana)
        - dept_results: resultados por departamento
        - resumen_bajos_pib: resultados para departamentos con PIB bajo
        - fig_global: gráfica boxplot global
        - fig_por_dept: gráfica por departamentos
        - conclusiones: interpretación de resultados
    """
    
    # Detectar columnas
    dept_col = _find_col(df, dept_candidates)
    area_col = _find_col(df, area_candidates)
    gdp_col = _find_col(df, gdp_candidates)
    score_col = _find_col(df, score_candidates)
    
    if score_col is None or area_col is None:
        raise ValueError(f"No se encontró columna de puntaje o área. Disponibles: {df.columns.tolist()}")
    
    # Preparar datos
    df = df.copy()
    df['__area_limpia__'] = df[area_col].astype(str).str.strip()
    df['__is_rural__'] = df['__area_limpia__'].isin(rural_labels)
    df['__is_urban__'] = df['__area_limpia__'].isin(urban_labels)
    
    # Filtrar solo rural y urbano
    mask_valido = (df['__is_rural__'] | df['__is_urban__']) & df[score_col].notna()
    df_ru = df[mask_valido].copy()
    
    if len(df_ru) == 0:
        raise ValueError("No hay datos válidos después de filtrar rural/urbano")
    
    # ============ ANÁLISIS GLOBAL ============
    rural_scores = df_ru[df_ru['__is_rural__']][score_col].dropna()
    urban_scores = df_ru[df_ru['__is_urban__']][score_col].dropna()
    
    t_glob, p_glob = safe_ttest(rural_scores, urban_scores)
    d_glob = cohen_d(rural_scores, urban_scores)
    
    resumen_global = {
        'mean_rural': float(rural_scores.mean()) if len(rural_scores) > 0 else np.nan,
        'std_rural': float(rural_scores.std()) if len(rural_scores) > 0 else np.nan,
        'mean_urban': float(urban_scores.mean()) if len(urban_scores) > 0 else np.nan,
        'std_urban': float(urban_scores.std()) if len(urban_scores) > 0 else np.nan,
        'diff_mean': float(rural_scores.mean() - urban_scores.mean()) if len(rural_scores) > 0 and len(urban_scores) > 0 else np.nan,
        't_stat': t_glob,
        'p_value': p_glob,
        'cohen_d': d_glob,
        'n_rural': int(len(rural_scores)),
        'n_urban': int(len(urban_scores)),
        'significancia_estadistica': p_glob < 0.05 if not np.isnan(p_glob) else False,
    }
    
    # ============ ANÁLISIS POR DEPARTAMENTO ============
    dept_results = None
    resumen_bajos_pib = None
    
    if dept_col:
        rows = []
        for dept, grupo in df_ru.groupby(dept_col):
            rural_dept = grupo[grupo['__is_rural__']][score_col].dropna()
            urban_dept = grupo[grupo['__is_urban__']][score_col].dropna()
            
            t_dept, p_dept = safe_ttest(rural_dept, urban_dept)
            d_dept = cohen_d(rural_dept, urban_dept)
            
            # PIB si existe
            gdp_val = np.nan
            if gdp_col:
                gdp_vals = df[df[dept_col] == dept][gdp_col].dropna()
                if len(gdp_vals) > 0:
                    gdp_val = float(gdp_vals.iloc[0])
            
            rows.append({
                'DEPARTAMENTO': dept,
                'mean_rural': float(rural_dept.mean()) if len(rural_dept) > 0 else np.nan,
                'std_rural': float(rural_dept.std()) if len(rural_dept) > 0 else np.nan,
                'mean_urban': float(urban_dept.mean()) if len(urban_dept) > 0 else np.nan,
                'std_urban': float(urban_dept.std()) if len(urban_dept) > 0 else np.nan,
                'diff_mean': float(rural_dept.mean() - urban_dept.mean()) if len(rural_dept) > 0 and len(urban_dept) > 0 else np.nan,
                't_stat': t_dept,
                'p_value': p_dept,
                'cohen_d': d_dept,
                'n_rural': int(len(rural_dept)),
                'n_urban': int(len(urban_dept)),
                'significancia': p_dept < 0.05 if not np.isnan(p_dept) else False,
                'PIB': gdp_val,
            })
        
        dept_results = pd.DataFrame(rows).sort_values('diff_mean', ascending=False, na_position='last')
        
        # ============ ANÁLISIS DEPARTAMENTOS CON BAJO PIB ============
        if gdp_col and 'PIB' in dept_results.columns:
            pib_valid = dept_results['PIB'].dropna()
            if len(pib_valid) > 0:
                threshold_pib = pib_valid.quantile(umbral_gdp_quantile)
                depts_bajo_pib = dept_results[dept_results['PIB'] <= threshold_pib]['DEPARTAMENTO'].tolist()
                
                mask_bajo_pib = df_ru[dept_col].isin(depts_bajo_pib)
                rural_bajo_pib = df_ru[mask_bajo_pib & df_ru['__is_rural__']][score_col].dropna()
                urban_bajo_pib = df_ru[mask_bajo_pib & df_ru['__is_urban__']][score_col].dropna()
                
                t_bajo, p_bajo = safe_ttest(rural_bajo_pib, urban_bajo_pib)
                d_bajo = cohen_d(rural_bajo_pib, urban_bajo_pib)
                
                resumen_bajos_pib = {
                    'departamentos': depts_bajo_pib,
                    'num_departamentos': len(depts_bajo_pib),
                    'threshold_pib': float(threshold_pib),
                    'mean_rural': float(rural_bajo_pib.mean()) if len(rural_bajo_pib) > 0 else np.nan,
                    'std_rural': float(rural_bajo_pib.std()) if len(rural_bajo_pib) > 0 else np.nan,
                    'mean_urban': float(urban_bajo_pib.mean()) if len(urban_bajo_pib) > 0 else np.nan,
                    'std_urban': float(urban_bajo_pib.std()) if len(urban_bajo_pib) > 0 else np.nan,
                    'diff_mean': float(rural_bajo_pib.mean() - urban_bajo_pib.mean()) if len(rural_bajo_pib) > 0 and len(urban_bajo_pib) > 0 else np.nan,
                    't_stat': t_bajo,
                    'p_value': p_bajo,
                    'cohen_d': d_bajo,
                    'n_rural': int(len(rural_bajo_pib)),
                    'n_urban': int(len(urban_bajo_pib)),
                    'significancia': p_bajo < 0.05 if not np.isnan(p_bajo) else False,
                }
    
    # ============ GRÁFICAS ============
    
    # Gráfica 1: Boxplot Global
    fig_global = px.box(
        df_ru,
        x='__area_limpia__',
        y=score_col,
        points='outliers',
        title='Distribución de Puntajes: Rural vs Urbana (Global)',
        labels={'__area_limpia__': 'Área de Residencia', score_col: 'Puntaje Global'},
        color='__area_limpia__',
        category_orders={'__area_limpia__': ['Rural', 'Urbana']},
    )
    fig_global.update_layout(showlegend=False, height=500)
    
    # Gráfica 2: Por Departamento (si existe dept_col)
    fig_por_dept = None
    if dept_col and len(dept_results) > 0:
        dept_results_sorted = dept_results.dropna(subset=['diff_mean']).sort_values('diff_mean')
        
        fig_por_dept = go.Figure()
        
        fig_por_dept.add_trace(go.Bar(
            y=dept_results_sorted['DEPARTAMENTO'],
            x=dept_results_sorted['mean_rural'],
            name='Rural',
            orientation='h',
            marker_color='lightblue'
        ))
        
        fig_por_dept.add_trace(go.Bar(
            y=dept_results_sorted['DEPARTAMENTO'],
            x=dept_results_sorted['mean_urban'],
            name='Urbana',
            orientation='h',
            marker_color='lightcoral'
        ))
        
        fig_por_dept.update_layout(
            barmode='group',
            title='Puntaje Promedio por Departamento: Rural vs Urbana',
            xaxis_title='Puntaje Promedio',
            yaxis_title='Departamento',
            height=max(400, len(dept_results) * 25),
            hovermode='closest'
        )
    
    # ============ CONCLUSIONES ============
    
    conclusiones = {
        'existe_brecha': resumen_global['p_value'] < 0.05 if not np.isnan(resumen_global['p_value']) else False,
        'magnitud_efecto': abs(resumen_global['cohen_d']) if not np.isnan(resumen_global['cohen_d']) else None,
        'interpretacion_efecto': _interpretar_cohen_d(resumen_global['cohen_d']) if not np.isnan(resumen_global['cohen_d']) else None,
        'requiere_intervencion': False,
        'recomendaciones': []
    }
    
    # Definir si requiere intervención
    if conclusiones['existe_brecha']:
        conclusiones['recomendaciones'].append(
            f"Se detecta diferencia significativa (p={resumen_global['p_value']:.4f}). "
            f"Rural: {resumen_global['mean_rural']:.2f} vs Urbana: {resumen_global['mean_urban']:.2f}"
        )
        
        if resumen_bajos_pib and resumen_bajos_pib['significancia']:
            conclusiones['requiere_intervencion'] = True
            conclusiones['recomendaciones'].append(
                f"En departamentos con PIB bajo, la brecha es aún MÁS significativa "
                f"(p={resumen_bajos_pib['p_value']:.4f}, diferencia={resumen_bajos_pib['diff_mean']:.2f}). "
                f"Se justifica intervención diferenciada."
            )
        else:
            conclusiones['recomendaciones'].append(
                "En departamentos con bajo PIB, la brecha no es estadísticamente significativa. "
                "Revise factores adicionales."
            )
    else:
        conclusiones['recomendaciones'].append(
            f"No hay diferencia significativa (p={resumen_global['p_value']:.4f}). "
            "No se justifica intervención basada solo en rural/urbano."
        )
    
    return {
        'resumen_global': resumen_global,
        'dept_results': dept_results,
        'resumen_bajos_pib': resumen_bajos_pib,
        'fig_global': fig_global,
        'fig_por_dept': fig_por_dept,
        'conclusiones': conclusiones
    }


def _interpretar_cohen_d(d):
    """Interpreta el tamaño del efecto según Cohen."""
    d_abs = abs(d)
    if d_abs < 0.2:
        return "Negligible"
    elif d_abs < 0.5:
        return "Pequeño"
    elif d_abs < 0.8:
        return "Mediano"
    else:
        return "Grande"


def generar_reporte_p1(resultados):
    """Genera un reporte textual de los resultados."""
    texto = []
    texto.append("=" * 80)
    texto.append("ANÁLISIS: BRECHA RURAL-URBANA EN DESEMPEÑO ICFES")
    texto.append("=" * 80)
    
    rg = resultados['resumen_global']
    texto.append("\nRESULTADOS GLOBALES")
    texto.append("-" * 80)
    texto.append(f"  Rural:  Media = {rg['mean_rural']:.2f}, Desv. Est. = {rg['std_rural']:.2f}, n = {rg['n_rural']}")
    texto.append(f"  Urbana: Media = {rg['mean_urban']:.2f}, Desv. Est. = {rg['std_urban']:.2f}, n = {rg['n_urban']}")
    texto.append(f"  Diferencia de Medias: {rg['diff_mean']:.2f}")
    texto.append(f"  t-statistic: {rg['t_stat']:.4f}")
    texto.append(f"  p-value: {rg['p_value']:.6f}")
    texto.append(f"  d de Cohen: {rg['cohen_d']:.4f} ({_interpretar_cohen_d(rg['cohen_d'])})")
    texto.append(f"  ¿Significancia estadística (p<0.05)? {'✓ SÍ' if rg['significancia_estadistica'] else '✗ NO'}")
    
    if resultados['resumen_bajos_pib']:
        rb = resultados['resumen_bajos_pib']
        texto.append("\n📍 RESULTADOS EN DEPARTAMENTOS CON BAJO PIB")
        texto.append("-" * 80)
        texto.append(f"  Número de departamentos: {rb['num_departamentos']}")
        texto.append(f"  Departamentos: {', '.join(rb['departamentos'][:5])}{'...' if len(rb['departamentos']) > 5 else ''}")
        texto.append(f"  Rural:  Media = {rb['mean_rural']:.2f}, Desv. Est. = {rb['std_rural']:.2f}, n = {rb['n_rural']}")
        texto.append(f"  Urbana: Media = {rb['mean_urban']:.2f}, Desv. Est. = {rb['std_urban']:.2f}, n = {rb['n_urban']}")
        texto.append(f"  Diferencia de Medias: {rb['diff_mean']:.2f}")
        texto.append(f"  p-value: {rb['p_value']:.6f}")
        texto.append(f"  d de Cohen: {rb['cohen_d']:.4f} ({_interpretar_cohen_d(rb['cohen_d'])})")
        texto.append(f"  ¿Significancia? {'✓ SÍ' if rb['significancia'] else '✗ NO'}")
    
    texto.append("\n🎯 CONCLUSIONES")
    texto.append("-" * 80)
    for rec in resultados['conclusiones']['recomendaciones']:
        texto.append(f"  • {rec}")
    
    if resultados['conclusiones']['requiere_intervencion']:
        texto.append("\n Intervención diferenciada JUSTIFICADA")
    else:
        texto.append("\n✓ Intervención diferenciada NO JUSTIFICADA basada en este análisis")
    
    texto.append("\n" + "=" * 80)
    
    return "\n".join(texto)