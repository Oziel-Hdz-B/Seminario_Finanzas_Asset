import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

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
        tickers_regiones = st.multiselect(
            label="Multiselect 1",
            options=[
            'SPLG',  # Tecnología
            'EWC',  # Finanzas
            'IEUR',  # Salud
            'EEM',  # Consumo básico
            'EWJ',  # Consumo discrecional
            ],
            default=["SPLG"]
        )
    else:
        ## Multiselect
        st.subheader("Activos por Sectores")
        tickers_sectores = st.multiselect(
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
    fecha_min = datetime(year=2000, month=1, day=1)
    fecha_max = fecha_hoy
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