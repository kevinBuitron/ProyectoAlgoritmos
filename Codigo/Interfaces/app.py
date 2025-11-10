import streamlit as st

# Importamos las vistas para llamar sus funciones
from home import home_view
from unificacion import unificacion_ris_view
from similitud import similitud_view
from categoria import categoria_view
from agrupamiento import agrupamiento_view
from visual import visual_view

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
if st.session_state.current_view == "categoria":
    categoria_view()
if st.session_state.current_view == "agrupamiento":
    agrupamiento_view()
if st.session_state.current_view == "visual":
    visual_view()