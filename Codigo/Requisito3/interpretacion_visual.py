import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import networkx as nx
from wordcloud import WordCloud
from networkx.algorithms import community
import matplotlib.patheffects as path_effects
import pandas as pd
from collections import Counter
from itertools import combinations
import matplotlib.cm as cm
import numpy as np
import matplotlib.patches as mpatches


# Ruta donde se guardarán los gráficos
ruta_graficos = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento3"

# Paso 4: Generar una gráfica de barras
def plot_bar_chart(keyword_counts, out_path=None):
    """
    Guarda un gráfico de barras con las frecuencias y devuelve la ruta del archivo guardado.
    Si out_path es None, usa ruta_graficos/frecuencia_palabras_clave.png
    """
    top_10 = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    keywords = [item[0] for item in top_10]
    counts = [item[1] for item in top_10]

    plt.figure(figsize=(12, 6))
    plt.barh(keywords, counts, color="skyblue")

    for i, count in enumerate(counts):
        plt.text(count + 0.5, i, str(count), va='center', fontsize=10)

    plt.xlabel("Frecuencia")
    plt.title("Top 20 - Frecuencia de Palabras Clave")
    plt.tight_layout()

    if out_path is None:
        out_path = os.path.join(ruta_graficos, "frecuencia_palabras_clave.png")
    plt.savefig(out_path)
    plt.close()
    return out_path


def plot_precision_results(precision_results, out_path=None):
    """
    Genera y guarda la gráfica de precisión (similitud) de nuevas palabras.
    Devuelve la ruta del archivo guardado.
    """
    df = pd.DataFrame(precision_results)
    plt.figure(figsize=(8, 5))
    plt.barh(df["Palabra"], df["Similitud"], color="skyblue")

    for i, sim in enumerate(df["Similitud"]):
        plt.text(sim + 0.01, i, str(round(sim, 2)), va='center', fontsize=10)

    plt.xlabel("Similitud con Palabras Clave Originales")
    plt.title("Evaluación de Precisión - Nuevas Palabras")
    plt.gca().invert_yaxis()
    plt.tight_layout()

    if out_path is None:
        out_path = os.path.join(ruta_graficos, "precision_nuevas_palabras.png")
    plt.savefig(out_path)
    plt.close()
    return out_path






