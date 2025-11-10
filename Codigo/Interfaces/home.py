import streamlit as st

def home_view():
    st.title("Proyecto Final Algoritmos")
    st.subheader("Interfaz de usuario para el proyecto de bibliometria")
    st.write("Este proyecto tiene como objetivo implementar algoritmos que permitan el análisis bibliométrico y computacional sobre un dominio de conocimiento a partir de las bases de datos disponibles en la Universidad del Quindío.")
    st.write("Realizado por:")
    st.write("- Kevin Buitron")


    
    st.write("Selecciona una funcionalidad para continuar:")
    if st.button("Unificar Archivos RIS"):
        st.session_state.current_view = "unificacion"
    if st.button("Calcular similitud textual"):
        st.session_state.current_view = "similitud"
    if st.button("Categoria y palabras asociadas"):
        st.session_state.current_view = "categoria"
