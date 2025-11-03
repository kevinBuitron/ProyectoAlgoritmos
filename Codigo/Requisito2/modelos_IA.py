from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import pandas as pd

"""
Esta clase contiene los modelos de IA utilizados para el requerimiento 2
"""

# Ruta donde se guardarán los datos
ruta_graficos = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento2"

# Cargar modelo SBERT (pre-entrenado). all-MiniLM-L6-v2 es ligero y rápido.
MODEL_NAME = "all-MiniLM-L6-v2"

# Carga perezosa: solo al usar el módulo
_model = None
def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def sbert_embeddings(texts):
    model = _get_model()
    # devuelve array (n_texts, dim)
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True)

def sbert_cosine_similarity(texts, pair_indices=None):
    """
    texts: list[str]
    pair_indices: lista de tuplas (i,j) para cálculo selectivo
    """
    emb = sbert_embeddings(texts)  # normalizado si convert_to_numpy + normalize=True
    sim_matrix = cosine_similarity(emb)  # valores entre -1 y 1; con embeddings normalizados ~ [0,1]
    if pair_indices is None:
        return sim_matrix
    return { (i,j): float(sim_matrix[i,j]) for i,j in pair_indices }

def save_similarity_matrices(matrices_dict):
    """
    matrices_dict: dict with keys = algorithm names, values = (matrix, labels_list) OR dict-of-pairs
    Guarda matrices en Excel con hojas por algoritmo.
    """

    excel_path = os.path.join(ruta_graficos, f"matrices_results.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for name, val in matrices_dict.items():
            if isinstance(val, tuple):
                matrix, labels = val
                df = pd.DataFrame(matrix, index=labels, columns=labels)
                df.to_excel(writer, sheet_name=name[:31])  # sheet name length limit
            else:
                # dict of pairs -> transformar a df
                pairs = val
                df = pd.DataFrame([{"i":i,"j":j,"sim":s} for (i,j),s in pairs.items()])
                df.to_excel(writer, sheet_name=name[:31], index=False)
    return excel_path
