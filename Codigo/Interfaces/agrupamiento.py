import streamlit as st
import os
import random
import pandas as pd
import numpy as np
import sys
# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Requisito4.preprocesar_texto import preprocess_abstracts
from Requisito4.similitud_clustering import compute_distance_matrix_from_tfidf, perform_clustering_from_condensed
from Requisito4.dendograma import plot_dendrogram
from scipy.cluster.hierarchy import linkage, fcluster, cophenet
from scipy.spatial.distance import pdist
from sklearn.metrics import silhouette_score

# Ajusta tu ruta por defecto a la de tu proyecto
DEFAULT_RIS_PATH = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Codigo/Requisito1/articulos_unicos.ris"
OUTPUT_DIR = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento4"

def agrupamiento_view():
    st.title("🌳 Requerimiento 4 — Clustering jerárquico y dendrogramas")
    st.write("Esta interfaz nos muestra una breve descripción del proceso que combina preprocesamiento, cálculo de similitud y agrupamiento jerárquico. Luego ofrece controles numéricos para definir parámetros como el tamaño de la muestra de abstracts, el número máximo de clusters que se mostrarán en el dendrograma y la cantidad de grupos para calcular el índice Silhouette.")
    st.write("Preprocesamiento → similitud → clustering jerárquico (3 métodos) → evaluación (cophenetic + silhouette) → dendrogramas.")

    # Parámetros de usuario
    sample_size = st.number_input("Tamaño muestra (0 = usar todos)", min_value=0, value=100)
    max_clusters_show = st.number_input("Máx clusters a mostrar en dendrograma (truncate p)", min_value=5, value=30)
    n_clusters_for_silhouette = st.number_input("Número de clusters para Silhouette (k)", min_value=2, value=5)

    if not os.path.exists(DEFAULT_RIS_PATH):
        st.error(f"No se encontró archivo RIS por defecto: {DEFAULT_RIS_PATH}")
        if st.button("🏠 Volver al Home"):
            st.session_state.current_view = "home"
        return

    # Cargar abstracts (reusa tu función load_ris si existe)
    from Requisito3.analizar_abstracts import load_ris
    abstracts = load_ris(DEFAULT_RIS_PATH)
    if len(abstracts) == 0:
        st.warning("No hay abstracts en el archivo RIS.")
        return

    # Muestreo
    if sample_size > 0 and len(abstracts) > sample_size:
        indices = random.sample(range(len(abstracts)), sample_size)
        abstracts_sample = [abstracts[i] for i in indices]
        st.write(f"Usando muestra aleatoria de {sample_size} abstracts (de {len(abstracts)})")
    else:
        abstracts_sample = abstracts
        st.write(f"Usando todos los abstracts ({len(abstracts_sample)})")

    # Botón para ejecutar pipeline
    if st.button("▶ Ejecutar clustering jerárquico"):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        with st.spinner("Preprocesando y vectorizando (TF-IDF)..."):
            tfidf_matrix, vectorizer = preprocess_abstracts(abstracts_sample)  # devuelve sparse matrix y vectorizer

        st.success("TF-IDF listo")

        # Calcular matriz de distancia cuadrada y condensada
        st.info("Calculando matriz de distancia (1 - coseno)...")
        distance_sq, distance_condensed = compute_distance_matrix_from_tfidf(tfidf_matrix)

        results = []
        methods = ["average", "complete", "ward"]  # usaremos ward con vectores directamente

        for method in methods:
            st.write(f"--- Método: {method} ---")
            try:
                if method == "ward":
                    # linkage directo sobre observaciones (reducir dimensionalidad si necesario)
                    # Convertir a dense o aplicar PCA si es muy grande. Aquí usamos toarray() (cuidado con memoria).
                    linkage_matrix = linkage(tfidf_matrix.toarray(), method="ward")
                    # Para cophenet, pasamos pdist sobre observaciones
                    coph_corr, _ = cophenet(linkage_matrix, pdist(tfidf_matrix.toarray()))
                else:
                    linkage_matrix = perform_clustering_from_condensed(distance_condensed, method=method)
                    # cophenet con pdist sobre vectores TF-IDF (condensado)
                    coph_corr, _ = cophenet(linkage_matrix, pdist(tfidf_matrix.toarray()))
                st.write(f"Cophenetic Correlation: {coph_corr:.4f}")
            except Exception as e:
                st.write(f"Error en clustering {method}: {e}")
                continue

            # Silhouette: cortar dendrograma en k clusters y medir
            try:
                labels = fcluster(linkage_matrix, t=n_clusters_for_silhouette, criterion='maxclust')
                unique_labels = len(set(labels))
                if unique_labels < 2:
                    st.warning(f"fcluster devolvió {unique_labels} cluster(s). Intentando fallback con AgglomerativeClustering...")
                    from sklearn.cluster import AgglomerativeClustering
                    agg = AgglomerativeClustering(n_clusters=min(n_clusters_for_silhouette, len(abstracts_sample)-1),
                                                affinity='cosine', linkage='average')
                    labels = agg.fit_predict(tfidf_matrix.toarray())
                    unique_labels = len(set(labels))

                if 2 <= unique_labels <= (len(abstracts_sample)-1):
                    sil = silhouette_score(tfidf_matrix.toarray(), labels, metric='cosine')
                    st.write(f"Silhouette (k={n_clusters_for_silhouette}): {sil:.4f}")
                else:
                    st.write(f"No es posible calcular Silhouette: etiquetas únicas = {unique_labels}")
            except Exception as e:
                st.write(f"No se pudo calcular Silhouette para {method}: {e}")
                sil = None

            # Guardar dendrograma
            out_png = os.path.join(OUTPUT_DIR, f"dendrogram_{method}.png")
            plot_dendrogram(linkage_matrix, labels=[f"A{i}" for i in range(len(abstracts_sample))],
                            title=f"Dendrograma - {method}", out_path=out_png, max_clusters=max_clusters_show)
            st.image(out_png, caption=f"Dendrograma - {method}")

            results.append({"Método": method, "Cophenet": coph_corr, "Silhouette": sil})

        # Guardar y mostrar ranking
        df_res = pd.DataFrame(results).sort_values(by="Cophenet", ascending=False)
        out_excel = os.path.join(OUTPUT_DIR, "coherencia_clustering.xlsx")
        df_res.to_excel(out_excel, index=False)
        st.success("Análisis completado. Resultados guardados.")
        st.dataframe(df_res)
        with open(out_excel, "rb") as f:
            st.download_button("⬇️ Descargar resultados (Excel)", data=f, file_name=os.path.basename(out_excel))

    if st.button("🏠 Volver al Home"):
        st.session_state.current_view = "home"
