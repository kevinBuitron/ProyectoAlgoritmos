import streamlit as st
import os
import pandas as pd
import sys

# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from Requisito3.analizar_abstracts import load_ris, count_keywords, extract_new_terms
from Requisito3.palabras import keywords as predefined_keywords
from Requisito3.interpretacion_visual import plot_bar_chart, plot_precision_results, ruta_graficos
from difflib import SequenceMatcher

# Ajusta si tu proyecto usa otra ruta por defecto (la misma que en las otras vistas)
DEFAULT_RIS_PATH = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Codigo/Requisito1/articulos_unicos.ris"

def evaluate_precision(new_terms, keywords_flat):
    """Evalúa similitud textual entre nuevas y conocidas (return lista dicts)."""
    results = []
    for word, freq in new_terms:
        similarities = [SequenceMatcher(None, word.lower(), kw.lower()).ratio() for kw in keywords_flat]
        precision = max(similarities) if similarities else 0.0
        results.append({"Palabra": word, "Frecuencia": int(freq), "Similitud": round(precision, 3)})
    return results

def asegurarse_ruta(ruta):
    if not os.path.exists(ruta):
        os.makedirs(ruta, exist_ok=True)

def categoria_view():
    st.title("🧭 Requerimiento 3 — Frecuencia y descubrimiento de palabras asociadas")
    st.write("Categoría: **Concepts of Generative AI in Education** y sus palabras asociadas. Se analizarán los abstracts del archivo por defecto.")

    # Comprobar archivo por defecto
    if not os.path.exists(DEFAULT_RIS_PATH):
        st.error(f"No se encontró el archivo por defecto:\n{DEFAULT_RIS_PATH}")
        if st.button("🏠 Volver al Home"):
            st.session_state.current_view = "home"
        return

    # Cargar abstracts
    abstracts = load_ris(DEFAULT_RIS_PATH)
    n = len(abstracts)
    st.markdown(f"**Abstracts encontrados:** {n}")
    if n == 0:
        st.warning("No se encontraron abstracts en el archivo RIS. Revisa el archivo.")
        return

    # Botón para ejecutar todo el flujo
    if st.button("▶ Ejecutar análisis de palabras"):
        with st.spinner("Analizando abstracts y generando resultados..."):
            asegurarse_ruta(ruta_graficos)

            # 1) Contar las palabras clave predefinidas
            keyword_data, keyword_counts = count_keywords(abstracts, predefined_keywords)

            # 2) Extraer nuevas palabras asociadas (top 15)
            new_terms = extract_new_terms(abstracts, predefined_keywords, top_n=15)

            # 3) Evaluar precisión: comparar nuevas palabras con todas las conocidas
            known_keywords_flat = [
                syn.lower()
                for cat in predefined_keywords.values()
                for term_syns in cat.values()
                for syn in term_syns
            ]
            precision_results = evaluate_precision(new_terms, known_keywords_flat)

            # 4) Guardar resultados en Excel
            df_keywords = pd.DataFrame(keyword_data)
            df_new = pd.DataFrame(new_terms, columns=["Término", "Frecuencia"])
            df_precision = pd.DataFrame(precision_results)

            out_dir = ruta_graficos
            asegurarse_ruta(out_dir)
            out_keywords = os.path.join(out_dir, "frecuencia_keywords_categorizadas.xlsx")
            out_new = os.path.join(out_dir, "nuevas_palabras.xlsx")
            out_precision = os.path.join(out_dir, "precision_nuevas_palabras.xlsx")

            df_keywords.to_excel(out_keywords, index=False)
            df_new.to_excel(out_new, index=False)
            df_precision.to_excel(out_precision, index=False)

            st.success("Análisis completado y guardado ✅")
            st.markdown(f"- Archivo frecuencias: `{out_keywords}`")
            st.markdown(f"- Nuevas palabras: `{out_new}`")
            st.markdown(f"- Precisión: `{out_precision}`")

            # 5) Mostrar tabla de frecuencias (top)
            st.subheader("Frecuencia — palabras predefinidas (Top)")
            if keyword_counts:
                df_counts = pd.DataFrame(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True), columns=["Término", "Frecuencia"])
                st.dataframe(df_counts)
            else:
                st.write("No se detectaron coincidencias con las palabras predefinidas en los abstracts.")

            # 6) Mostrar nuevas palabras sugeridas
            st.subheader("Nuevas palabras asociadas (top 15)")
            if new_terms:
                st.table(pd.DataFrame(new_terms, columns=["Término", "Frecuencia"]))
            else:
                st.write("No se encontraron nuevas palabras relevantes.")

            # 7) Mostrar y guardar gráficos (usando funciones que retornan la ruta)
            try:
                bar_path = plot_bar_chart(keyword_counts, out_path=os.path.join(out_dir, "frecuencia_palabras_clave.png"))
                st.image(bar_path, caption="Frecuencia palabras clave")
            except Exception as e:
                st.write(f"No se pudo generar el gráfico de barras: {e}")

            try:
                precision_path = plot_precision_results(precision_results, out_path=os.path.join(out_dir, "precision_nuevas_palabras.png"))
                st.image(precision_path, caption="Precisión nuevas palabras")
            except Exception as e:
                st.write(f"No se pudo generar el gráfico de precisión: {e}")

            # 8) Ofrecer descargas
            with open(out_keywords, "rb") as f:
                st.download_button("⬇️ Descargar frecuencias (Excel)", data=f, file_name=os.path.basename(out_keywords))
            with open(out_new, "rb") as f:
                st.download_button("⬇️ Descargar nuevas palabras (Excel)", data=f, file_name=os.path.basename(out_new))
            with open(out_precision, "rb") as f:
                st.download_button("⬇️ Descargar evaluación (Excel)", data=f, file_name=os.path.basename(out_precision))

    if st.button("🏠 Volver al Home"):
        st.session_state.current_view = "home"
