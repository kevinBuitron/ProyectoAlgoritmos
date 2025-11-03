import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import combinations
import os

# Ruta donde se guardarán los gráficos
ruta_graficos = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento2"

# Aqui contruimos las parejas con los n abstracts que tenemos para manejarlos
def build_pair_indices(n):
    """Todas las combinaciones i<j para n elementos."""
    return list(combinations(range(n), 2))

# Aqui convertimos el diccionario de parejas a una matriz completa
def pair_results_to_matrix(pair_dict, n):
    """Convertir dict (i,j)->sim a matriz completa sim[i][j] sim[j][i]"""
    mat = np.eye(n)
    for (i,j), s in pair_dict.items():
        mat[i,j] = s
        mat[j,i] = s
    return mat

# Finalmente generamos un grafico de calor para visualizar las similitudes
def plot_heatmap(matrix, labels, title, out_path=None):
    n = len(labels)
    matrix = np.array(matrix)

    # Ajustar tamaño del gráfico según número de abstracts
    fig_width = max(8, n * 0.4)
    fig_height = max(6, n * 0.4)
    plt.figure(figsize=(fig_width, fig_height))

    # Mostrar valores solo si la matriz es pequeña (<15 abstracts)
    show_values = n <= 15

    ax = sns.heatmap(
        matrix,
        xticklabels=labels,
        yticklabels=labels,
        cmap="viridis",
        cbar_kws={"label": "Similitud"},
        annot=show_values,
        fmt=".2f" if show_values else "",
        linewidths=0.2
    )

    plt.title(title, fontsize=14, pad=12)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(ruta_graficos, "frecuencia_palabras_clave.png"))
    plt.close()

#Top 10 abstacts mas similitud
def plot_top_similar_heatmap(matrix, labels, title, out_path=None, top_n=10):
    
    matrix = np.array(matrix)
    mean_sim = np.mean(matrix, axis=1)
    top_idx = np.argsort(mean_sim)[-top_n:]
    top_matrix = matrix[np.ix_(top_idx, top_idx)]
    top_labels = [labels[i] for i in top_idx]

    plt.figure(figsize=(8, 6))
    sns.heatmap(top_matrix, xticklabels=top_labels, yticklabels=top_labels, cmap="viridis", annot=True, fmt=".2f")
    plt.title(f"Top {top_n} abstracts más similares", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(ruta_graficos, "heatmap_top10.png"))
    plt.close()
