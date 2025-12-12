import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import yfinance as yf
import os
from math import factorial
from metricas_funciones import *
from portafolios_markowitz import *

# Hacemo la descarga de los csv de los activos que tenemos
# Nombres de los archivos
FILES = ['ACWI.csv', 'SPY.csv', 'todos.csv']
filepath_1 = os.path.join('market', 'ACWI.csv')
filepath_2 = os.path.join('market', 'SPY.csv')
filepath_3 = os.path.join('market', 'todos.csv')
# Leemos los csv
df_spy = pd.DataFrame(pd.read_csv(filepath_2))
df_acwy= pd.DataFrame(pd.read_csv(filepath_1))
df_general= pd.DataFrame(pd.read_csv(filepath_3))
# convertimos la columna 'Date' en datos de fecha
df_spy['Date'] = pd.to_datetime(df_spy['Date'])
df_acwy['Date'] = pd.to_datetime(df_acwy['Date'])
df_general['Date'] = pd.to_datetime(df_general['Date'])
# Establece 'Date' como el índice para facilitar el filtrado por rango de fechas
df_spy = df_spy.set_index('Date')
df_acwy = df_acwy.set_index('Date')
df_general = df_general.set_index('Date')
###########################################################################
# Parámetros a cosiderar del código
# tickers <- contiene el nombre de los activos dados por el usuario
# fecha_inicio <- es la fecha de inicio input, para filtrar datos
# fecha_fin <- es la fecha de inicio input, para filtrar datos
#
# SOBRE LOS PARÁMETROS ANTERIORES SE HACE EL FILTRADO DEL DATAFRAME GENERAL
#
# tabla5["Pesos"]   <- Contiene los pesos del **PORTAFOLIO ARBITRARIO** donde el usuario escoge los pesos
#                    Ese sería el vector de pesos
#                    Los rangos: 0.0 - 1.0
# tasa_ib_r         <- Es la tasa libre de riesgo, considerese anual, las func. la reciben así
#                    Rango: 0.0 - 1.0
# nivel_conf        <- Nivel de confianza para el VaR y el CVaR, así lo reciben las funciones
#                    Rango: 0.9 - 0.99
# rend_objetivo     <- Rendimineto objetivo solo para el **PORTAFOLIO CON REND. OBJETIVO**
#                    Rango: 0.03 - 0.5
# 
# Más abajo defino los Dataframes filtrados con los tickers y fechas dados por el usuario, son:
# df_general_filt   <- Dataframe filtrado por [fecha_inicio:fecha_fin, tickers]
# df_spy_filt       <- Dataframe filtrado por [fecha_inicio:fecha_fin]
# df_acwy_filtered  <- Dataframe filtrado por [fecha_inicio:fecha_fin]
# 
# LOS MÁS IMORTANTES QUE VAN A USAR SON LOS DATAFRAMES DE JUSTO ARRIBA, LOS FILTRADOS
###########################################################################
# #############################################################################
# ##################################
# CERO PARTE, SELECCIONAR ACTIVOS, FECHAS, Y MOSTRAR CARÁTULA
# ##################################
# #############################################################################
# Sidebar
with st.sidebar:
    # Información del proyecto
    st.title("Proyecto - Seminario de Finanzas I")
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    *Integrantes:*
    - Flores Moreno Alan Alberto
    - Gonzales Carapia Ricardo 
    - Hernández Banda Oziel
    - Jimenez Borzani Daniela Naomi
    """)
    # Layouts
    st.header("Escoge los activos", divider="red")
    ## Selectbox
    selectbox_1 = st.selectbox(
        "Activos Regionales o por sectores",
        ["Regionales", "Sectores"],
        index=1
    )
    st.write(selectbox_1)
    if str(selectbox_1) == "Regionales":
        ## Multiselect
        st.subheader("Activos por Regiones")
        tickers = st.multiselect(
            label="Lista de activos",
            options=[
            'SPLG',  # 
            'EWC',  # 
            'IEUR',  # 
            'EEM',  # 
            'EWJ',  # 
            ],
            default=["SPLG"]
        )
    else:
        ## Multiselect
        st.subheader("Activos por Sectores")
        tickers = st.multiselect(
            label="Lista de activos",
            options=[
            'XLK',  # Tecnología
            'XLF',  # Finanzas
            'XLV',  # Salud
            'XLP',  # Consumo básico
            'XLY',  # Consumo discrecional
            'XLE',  # Energía
            'XLI',  # Industrial
            'XLC',  # Comunicaciones
            'XLB',  # Materiales
            'XLU',  # Servicios públicos
            'XLRE', # Bienes raíces"
            ],
            default=["XLK"]
        )
    st.markdown("---")
    # Layouts
    st.header("Escoge las fechas de inicio y fin para los datos", divider="red")
    ## Date input
    st.subheader("Fechas")
    # fecha_hoy = datetime.today()
    fecha_min = datetime(year=2020, month=1, day=1)
    fecha_max = datetime(year=2025, month=12, day=2)
    fecha_inicio = st.date_input(
        "Input Fecha de incio",
        datetime(year=2020, month=12, day=2),
        min_value=fecha_min,
        max_value=fecha_max
    )
    fecha_fin = st.date_input(
        "Input Fecha de fin",
        datetime(year=2025, month=12, day=2),
        min_value=fecha_min,
        max_value=fecha_max
    )
    fecha_inicio = datetime(year=fecha_inicio.year, month=fecha_inicio.month, day=fecha_inicio.day)
    fecha_fin = datetime(year=fecha_fin.year, month=fecha_fin.month, day=fecha_fin.day)
    # Layouts 
    st.header("Escoge la tasa libre de riesgo", divider="red")
    ## Input Numerico
    tasa_ib_r = st.number_input(
        "Tasa libre de Riesgo",
        min_value = 0.0,
        max_value = 1.0,
        value=0.2,
        step=0.01
    )
    st.header("Escoge el nivel de confianza para métricas de Riesgo", divider="red")
    ## Input Numerico
    nivel_conf = st.number_input(
        "Nivel de confianza",
        min_value = 0.9,
        max_value = 0.99,
        value=0.95,
        step=0.01
    )
    st.header("Escoge tu Benchmark", divider="red")
    selectbox_2 = st.selectbox(
        "Bechmark",
        ["S&P500", "ACWI","Regiones, como en instrucciones","Sectores, como en instrucciones"],
        index=1
    )
    st.markdown("---")
## HAGO EL FILTRADO POR FECHAS Y TICKERS DADOS EN INPUTS
df_general_filt = df_general.loc[fecha_inicio:fecha_fin, tickers]
df_spy_filt = df_spy.loc[fecha_inicio:fecha_fin]
df_acwy_filtered = df_acwy.loc[fecha_inicio:fecha_fin]
# Creo el BENCHMARK POR CASOS
if str(selectbox_2) == "S&P500":
    benchmark_returns = df_spy_filt.dropna()
elif str(selectbox_2) == "ACWI":
    benchmark_returns = df_acwy_filtered.dropna()
elif str(selectbox_2) == "Regiones, como en instrucciones":
    benchmark_returns = df_general.loc[fecha_inicio:fecha_fin,['SPLG','EWC','IEUR',
                                                               'EEM','EWJ']].dot([0.7062,0.0323,
                                                                                  0.1176,0.0902,0.0537])
    benchmark_returns = pd.DataFrame(benchmark_returns)
elif str(selectbox_2) == "Sectores, como en instrucciones":
    benchmark_returns = df_general.loc[fecha_inicio:fecha_fin,['XLC','XLY','XLP','XLE',
                                                               'XLF','XLV','XLI','XLB',
                                                               'XLRE','XLK','XLU']].dot([0.0999,0.1025,0.0482,0.0295,
                                                                                         0.1307,0.0958,0.0809,0.0166,
                                                                                         0.0187,0.3535,0.0237])
    benchmark_returns = pd.DataFrame(benchmark_returns)
# #############################################################################
# ##################################
# 1RA PARTE, SELECCIONAR EL TIPO DE PORTAFOLIO
# ##################################
# #############################################################################
# Layouts
st.header("Escoge el tipo de portafolio que gustes", divider="red")
## Multiselect
portafolio_tipo = st.selectbox(
    "Tipos de portafolios",
    [
    'Portafolio arbitrario',  # Caso más simple con inputs de pesos
    'Portafolio optimizado - Mínima Varianza',  # Markowitz Min Var
    'Portafolio optimizado - Máximo Sharpe',  # Markowitz Max Sharpe Ratio
    'Portafolio optimizado - Rendimiento Fijo',  # Markowitz con Rendimiento de input
    'Portafolio optimizado - Black Litterman'
    ],
    index=1
)
# ###########################################################################
# ##################################
# 3ERA PARTE DIVIOSIÓN DE CASOS
# ##################################
# ###########################################################################
if str(portafolio_tipo) == 'Portafolio arbitrario':
    # ###########################################################################
    # PRIMER CASO
    # ###########################################################################
    ## Tabla editable
    st.subheader("Tabla de pesos, por favor elige los pesos")
    pesos = [0.1 for _ in tickers]
    df_port = df_port = pd.DataFrame({
        "Tickers": tickers,
        "Pesos": [0.1] * len(tickers)
        })
    tabla5 = st.data_editor(df_port, disabled=["Tickers"])
    if tabla5["Pesos"].sum()==1.0 and (tabla5["Pesos"].between(0,1).all()):
        st.write("La suma de los pesos suma 1, el 100%")
        ########
        ## EN ESTE NIVEL DE IDENTACIÓN SE COMIENZA A ESCRIBIR MÁS CÓDIGO
        ########
        #######
        #######
        # RICARDO
        #######
        ####### 
        # DEFINIR PESOS (ELEGIDOS)
        pesos_array = tabla5["Pesos"].values
        portfolio_assets_returns = df_general_filt.dropna()
        # Alineación de fechas
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        # Retornos del Portafolio (R_p = Matriz * Pesos)
        r_p = portfolio_assets_returns.dot(pesos_array)
        # 3. Calcular TODAS las Métricas
        try:
            # Básicas
            ret_anual = retorno_anual_portafolio(r_p.values)
            vol_anual = volatilidad_portafolio(portfolio_assets_returns, pesos_array)
            sharpe = sharpe_ratio(r_p.values, rf=tasa_ib_r)
            # Riesgo y Distribución
            max_dd = max_drawdown(r_p.values)
            var_val, _ = var_historico(r_p.values, alpha=nivel_conf)
            cvar_val, _ = cvar_historico(r_p.values, alpha=nivel_conf)
            # Métricas Avanzadas (Nuevas)
            sesgo = sesgo_portafolio(r_p.values)
            curtosis = curtosis_portafolio(r_p.values)
            sortino = sortino_ratio(r_p.values, rf=tasa_ib_r)
            # Comparativas (Treynor y Beta)
            treynor, beta = treynor_ratio(r_p.values, benchmark_returns, r_p.index, rf_rate=tasa_ib_r)
        except Exception as e:
            st.error(f"Error en métricas: {e}")
            ret_anual = vol_anual = sharpe = max_dd = var_val = cvar_val = treynor = beta = sesgo = curtosis = sortino = 0

        # 4. Visualización de Resultados
        st.markdown("###  Desempeño del Portafolio")
        # FILA 1: Rendimiento y Riesgo Básico
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rendimiento Anual", f"{ret_anual:.2%}")
        col2.metric("Volatilidad Anual", f"{vol_anual:.2%}")
        col3.metric("Sharpe Ratio", f"{sharpe:.3f}")
        col4.metric("Sortino Ratio", f"{sortino:.3f}") 
        # FILA 2: Riesgo de Cola
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("VaR Histórico", f"{var_val:.2%}")
        col2.metric("CVaR Histórico", f"{cvar_val:.2%}")
        col3.metric("Max Drawdown", f"{max_dd:.2%}")
        col4.metric("Beta (vs Benchmark)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sesgo", f"{sesgo:.3f}")       
        col2.metric("Curtosis", f"{curtosis:.3f}") 
        col3.metric("Treynor Ratio", f"{treynor:.3f}")
        st.subheader("Rendimiento Acumulado vs Benchmark")
        cum_ret_port = (1 + r_p).cumprod()
        cum_ret_bench = (1 + benchmark_returns.iloc[:, 0]).cumprod()
        st.line_chart(pd.DataFrame({"Portafolio": cum_ret_port, "Benchmark": cum_ret_bench}))
        #####
        #####
        # FIN 1RA PARTE RICARDO
        #####
        #####
    else:
        st.write("La suma de los pesos debe sumar 1.0 y cada pesos deben estar entre 0 y 1")
        if tabla5["Pesos"].sum()<1.0:
            st.write("Te falta {} para sumar 1".format(1-tabla5["Pesos"].sum()))
        else:
            st.write("Los pesos exceden la suma de 1")

elif str(portafolio_tipo) == 'Portafolio optimizado - Mínima Varianza':
    # ###########################################################################
    # SEGUNDO CASO
    # ###########################################################################
    #####
    #####
    # 2DA PARTE RICARDO
    #####
    #####
    # === INICIO PARTE DANIELA ===
    # En este bloque calculo los pesos óptimos usando la función portafolio_minima_varianza
    # (definida en portafolios_markowitz.py), asigno esos pesos a 'pesos_array' y
    # recalculo r_p con dichos pesos para que el bloque original de Ricardo use el r_p optimizado.
    # No se elimina código previo; únicamente se redefine pesos_array y r_p.
    try:
        portfolio_assets_returns = df_general_filt.dropna()
        # Alineación de fechas con benchmark (igual que estructura original)
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]

        # Llamada a la función de mínima varianza: devuelve (pesos_optimos, retorno, volatilidad)
        pesos_optimos, _, _ = portafolio_minima_varianza(portfolio_assets_returns)
        # Aseguramos que pesos sean numpy array
        pesos_array = np.array(pesos_optimos)
        # Recalculo r_p usando los pesos óptimos (r_p será usado por el bloque original de Ricardo)
        r_p = portfolio_assets_returns.dot(pesos_array)
    except Exception as e:
        # Si falla la optimización, dejar pesos homogéneos como fallback (NO se borra el flujo original)
        st.warning(f" Error calculando portafolio mínima varianza: {e}. Se usan pesos homogéneos como fallback.")
        n_activos = len(tickers)
        pesos_array = np.array([1/n_activos] * n_activos)
        portfolio_assets_returns = df_general_filt.dropna()
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        r_p = portfolio_assets_returns.dot(pesos_array)
    # === FIN PARTE DANIELA ===
    st.write(pd.DataFrame({'Tickers':pd.array(tickers),'Pesos del portafolio':pd.array(pesos_array)}))
    try:
            # Básicas
            ret_anual = retorno_anual_portafolio(r_p.values)
            vol_anual = volatilidad_portafolio(portfolio_assets_returns, pesos_array)
            sharpe = sharpe_ratio(r_p.values, rf=tasa_ib_r)
            # Riesgo y Distribución
            max_dd = max_drawdown(r_p.values)
            var_val, _ = var_historico(r_p.values, alpha=nivel_conf)
            cvar_val, _ = cvar_historico(r_p.values, alpha=nivel_conf)
            # Métricas Avanzadas (Nuevas)
            sesgo = sesgo_portafolio(r_p.values)
            curtosis = curtosis_portafolio(r_p.values)
            sortino = sortino_ratio(r_p.values, rf=tasa_ib_r)
            # Comparativas (Treynor y Beta)
            treynor, beta = treynor_ratio(r_p.values, benchmark_returns, r_p.index, rf_rate=tasa_ib_r)
    except Exception as e:
            st.error(f"Error en métricas: {e}")
            ret_anual = vol_anual = sharpe = max_dd = var_val = cvar_val = treynor = beta = sesgo = curtosis = sortino = 0
        # 4. Visualización de Resultados
    st.markdown("###  Desempeño del Portafolio")
        # FILA 1: Rendimiento y Riesgo Básico
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rendimiento Anual", f"{ret_anual:.2%}")
    col2.metric("Volatilidad Anual", f"{vol_anual:.2%}")
    col3.metric("Sharpe Ratio", f"{sharpe:.3f}")
    col4.metric("Sortino Ratio", f"{sortino:.3f}") 
        # FILA 2: Riesgo de Cola
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("VaR Histórico", f"{var_val:.2%}")
    col2.metric("CVaR Histórico", f"{cvar_val:.2%}")
    col3.metric("Max Drawdown", f"{max_dd:.2%}")
    col4.metric("Beta (vs Benchmark)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesgo", f"{sesgo:.3f}")       
    col2.metric("Curtosis", f"{curtosis:.3f}") 
    col3.metric("Treynor Ratio", f"{treynor:.3f}")
    st.subheader("Rendimiento Acumulado vs Benchmark")
    cum_ret_port = (1 + r_p).cumprod()
    cum_ret_bench = (1 + benchmark_returns.iloc[:, 0]).cumprod()
    st.line_chart(pd.DataFrame({"Portafolio": cum_ret_port, "Benchmark": cum_ret_bench}))   
    #####
    #####
    # FIN 2DA PARTE RICARDO
    #####
    #####
elif str(portafolio_tipo) == 'Portafolio optimizado - Máximo Sharpe':
    # ###########################################################################
    # TERCER CASO
    # ###########################################################################
    #####
    #####
    # 3RA PARTE RICARDO
    #####
    #####
    # === INICIO PARTE DANIELA ===
    # Este bloque calcula los pesos que maximizan el Sharpe usando la función
    # portafolio_maximo_sharpe(retornos, rf) y redefine 'pesos_array' y 'r_p'
    # para que las métricas posteriores las calcule Ricardo con los pesos óptimos.
    try:
        portfolio_assets_returns = df_general_filt.dropna()
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]

        # Llamada a la función de Maximos Sharpe: devuelve (pesos_optimos, retorno, volatilidad)
        pesos_optimos, _, _ = portafolio_maximo_sharpe(portfolio_assets_returns, rf=tasa_ib_r)
        pesos_array = np.array(pesos_optimos)
        r_p = portfolio_assets_returns.dot(pesos_array)
    except Exception as e:
        st.warning(f"Error calculando portafolio máximo Sharpe: {e}. Se usan pesos homogéneos como fallback.")
        n_activos = len(tickers)
        pesos_array = np.array([1/n_activos] * n_activos)
        portfolio_assets_returns = df_general_filt.dropna()
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        r_p = portfolio_assets_returns.dot(pesos_array)
    # === FIN PARTE DANIELA ===
    st.write(pd.DataFrame({'Tickers':pd.array(tickers),'Pesos del portafolio':pd.array(pesos_array)}))
    try:
            # Básicas
            ret_anual = retorno_anual_portafolio(r_p.values)
            vol_anual = volatilidad_portafolio(portfolio_assets_returns, pesos_array)
            sharpe = sharpe_ratio(r_p.values, rf=tasa_ib_r)
            # Riesgo y Distribución
            max_dd = max_drawdown(r_p.values)
            var_val, _ = var_historico(r_p.values, alpha=nivel_conf)
            cvar_val, _ = cvar_historico(r_p.values, alpha=nivel_conf)
            # Métricas Avanzadas (Nuevas)
            sesgo = sesgo_portafolio(r_p.values)
            curtosis = curtosis_portafolio(r_p.values)
            sortino = sortino_ratio(r_p.values, rf=tasa_ib_r)
            # Comparativas (Treynor y Beta)
            treynor, beta = treynor_ratio(r_p.values, benchmark_returns, r_p.index, rf_rate=tasa_ib_r)
    except Exception as e:
            st.error(f"Error en métricas: {e}")
            ret_anual = vol_anual = sharpe = max_dd = var_val = cvar_val = treynor = beta = sesgo = curtosis = sortino = 0
        # 4. Visualización de Resultados
    st.markdown("###  Desempeño del Portafolio")

        # FILA 1: Rendimiento y Riesgo Básico
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rendimiento Anual", f"{ret_anual:.2%}")
    col2.metric("Volatilidad Anual", f"{vol_anual:.2%}")
    col3.metric("Sharpe Ratio", f"{sharpe:.3f}")
    col4.metric("Sortino Ratio", f"{sortino:.3f}") 
        # FILA 2: Riesgo de Cola
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("VaR Histórico", f"{var_val:.2%}")
    col2.metric("CVaR Histórico", f"{cvar_val:.2%}")
    col3.metric("Max Drawdown", f"{max_dd:.2%}")
    col4.metric("Beta (vs Benchmark)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesgo", f"{sesgo:.3f}")       
    col2.metric("Curtosis", f"{curtosis:.3f}") 
    col3.metric("Treynor Ratio", f"{treynor:.3f}")
    st.subheader("Rendimiento Acumulado vs Benchmark")
    cum_ret_port = (1 + r_p).cumprod()
    cum_ret_bench = (1 + benchmark_returns.iloc[:, 0]).cumprod()
    st.line_chart(pd.DataFrame({"Portafolio": cum_ret_port, "Benchmark": cum_ret_bench}))
    #####
    #####
    # FIN 3RA PARTE RICARDO
    #####
    #####
elif str(portafolio_tipo) == 'Portafolio optimizado - Rendimiento Fijo':
    # ###########################################################################
    # CUARTO CASO
    # ###########################################################################
    st.header("Escoge el rendimiento objetivo para este portafolio", divider="red")
    ## Input Numerico
    rend_objetivo = st.number_input(
        "Rendimiento objeetivo",
        min_value = 0.03,
        max_value = 0.5,
        value=0.2,
        step=0.01
    )
    #####
    #####
    # 4TA PARTE RICARDO
    #####
    #####
    # === INICIO PARTE DANIELA ===
    # En este bloque uso min_varianza_dado_retorno para obtener los pesos del portafolio
    # que cumpla con el rendimiento objetivo y luego recalculo r_p para que Ricardo
    # calcule las métricas con dichos pesos.
    try:
        portfolio_assets_returns = df_general_filt.dropna()
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]

        # Llamada a la función que minimiza varianza para un retorno objetivo
        pesos_optimos, _, _ = min_varianza_dado_retorno(portfolio_assets_returns, target_return=rend_objetivo)
        pesos_array = np.array(pesos_optimos)
        r_p = portfolio_assets_returns.dot(pesos_array)
    except Exception as e:
        st.warning(f"Error calculando portafolio con rendimiento fijo: {e}. Se usan pesos homogéneos como fallback.")
        n_activos = len(tickers)
        pesos_array = np.array([1/n_activos] * n_activos)
        portfolio_assets_returns = df_general_filt.dropna()
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        r_p = portfolio_assets_returns.dot(pesos_array)
    # === FIN PARTE DANIELA ===
    st.write(pd.DataFrame({'Tickers':pd.array(tickers),'Pesos del portafolio':pd.array(pesos_array)}))
    try:
            # Básicas
            ret_anual = retorno_anual_portafolio(r_p.values)
            vol_anual = volatilidad_portafolio(portfolio_assets_returns, pesos_array)
            sharpe = sharpe_ratio(r_p.values, rf=tasa_ib_r)
            # Riesgo y Distribución
            max_dd = max_drawdown(r_p.values)
            var_val, _ = var_historico(r_p.values, alpha=nivel_conf)
            cvar_val, _ = cvar_historico(r_p.values, alpha=nivel_conf)
            # Métricas Avanzadas (Nuevas)
            sesgo = sesgo_portafolio(r_p.values)
            curtosis = curtosis_portafolio(r_p.values)
            sortino = sortino_ratio(r_p.values, rf=tasa_ib_r)
            # Comparativas (Treynor y Beta)
            treynor, beta = treynor_ratio(r_p.values, benchmark_returns, r_p.index, rf_rate=tasa_ib_r)
    except Exception as e:
            st.error(f"Error en métricas: {e}")
            ret_anual = vol_anual = sharpe = max_dd = var_val = cvar_val = treynor = beta = sesgo = curtosis = sortino = 0
        # 4. Visualización de Resultados
    st.markdown("###  Desempeño del Portafolio")
        # FILA 1: Rendimiento y Riesgo Básico
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rendimiento Anual", f"{ret_anual:.2%}")
    col2.metric("Volatilidad Anual", f"{vol_anual:.2%}")
    col3.metric("Sharpe Ratio", f"{sharpe:.3f}")
    col4.metric("Sortino Ratio", f"{sortino:.3f}") 
        # FILA 2: Riesgo de Cola
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("VaR Histórico", f"{var_val:.2%}")
    col2.metric("CVaR Histórico", f"{cvar_val:.2%}")
    col3.metric("Max Drawdown", f"{max_dd:.2%}")
    col4.metric("Beta (vs Benchmark)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesgo", f"{sesgo:.3f}")       
    col2.metric("Curtosis", f"{curtosis:.3f}") 
    col3.metric("Treynor Ratio", f"{treynor:.3f}")
    st.subheader("Rendimiento Acumulado vs Benchmark")
    cum_ret_port = (1 + r_p).cumprod()
    cum_ret_bench = (1 + benchmark_returns.iloc[:, 0]).cumprod()
    st.line_chart(pd.DataFrame({"Portafolio": cum_ret_port, "Benchmark": cum_ret_bench}))
    #####
    #####
    # FIN 4TA PARTE RICARDO
    #####
    #####
elif str(portafolio_tipo) == 'Portafolio optimizado - Black Litterman':
    # ###########################################################################
    # QUINTO CASO
    # ###########################################################################
    #####
    #####
    # 5TA PARTE RICARDO
    #####
    #####
    # ================================================================
    # PARÁMETROS DEL MODELO
    # ================================================================
    st.header("Parámetros del Modelo", divider="red")
    col1, col2 = st.columns(2)       
    with col1:
        st.subheader("Parámetro Tau (τ)")
        st.markdown("""
        Escala de incertidumbre en las expectativas de mercado.
        """)
        tau_ = st.number_input(
            "Ingresa el valor de Tau (τ):",
            min_value=0.01,
            max_value=0.05,
            value=0.025,
            step=0.001,
            format="%.3f"
        )
    with col2:
        st.subheader("Coeficiente de Aversión al Riesgo (λ)")
        st.markdown("""
        Mide la preferencia del inversor por el riesgo.
        """)
        lam_ = st.number_input(
            "Coeficiente de aversión al riesgo (λ):",
            min_value=10.0,
            max_value=20.0,
            value=15.0,
            step=0.1
        )
                
    st.header("Definir Views del Mercado",divider="red")
    st.markdown("""
    **Matriz P:** Define tus views sobre los activos.
    - **1:** Activo con retorno positivo
    - **-1:** Activo con retorno negativo  
    - **0:** Activo no considerado en la view
    **Vector Q:** Nivel de confianza en cada view (0 a 1)
    """) 
    # Número de views
    if len(tickers)<3:
        n_views = st.number_input(
            "Número de views que deseas definir:",
            min_value=1,
            max_value=1, #combinaciones de n en 2
            value=1,
            step=1
        )
    else:
        n_views = st.number_input(
            "Número de views que deseas definir:",
            min_value=1,
            max_value=int(factorial(len(tickers))/(factorial(len(tickers)-2)*2)) + len(tickers), #combinaciones de n en 2
            value=2,
            step=1
        )
    n_assets = len(tickers) 
    # Crear matriz P editable
    st.subheader("Matriz P (Views)")
    st.write(f"Dimensiones: {n_views} views × {n_assets} activos")
            
    # Crear DataFrame para la matriz P
    p_data = []
    for i in range(n_views):
        row = []
        for j in range(n_assets):
            # Inicializar con 0
            row.append(0)
        p_data.append(row)
            
    p_df = pd.DataFrame(
        p_data,
        columns=tickers,
        index=[f"View {i+1}" for i in range(n_views)]
    )
            
    # Editar matriz P con restricciones
    st.info("💡 Solo puedes ingresar valores: -1, 0, o 1")   
    # Crear columnas para edición
    cols = st.columns(min(6, n_assets + 1))     
    # Diccionario para almacenar valores
    p_values = {}     
    with cols[0]:
        st.write("**View**")
        for i in range(n_views):
            st.write(f"View {i+1}")      
    for j, asset in enumerate(tickers):
        if j < len(cols) - 1:
            with cols[j + 1]:
                st.write(f"**{asset}**")
                for i in range(n_views):
                    key = f"p_{i}_{j}"
                    value = st.selectbox(
                        "-",
                        options=[-1, 0, 1],
                        index=1,  # 0 es el valor por defecto
                        key=key,
                        label_visibility="collapsed"
                    )
                    p_values[key] = value      
    # Construir matriz P desde los valores
    P = np.zeros((n_views, n_assets))
    for i in range(n_views):
        for j in range(n_assets):
            key = f"p_{i}_{j}"
            P[i, j] = p_values.get(key, 0)
    ##########################        
    # Mostrar matriz P
    #########################
    st.subheader("Matriz P Definida",divider='red')
    p_display_df = pd.DataFrame(
        P,
        columns=tickers,
        index=[f"View {i+1}" for i in range(n_views)]
    )
    st.dataframe(p_display_df, width="stretch")  
    #########################       
    # Vector Q
    #########################
    st.subheader("Vector Q (Niveles de Confianza)",divider='red')
    st.write(f"Dimensiones: {n_views} views")
    # Primero, necesitamos definir la función describe_view
    def describe_view(view_row, asset_names):
        """Describe una view en texto legible"""
        positives = [asset_names[i] for i, val in enumerate(view_row) if val == 1]
        negatives = [asset_names[i] for i, val in enumerate(view_row) if val == -1]
        
        if positives and negatives:
            return f"{positives[0]} superará a {negatives[0]}"
        elif positives:
            return f"{positives[0]} tendrá rendimiento positivo"
        elif negatives:
            return f"{negatives[0]} tendrá rendimiento negativo"
        else:
            return "View no definida"
    q_data = []
    for i in range(n_views):
        col1, col2 = st.columns([3, 1])
        with col1:
            # Llamamos a la función describe_view con la fila correspondiente de P
            view_description = describe_view(P[i], tickers)
            st.write(f"**View {i+1}:** {view_description}")
        with col2:
            q_value = st.number_input(
                f"Confianza View {i+1}:",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                key=f"q_{i}"
            )
            q_data.append(q_value)
    Q = np.array(q_data)     
    # Mostrar vector Q
    q_display_df = pd.DataFrame(
        Q.reshape(-1, 1),
        columns=["Confianza"],
        index=[f"View {i+1}" for i in range(n_views)]
    )
    st.dataframe(q_display_df, width="stretch")
    #########################
    # Vector x_M 
    #########################
    st.subheader("Matriz w_M, pesos del benchmark para calcular π",divider='red')
    def create_benchmark_inputs(tickers):
        # """
        # Crea una interfaz para ingresar los pesos del benchmark
        # Parámetros:
        # -----------
        # tickers : list
        # Lista de nombres de los activos  
        # Retorna:
        # --------
        # w_M : numpy array or None
        #     Array de pesos del benchmark, o None si no se han ingresado correctamente
        # """
        st.info("Edita la columna 'Peso' directamente en la tabla")
        
        # Crear DataFrame inicial
        weights_df = pd.DataFrame({
            'Activo': tickers,
            'Peso': [1.0/n_assets] * n_assets
        })
        
        # Editor de datos
        edited_df = st.data_editor(
            weights_df,
            column_config={
                "Activo": st.column_config.TextColumn(
                    "Activo",
                    disabled=True
                ),
                "Peso": st.column_config.NumberColumn(
                    "Peso",
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    format="%.4f",
                    required=True
                )
            },
            hide_index=True,
            num_rows="fixed"
        )
        
        # Validar pesos
        total = edited_df['Peso'].sum()
        st.metric("Suma total de pesos", f"{total:.4f}")
        
        if abs(total - 1.0) > 0.0001:
            st.warning(f"⚠️ La suma de pesos es {total:.4f}, debe ser 1.00")
            
            # Normalizar automáticamente
            if st.button("🔧 Normalizar automáticamente", key="normalize_table"):
                edited_df['Peso'] = edited_df['Peso'] / total
                total = 1.0
                st.rerun()
        
        if abs(total - 1.0) <= 0.0001:
            w_M = edited_df['Peso'].values
            
            # Verificar que todos los pesos estén en [0, 1]
            if np.all((w_M >= 0) & (w_M <= 1)):
                st.success("✅ Pesos del benchmark validados correctamente")
                return w_M
            else:
                st.error("❌ Algunos pesos están fuera del rango [0, 1]")
                return None
    w_Mercado = create_benchmark_inputs(tickers)

    try:
        portfolio_assets_returns = df_general_filt.dropna()
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]

        # Llamada a la función que minimiza varianza para un retorno objetivo
        pesos_optimos,ret_post = black_litterman_portfolio(portfolio_assets_returns, 
                                                        tau_, 
                                                        tasa_ib_r, 
                                                        P, Q, w_Mercado, lam_, sum_constraint=True)
        pesos_optimos_alt,ret_post_alt = black_litterman_portfolio(portfolio_assets_returns, 
                                                        tau_, 
                                                        tasa_ib_r, 
                                                        P, Q, w_Mercado, lam_, sum_constraint=False)
        
        #pesos_optimos_alt_2,ret_post_alt_2,_ = black_litterman_portfolio_02(portfolio_assets_returns,
                                                                          #tau_, 
                                                                          #tasa_ib_r, 
                                                                          #P, Q, lam_,w_Mercado,#sum_constraint=True,
                                                                          #method='SLSQP', 
                                                                          #use_equilibrium=True)
        pesos_array = np.array(pesos_optimos)
        pesos_array_alt = np.array(pesos_optimos_alt)
        #pesos_array_alt_2 = np.array(pesos_optimos_alt_2)
        r_p = portfolio_assets_returns.dot(pesos_array)
        r_p_alt = portfolio_assets_returns.dot(pesos_array_alt)
        #r_p_alt_2 = portfolio_assets_returns.dot(pesos_array_alt_2)
    except Exception as e:
        st.warning(f"Error calculando portafolio: {e}. Se usan pesos homogéneos como fallback.")
        n_activos = len(tickers)
        pesos_array = np.array([1/n_activos] * n_activos)
        portfolio_assets_returns = df_general_filt.dropna()
        common_index = portfolio_assets_returns.index.intersection(benchmark_returns.index)
        portfolio_assets_returns = portfolio_assets_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        r_p = portfolio_assets_returns.dot(pesos_array)
    st.header('Pesos obtenidos para el modelo B-L',divider='red')
    st.write('Pesos del portafolio con restricciones')
    st.write(pd.DataFrame({'Tickers':pd.array(tickers),'Pesos del portafolio':pd.array(pesos_array)}))
    st.write('Pesos del portafolio sin restricciones')
    st.write(pd.DataFrame({'Tickers':pd.array(tickers),'Pesos del portafolio':pd.array(pesos_array_alt)}))
    #st.write('Alternativa 2')
    #st.write(pd.DataFrame({'Tickers':pd.array(tickers),'Pesos del portafolio':pd.array(pesos_array_alt_2)}))
    try:
            # Básicas
            ret_anual = retorno_anual_portafolio(r_p.values)
            vol_anual = volatilidad_portafolio(portfolio_assets_returns, pesos_array)
            sharpe = sharpe_ratio(r_p.values, rf=tasa_ib_r)
            # Riesgo y Distribución
            max_dd = max_drawdown(r_p.values)
            var_val, _ = var_historico(r_p.values, alpha=nivel_conf)
            cvar_val, _ = cvar_historico(r_p.values, alpha=nivel_conf)
            # Métricas Avanzadas (Nuevas)
            sesgo = sesgo_portafolio(r_p.values)
            curtosis = curtosis_portafolio(r_p.values)
            sortino = sortino_ratio(r_p.values, rf=tasa_ib_r)
            # Comparativas (Treynor y Beta)
            treynor, beta = treynor_ratio(r_p.values, benchmark_returns, r_p.index, rf_rate=tasa_ib_r)
    except Exception as e:
            st.error(f"Error en métricas: {e}")
            ret_anual = vol_anual = sharpe = max_dd = var_val = cvar_val = treynor = beta = sesgo = curtosis = sortino = 0
        # 4. Visualización de Resultados
    st.markdown("###  Desempeño del Portafolio")
        # FILA 1: Rendimiento y Riesgo Básico
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rendimiento Anual", f"{ret_anual:.2%}")
    col2.metric("Volatilidad Anual", f"{vol_anual:.2%}")
    col3.metric("Sharpe Ratio", f"{sharpe:.3f}")
    col4.metric("Sortino Ratio", f"{sortino:.3f}") 
        # FILA 2: Riesgo de Cola
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("VaR Histórico", f"{var_val:.2%}")
    col2.metric("CVaR Histórico", f"{cvar_val:.2%}")
    col3.metric("Max Drawdown", f"{max_dd:.2%}")
    col4.metric("Beta (vs Benchmark)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesgo", f"{sesgo:.3f}")       
    col2.metric("Curtosis", f"{curtosis:.3f}") 
    col3.metric("Treynor Ratio", f"{treynor:.3f}")
    st.subheader("Rendimiento Acumulado vs Benchmark")
    cum_ret_port = (1 + r_p).cumprod()
    cum_ret_bench = (1 + benchmark_returns.iloc[:, 0]).cumprod()
    st.line_chart(pd.DataFrame({"Portafolio": cum_ret_port, "Benchmark": cum_ret_bench}))
    #####
    #####
    # FIN 5TA PARTE RICARDO
    #####
    #####