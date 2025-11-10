import streamlit as st

# Importamos las vistas para llamar sus funciones
from home import home_view
from unificacion import unificacion_ris_view
from similitud import similitud_view

# Configuración inicial de la vista
if "current_view" not in st.session_state:
    st.session_state.current_view = "home"

# Navegación entre vistas
if st.session_state.current_view == "home":
    home_view()
if st.session_state.current_view == "unificacion":
    unificacion_ris_view()
if st.session_state.current_view == "similitud":
    similitud_view()
