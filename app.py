import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import yfinance as yf

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

    **Integrantes:**
    - Flores Moreno Alan Alberto
    - Gonzales Carapia Ricardo 
    - Hernández Banda Oziel
    - Jimenez Borzani Daniela Naomi
    """)

    st.header("Escoge los ativos")

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
            label="Multiselect 1",
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
            label="Multiselect 2",
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
    
    st.header("Escoge las fechas de inicio y fin para los datos")
    ## Date input
    st.subheader("Fechas")
    fecha_hoy = datetime.today()
    fecha_min = datetime(year=2010, month=1, day=1)
    fecha_max = datetime(year=2025, month=12, day=2)
    fecha_inicio = st.date_input(
        "Input Fecha de incio",
        fecha_hoy,
        min_value=fecha_min,
        max_value=fecha_max
    )
    fecha_fin = st.date_input(
        "Input Fecha de fin",
        fecha_hoy,
        min_value=fecha_min,
        max_value=fecha_max
    )
    fecha_inicio = datetime(year=fecha_inicio.year, month=fecha_inicio.month, day=fecha_inicio.day)
    fecha_fin = datetime(year=fecha_fin.year, month=fecha_fin.month, day=fecha_fin.day)

    st.markdown("---")

"""
# Descarga de datos para todos los tickers
@st.cache_data
def obtener_datos (stocks):
    df = yf.download(stocks, 
                     start=datetime(year = 2010, 
                                  month = 1, 
                                  day = 1),
                     end=datetime(year = datetime.today().year, 
                                  month =datetime.today().month, 
                                  day = datetime.today().day ))
    
df_regiones = obtener_datos(['SPLG','EWC','IEUR','EEM','EWJ'])
df_sectores = obtener_datos(['XLK','XLF','XLV','XLY','XLE','XLI','XLC','XLB','XLU','XLRE'])

st.write(pd.DataFrame(df_sectores))
st.write(pd.DataFrame(df_regiones))

df_sectores = pd.DataFrame(df_sectores).dropna(how="all",axis=1).dropna(how="any")
st.write(df_sectores)
"""

# #############################################################################
# ##################################
# 1RA PARTE, SELECCIONAR EL TIPO DE PORTAFOLIO
# ##################################
# #############################################################################

st.header("Escoge el tipo de portafolio que gustes")

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

elif str(portafolio_tipo) == 'Portafolio optimizado - Mínima Varianza':
    # ###########################################################################
    # SEGUNDO CASO
    # ###########################################################################
    pass
elif str(portafolio_tipo) == 'Portafolio optimizado - Máximo Sharpe':
    # ###########################################################################
    # TERCER CASO
    # ###########################################################################
    pass
elif str(portafolio_tipo) == 'Portafolio optimizado - Black Litterman':
    # ###########################################################################
    # QUINTO CASO
    # ###########################################################################
    pass