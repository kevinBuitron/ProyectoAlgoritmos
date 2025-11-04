from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.cluster.hierarchy import linkage

def compute_distance_matrix(tfidf_matrix):
    similarity = cosine_similarity(tfidf_matrix)
    distance = 1 - similarity
    return distance

def perform_clustering(distance_matrix, method):
    """
    method: 'ward', 'average', 'complete'
    """
    linkage_matrix = linkage(distance_matrix, method=method)
    return linkage_matrix