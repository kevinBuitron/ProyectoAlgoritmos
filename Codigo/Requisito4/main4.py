import os
import sys
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
import pandas as pd
import random

# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from preprocesar_texto import preprocess_abstracts
from similitud_clustering import compute_distance_matrix, perform_clustering
from dendograma import plot_dendrogram
from Requisito3.analizar_abstracts import load_ris  # reutiliza tu función

def main4(ris_path, output_dir="C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento4"):
    os.makedirs(output_dir, exist_ok=True)

    # 1️ Cargar abstracts
    abstracts = load_ris(ris_path)
    # 🔹 MUESTREO: toma 100 abstracts al azar
    sample_size = 100
    if len(abstracts) > sample_size:
        sample_indices = random.sample(range(len(abstracts)), sample_size)
        abstracts = [abstracts[i] for i in sample_indices]
        print(f" Se seleccionaron {sample_size} abstracts aleatorios para mejorar la visualización.")

    # 2️ Preprocesamiento
    tfidf_matrix, _ = preprocess_abstracts(abstracts)

    # 3️ Matriz de distancia
    distance_matrix = compute_distance_matrix(tfidf_matrix)

    # 4️ Aplicar los tres algoritmos y medir coherencia
    methods = ["ward", "average", "complete"]
    coherence_results = []  # aquí guardaremos los resultados

    for method in methods:
        print(f"\n=== Ejecutando clustering {method} ===")
        linkage_matrix = perform_clustering(distance_matrix, method)

        # --- Calcular coherencia (cophenetic correlation coefficient) ---
        coph_corr, _ = cophenet(linkage_matrix, pdist(tfidf_matrix.toarray()))
        coherence_results.append({"Método": method, "Coherencia": coph_corr})
        print(f"Coeficiente de coherencia ({method}): {coph_corr:.4f}")

        # --- Graficar dendrograma ---
        out_path = os.path.join(output_dir, f"dendrogram_{method}.png")
        plot_dendrogram(
            linkage_matrix,
            [f"A{i}" for i in range(len(abstracts))],
            title=f"Clustering Jerárquico - {method.capitalize()}",
            out_path=out_path
        )
        print(f"Dendrograma ({method}) guardado en {out_path}")

    # 5️ Guardar resultados de coherencia
    df_results = pd.DataFrame(coherence_results)
    df_results = df_results.sort_values(by="Coherencia", ascending=False)
    excel_path = os.path.join(output_dir, "coherencia_algoritmos.xlsx")
    df_results.to_excel(excel_path, index=False)
    print("\n Resultados de coherencia guardados en:", excel_path)

    print("\n=== Ranking de algoritmos por coherencia ===")
    print(df_results.to_string(index=False))

    # 6️ Identificar el mejor
    best = df_results.iloc[0]
    print(f"\n Mejor método: {best['Método']} (Coherencia = {best['Coherencia']:.4f})")


if __name__ == "__main__":
    ris_path = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Codigo/Requisito1/articulos_unicos.ris"
    main4(ris_path)
