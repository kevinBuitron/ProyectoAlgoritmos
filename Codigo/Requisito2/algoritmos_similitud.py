import Levenshtein
import math
from collections import Counter
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_sim

"""
Esta clase contiene los algoritmos de similitud utilizados para el requerimiento 2, entre los cuales se encuentran:
- Distancia de Levenshtein (edit distance)
- Similitud de Jaccard (token-level)
- Coeficiente de Sørensen–Dice (token-level)
- Similitud de Cosine usando TF-IDF (vectorization statistical)
"""

def normalize_text(text):
    text = text.lower()
    # tokenización simple: mantener letras y números
    tokens = re.findall(r'\b[\w-]+\b', text)
    return tokens

# 1) Levenshtein distance (edit distance) - DP
def levenshtein_distancia(a: str, b: str) -> int:
    """Devuelve la distancia de edición (Levenshtein) entre a y b."""
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n
    dp = [[0] * (m+1) for _ in range(n+1)]
    for i in range(n+1):
        dp[i][0] = i
    for j in range(m+1):
        dp[0][j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1,       # delete
                           dp[i][j-1] + 1,       # insert
                           dp[i-1][j-1] + cost)  # replace
    return dp[n][m]

def normalized_levenshtein(a: str, b: str) -> float:
    """Devuelve 1 - (distancia / max_len) para tener una similitud entre 0 y 1."""
    if a == b:
        return 1.0
    dist = levenshtein_distancia(a, b)
    max_len = max(len(a), len(b))
    return 1.0 - (dist / max_len) if max_len > 0 else 0.0

# 2) Jaccard similarity (token-level)
def jaccard_similitud(a: str, b: str) -> float:
    tokens_a = set(normalize_text(a))
    tokens_b = set(normalize_text(b))
    if not tokens_a and not tokens_b:
        return 1.0
    inter = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(inter) / len(union) if union else 0.0

# 3) Sørensen–Dice coefficient (token-level)
def dice_coefficient(a: str, b: str) -> float:
    tokens_a = set(normalize_text(a))
    tokens_b = set(normalize_text(b))
    if not tokens_a and not tokens_b:
        return 1.0
    inter = len(tokens_a.intersection(tokens_b))
    return (2 * inter) / (len(tokens_a) + len(tokens_b)) if (len(tokens_a)+len(tokens_b)) > 0 else 0.0

# 4) Cosine similarity using TF-IDF (vectorization statistical)
def tfidf_cosine_similarity(docs: list, pair_indices=None):
    """
    docs: lista de strings (abstracts)
    pair_indices: lista de tuplas (i,j) para calcular solo pares. Si None, devuelve matriz completa.
    Devuelve matriz de similitud (numpy array) o diccionario de pares.
    """
    # Vectorizar con TF-IDF (preprocesamiento interno)
    vectorizer = TfidfVectorizer(lowercase=True, token_pattern=r'\b[\w-]+\b', stop_words='english')
    X = vectorizer.fit_transform(docs)  # shape (n_docs, n_features)
    sim_matrix = sk_cosine_sim(X)
    if pair_indices is None:
        return sim_matrix
    else:
        return { (i,j): float(sim_matrix[i,j]) for i,j in pair_indices }
