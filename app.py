import streamlit as st

# Sidebar
with st.sidebar:
    # Información del proyecto
    st.title("⚙️ Proyecto 1")
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    st.markdown("""

    **👥 Integrantes:**
    - Oziel Hernández
    - Daniela Borzani
    - Santiago Cruz
    - Ximena Paredes
    """)
    st.markdown("---")