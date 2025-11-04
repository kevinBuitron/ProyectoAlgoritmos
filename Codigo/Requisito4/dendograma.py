import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram

def plot_dendrogram(linkage_matrix, labels, title, out_path=None, max_clusters=30):
    """
    Dibuja un dendrograma truncado para evitar sobrecarga visual.
    max_clusters: número de grupos finales que se muestran.
    """
    plt.figure(figsize=(12, 6))
    dendrogram(
        linkage_matrix,
        labels=labels,
        leaf_rotation=90,
        truncate_mode='lastp',  # Mostrar solo los últimos clusters
        p=max_clusters,         # Número de clusters visibles
        show_contracted=True    # Muestra la contracción de subárboles
    )
    plt.title(f"{title} (Truncado a {max_clusters} clusters)")
    plt.xlabel("Clusters")
    plt.ylabel("Distancia")
    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300)
        plt.close()
    else:
        plt.show()
