import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import yfinance as yf
import os
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
        col4.metric("Beta (vs SPY)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sesgo", f"{sesgo:.3f}")       
        col2.metric("Curtosis", f"{curtosis:.3f}") 
        col3.metric("Treynor Ratio", f"{treynor:.3f}")
        st.subheader("Rendimiento Acumulado vs SPY")
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
    # 1. DEFINIR PESOS (Homogéneos)
    n_activos = len(tickers)
    pesos_array = np.array([1/n_activos] * n_activos)
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
    col4.metric("Beta (vs SPY)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesgo", f"{sesgo:.3f}")       
    col2.metric("Curtosis", f"{curtosis:.3f}") 
    col3.metric("Treynor Ratio", f"{treynor:.3f}")
    st.subheader("Rendimiento Acumulado vs SPY")
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
    # 1. DEFINIR PESOS (Homogéneos)
    n_activos = len(tickers)
    pesos_array = np.array([1/n_activos] * n_activos)
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
    col4.metric("Beta (vs SPY)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesgo", f"{sesgo:.3f}")       
    col2.metric("Curtosis", f"{curtosis:.3f}") 
    col3.metric("Treynor Ratio", f"{treynor:.3f}")
    st.subheader("Rendimiento Acumulado vs SPY")
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
        "Tasa libre de Riesgo",
        min_value = 0.03,
        max_value = 0.5,
        value=0.2,
        step=0.01
    )
    #####
    #####
    # FIN 4TA PARTE RICARDO
    #####
    #####
    # 1. DEFINIR PESOS (Homogéneos)
    n_activos = len(tickers)
    pesos_array = np.array([1/n_activos] * n_activos)
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
    col4.metric("Beta (vs SPY)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesgo", f"{sesgo:.3f}")       
    col2.metric("Curtosis", f"{curtosis:.3f}") 
    col3.metric("Treynor Ratio", f"{treynor:.3f}")
    st.subheader("Rendimiento Acumulado vs SPY")
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
    # 4TA PARTE RICARDO
    #####
    #####
    # 1. DEFINIR PESOS (Homogéneos)
    n_activos = len(tickers)
    pesos_array = np.array([1/n_activos] * n_activos)
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
    col4.metric("Beta (vs SPY)", f"{beta:.3f}")
        # FILA 3: Distribución y Avanzadas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sesgo", f"{sesgo:.3f}")       
    col2.metric("Curtosis", f"{curtosis:.3f}") 
    col3.metric("Treynor Ratio", f"{treynor:.3f}")
    st.subheader("Rendimiento Acumulado vs SPY")
    cum_ret_port = (1 + r_p).cumprod()
    cum_ret_bench = (1 + benchmark_returns.iloc[:, 0]).cumprod()
    st.line_chart(pd.DataFrame({"Portafolio": cum_ret_port, "Benchmark": cum_ret_bench}))
    #####
    #####
    # 4TA PARTE RICARDO
    #####
    #####