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
def plot_bar_chart(keyword_counts):

    top_10 = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    # Separar claves y valores
    keywords = [item[0] for item in top_10]
    counts = [item[1] for item in top_10]

    plt.figure(figsize=(12, 6))
    plt.barh(keywords, counts, color="skyblue")

    #Agregar etiquetas al final de la barra
    for i, count in enumerate(counts):
        plt.text(count + 0.5, i, str(count), va='center', fontsize=10)

    plt.xlabel("Frecuencia")
    plt.title("Top 20 - Frecuencia de Palabras Clave")
    plt.tight_layout()
    plt.savefig(os.path.join(ruta_graficos, "frecuencia_palabras_clave.png"))
    plt.close()

def generate_wordcloud(keyword_counts):
        wordcloud = WordCloud(
        width=1600,              # Mayor resolución horizontal
        height=800,              # Mayor resolución vertical
        background_color="white",
        colormap="tab10",        # Mejores colores (puedes probar: "viridis", "plasma", "Set2", etc.)
        prefer_horizontal=0.9,   # Preferir palabras en horizontal
        max_words=200,           # Aumenta el número de palabras visibles
        contour_color='black',   # Borde negro (opcional)
        contour_width=0.5        # Grosor del borde
    ).generate_from_frequencies(keyword_counts)

        plt.figure(figsize=(16, 8))  # Lienzo más grande
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(os.path.join(ruta_graficos, "nube_palabras_clave.png"), dpi=300)  # Alta resolución
        plt.close()
