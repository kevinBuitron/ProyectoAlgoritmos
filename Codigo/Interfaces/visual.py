# requerimiento5_streamlit.py  (añádelo a tu carpeta de vistas)
import streamlit as st
import os
import tempfile
import sys

# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Requisito5.graficos import generar_mapa_calor, generar_linea_tiempo, generar_nube_palabras
from Requisito5.exportar_pdf import exportar_pdf
from Requisito3.analizar_abstracts import parse_large_ris

# Ruta RIS por defecto (ajusta si la tienes en otra ubicación)
DEFAULT_RIS_PATH = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Codigo/Requisito1/articulos_unicos.ris"
# Carpeta donde ya guardan graficos (según tu repo)
OUTPUT_DIR = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5"

def visual_view():
    st.title("📊 Requerimiento 5 — Análisis visual de la producción científica")
    st.write("Se muestran mapa geográfico, nube de palabras y línea temporal. Para evitar problemas con kaleido, el mapa y la línea temporal se presentan interactivos en el navegador; si deseas incluirlos en el PDF descarga esas imágenes desde el navegador y súbelas aquí. La nube de palabras se genera localmente y se incluye por defecto en el PDF.")

    if not os.path.exists(DEFAULT_RIS_PATH):
        st.error(f"No se encontró el archivo por defecto:\n{DEFAULT_RIS_PATH}")
        if st.button("🏠 Volver al Home"):
            st.session_state.current_view = "home"
        return

    # Cargar registros RIS (usa tu parser parse_large_ris)
    entries = list(parse_large_ris(DEFAULT_RIS_PATH))
    if not entries:
        st.warning("No se encontraron abstracts en el archivo RIS.")
        return

    # Preparar texto completo para la nube (abstracts + keywords)
    # Detectar columnas como en tu script main5
    import pandas as pd
    df = pd.DataFrame(entries)
    abstract_col = next((c for c in ["AB", "Abstract"] if c in df.columns), None)
    keywords_col = next((c for c in ["KW", "Keywords"] if c in df.columns), None)
    texto_completo = ""
    if abstract_col:
        texto_completo += " ".join(df[abstract_col].dropna().astype(str).tolist())
    if keywords_col:
        texto_completo += " " + " ".join(df[keywords_col].dropna().astype(str).tolist())

    st.markdown("### 1) Nube de palabras (incluida por defecto en el PDF)")
    # Generar nube (tu función guarda el PNG y devuelve la ruta)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nube_path = generar_nube_palabras(texto_completo, out_path=None)
    if nube_path and os.path.exists(nube_path):
        st.image(nube_path, caption="Nube de palabras (puedes descargarla directamente desde aquí)", use_column_width=True)
    else:
        st.write("No se pudo generar la nube de palabras.")

    st.markdown("### 2) Mapa geográfico (interactivo)")
    # Generar mapa con plotly — la función original usa fig.show(); aquí la retornamos y mostramos con Streamlit
    # Si tu generar_mapa_calor ya hace fig.show(), puedes modificarla para que retorne fig; si no, usaremos la versión actual que hace show()
    try:
        fig_map = generar_mapa_calor(df)  # según tu implementación puede return path o None; la ideal es que retorne figura
        # Si generar_mapa_calor devuelve un objeto plotly (fig), lo mostramos:
        if hasattr(fig_map, "to_plotly_json") or getattr(fig_map, "data", None) is not None:
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            # Si tu función llamó fig.show() y no retornó fig, informamos al usuario
            st.info("El mapa se mostró en el navegador. Para guardarlo en tu máquina haz clic derecho sobre el mapa y elige 'Guardar imagen como...'. Luego súbelo abajo para que forme parte del PDF.")
    except Exception as e:
        st.write("No se pudo generar el mapa interactivo directamente:", e)
        st.info("Si el mapa no se muestra, ejecuta el script localmente para generar el gráfico con fig.show() y guarda la imagen manualmente.")

    st.markdown("### 3) Línea temporal (interactiva)")
    try:
        fig_line = generar_linea_tiempo(df, top_n=20)
        if hasattr(fig_line, "to_plotly_json") or getattr(fig_line, "data", None) is not None:
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("La línea temporal se mostró en el navegador; para guardarla: clic derecho → Guardar imagen como... y súbela abajo.")
    except Exception as e:
        st.write("No se pudo generar la línea temporal directamente:", e)
        st.info("Si no se muestra, guarda la imagen manualmente y súbela más abajo para el PDF.")

    st.markdown("### 4) Incluir imágenes en el PDF")
    st.write("La nube de palabras se incluye por defecto. Si quieres que el PDF incluya también el mapa y la línea temporal, descarga esas dos imágenes desde el navegador y súbelas aquí (opcional).")

    uploaded_map = st.file_uploader("Sube aquí el archivo PNG del Mapa (opcional)", type=["png", "jpg", "jpeg"])
    uploaded_line = st.file_uploader("Sube aquí el archivo PNG de la Línea temporal (opcional)", type=["png", "jpg", "jpeg"])

    # Guardar uploads temporales si existen
    files_for_pdf = {}
    # incluir siempre la nube de palabras si existe
    if nube_path and os.path.exists(nube_path):
        files_for_pdf["Nube de palabras"] = nube_path

    def save_uploaded_temp(uploaded_file, default_name):
        if not uploaded_file:
            return None
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
        tmp.write(uploaded_file.getvalue())
        tmp.flush()
        tmp.close()
        return tmp.name

    map_path = save_uploaded_temp(uploaded_map, "mapa.png")
    line_path = save_uploaded_temp(uploaded_line, "linea.png")
    if map_path:
        files_for_pdf["Mapa geográfico"] = map_path
    if line_path:
        files_for_pdf["Línea temporal"] = line_path

    st.markdown("### 5) Exportar a PDF")
    st.write("Al pulsar 'Generar PDF' se creará un PDF que incluirá la nube de palabras y las imágenes que hayas subido. Si no subes mapa ni línea temporal, el PDF contendrá únicamente la nube de palabras.")

    if st.button("Generar PDF"):
        if not files_for_pdf:
            st.warning("No hay imágenes disponibles para exportar. Generando PDF con la nube de palabras (si existe).")
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            output_pdf = os.path.join(OUTPUT_DIR, "analisis_visual_requerimiento5.pdf")
            exportar_pdf(files_for_pdf, output_path=output_pdf)
            st.success(f"PDF generado: {output_pdf}")
            with open(output_pdf, "rb") as f:
                st.download_button("⬇️ Descargar PDF", data=f, file_name=os.path.basename(output_pdf), mime="application/pdf")
        except Exception as e:
            st.error(f"No se pudo generar el PDF: {e}")

    if st.button("🏠 Volver al Home"):
        st.session_state.current_view = "home"
