# similitud_clustering.py (corregido)
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import pdist, squareform

def compute_distance_matrix_from_tfidf(tfidf_matrix):
    """
    Recibe tfidf_matrix (sparse matrix) y devuelve:
    - distance_sq: matriz de distancias cuadrada NxN
    - distance_condensed: vector condensado (pdist) usable por linkage
    """
    # similarity (NxN)
    similarity = cosine_similarity(tfidf_matrix)
    distance_sq = 1.0 - similarity
    # condensada
    # pdist espera la matriz de observaciones; si ya tenemos similarity -> usamos squareform
    from scipy.spatial.distance import squareform
    distance_condensed = squareform(distance_sq, checks=False)
    return distance_sq, distance_condensed

def perform_clustering_from_condensed(distance_condensed, method):
    """
    Ejecuta linkage a partir de la distancia condensada (formato pdist).
    method: 'ward' (nota: 'ward' requiere distancias euclidianas sobre observaciones),
            'average', 'complete', 'single', etc.
    IMPORTANTE: Para 'ward' lo más correcto es dar linkage sobre vectores (no sobre distancias),
    pero aún puede usarse si se transforma adecuadamente; aquí asumimos 'average' y 'complete' son válidos.
    """
    # Si el método es 'ward' conviene hacer linkage sobre vectores — la vista usará tfidf_matrix en ese caso.
    linkage_matrix = linkage(distance_condensed, method=method)
    return linkage_matrix
