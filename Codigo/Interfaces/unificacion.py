import streamlit as st
import os
import tempfile
import unicodedata
import re
from collections import defaultdict

# === Función para normalizar texto ===
def normalize(text):
    """
    Normaliza un texto para comparación:
    - Maneja None/string vacíos
    - Pasa a minúsculas
    - Elimina acentos
    - Quita puntuación (queda solo letras, números y espacios)
    - Elimina espacios al inicio/fin
    """
    if not text:
        return ""
    # Minúsculas
    text = text.lower()
    # Normalizar y eliminar acentos
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    # Eliminar puntuación y símbolos especiales, excepto letras, números y espacios
    text = re.sub(r"[^\w\s]", "", text)
    # Quitar espacios innecesarios
    return text.strip()


# === Función para procesar archivo RIS y separar únicos/duplicados por título normalizado ===
def process_ris_file(input_path, unique_output, duplicate_output):
    """
    Lee un archivo RIS desde 'input_path', agrupa artículos por título normalizado
    y escribe dos archivos: uno con artículos únicos y otro con los duplicados.
    """
    articles = defaultdict(list)  # Diccionario para agrupar artículos por título normalizado

    with open(input_path, "r", encoding="utf-8") as file:  # Abre el archivo RIS en modo lectura
        current_article, current_title = [], None  # Inicializa las variables para almacenar un artículo
        for line in file:  # Itera sobre cada línea del archivo
            if line.startswith("TY  -"):  # Detecta el inicio de un nuevo artículo
                if current_article and current_title:  # Guarda el artículo anterior si ya existe
                    articles[normalize(current_title)].append(current_article)  # Agrupa por título
                current_article, current_title = [line], None  # Reinicia el artículo actual
            else:
                current_article.append(line)  # Agrega la línea actual al artículo
                if line.startswith(("TI  -", "T1  -")):  # Detecta el título del artículo
                    # Extrae el título removiendo el prefijo y posibles espacios
                    # Notar que en RIS el título suele comenzar en la posición después del 'TI  - '
                    current_title = line.split(" - ", 1)[1].strip() if " - " in line else line[6:].strip()

        # Guarda el último artículo leído antes de finalizar
        if current_article and current_title:
            articles[normalize(current_title)].append(current_article)

    # Escribe los artículos únicos y duplicados en sus respectivos archivos
    with open(unique_output, "w", encoding="utf-8") as u, open(duplicate_output, "w", encoding="utf-8") as d:
        for entries in articles.values():  # Itera sobre cada grupo de artículos
            # Escribe el primer artículo del grupo como "único"
            u.writelines(entries[0] + ["\n"])
            # Si hay más de uno en el grupo, escribimos los siguientes como duplicados
            if len(entries) > 1:
                # concatenamos todas las listas (cada artículo es una lista de líneas)
                d.writelines(sum(entries[1:], []) + ["\n"])


# === INTERFAZ PRINCIPAL ===
def unificacion_ris_view():
    st.title("📘 Unificación y Detección de Duplicados (Archivo RIS)")
    st.subheader("Sube tu archivo `articulos_fusionados.ris` para analizar duplicados y unificar resultados.")

    uploaded_file = st.file_uploader("Selecciona tu archivo RIS", type=["ris"])

    if uploaded_file:
        # Guardamos temporalmente el archivo RIS subido para procesarlo con la función basada en archivos
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ris", mode="w", encoding="utf-8") as tmp_in:
            input_path = tmp_in.name
            tmp_in.write(uploaded_file.getvalue().decode("utf-8"))

        st.success("Archivo subido correctamente y listo para procesar.")

        # Crear ficheros de salida temporales
        tmp_dir = tempfile.mkdtemp()
        unique_path = os.path.join(tmp_dir, "articulos_unicos.ris")
        duplicate_path = os.path.join(tmp_dir, "articulos_duplicados.ris")

        # Procesar archivo (agrupa por título normalizado y separa duplicados)
        process_ris_file(input_path, unique_path, duplicate_path)

        # Leer resultados para mostrar conteos y previsualizar
        def contar_registros_ris(path):
            if not os.path.exists(path):
                return 0
            count = 0
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("TY  -"):
                        count += 1
            return count

        n_unicos = contar_registros_ris(unique_path)
        n_duplicados = contar_registros_ris(duplicate_path)

        st.markdown(f"**✅ Registros únicos:** {n_unicos}")
        st.markdown(f"**⚠️ Registros duplicados:** {n_duplicados}")

        # Mostrar una previsualización (primeros 5000 caracteres) de cada archivo si existen
        if n_unicos > 0:
            with open(unique_path, "r", encoding="utf-8") as f:
                preview = f.read(500)
            st.subheader("Previsualización — artículos únicos (primeros 500 caracteres)")
            st.code(preview)

        if n_duplicados > 0:
            with open(duplicate_path, "r", encoding="utf-8") as f:
                preview_dup = f.read(500)
            st.subheader("Previsualización — artículos duplicados (primeros 500 caracteres)")
            st.code(preview_dup)

        # Botones para descargar los archivos de salida
        with open(unique_path, "r", encoding="utf-8") as f:
            unique_data = f.read()
        with open(duplicate_path, "r", encoding="utf-8") as f:
            duplicate_data = f.read()

        st.download_button(
            "⬇️ Descargar artículos únicos",
            data=unique_data,
            file_name="articulos_unicos.ris",
            mime="text/plain"
        )
        st.download_button(
            "⬇️ Descargar artículos duplicados",
            data=duplicate_data,
            file_name="articulos_duplicados.ris",
            mime="text/plain"
        )

        # (Opcional) limpiar archivos temporales si no los necesitas después de la descarga
        # os.remove(input_path)
        # os.remove(unique_path)
        # os.remove(duplicate_path)
        # os.rmdir(tmp_dir)

    # Botón para volver al inicio (mantengo la misma lógica que tenías)
    if st.button("🏠 Volver al Home"):
        st.session_state.current_view = "home"


# Si deseas ejecutar esta vista directamente (por ejemplo, al ejecutar el script),
# descomenta la siguiente línea y ejecuta `streamlit run app.py`
# unificacion_ris_view()
