from tqdm import tqdm
import os
import argparse
import pandas as pd
import sys
from concurrent.futures import ProcessPoolExecutor
import random


# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# importar utilidades
from Requisito2.algoritmos_similitud import (
    jaccard_similitud, dice_coefficient, normalized_levenshtein, tfidf_cosine_similarity, normalize_text
)
from Requisito2.modelos_IA import sbert_cosine_similarity, save_similarity_matrices
from Requisito2.evaluacion_resultados import build_pair_indices, pair_results_to_matrix, plot_heatmap, plot_top_similar_heatmap

# Si quieres reutilizar tu parser RIS del Requisito3:
try:
    from Requisito3.analizar_abstracts import load_ris
except Exception:
    load_ris = None
    print("No se encontró Requisito3.analizar_abstracts.load_ris - asegúrate de importarlo o pasar abstracts manualmente.")

# ==== funciones auxiliares para multiprocessing ====

def compute_jaccard_pair(args):
    tokenized, i, j = args
    inter = tokenized[i].intersection(tokenized[j])
    union = tokenized[i].union(tokenized[j])
    return (i, j, len(inter) / len(union) if union else 0.0)

def compute_dice_pair(args):
    tokenized, i, j = args
    inter = len(tokenized[i].intersection(tokenized[j]))
    total = len(tokenized[i]) + len(tokenized[j])
    return (i, j, (2 * inter) / total if total > 0 else 0.0)

def compute_levenshtein_pair(args):
    abstracts, i, j = args
    from Requisito2.algoritmos_similitud import normalized_levenshtein
    return (i, j, normalized_levenshtein(abstracts[i], abstracts[j]))

def compute_all_similarities(abstracts):
    """
    Versión optimizada con mensajes en consola y tqdm.
    """
    n = len(abstracts)
    pair_idxs = build_pair_indices(n)

    print(f"\n Total de pares a comparar: {len(pair_idxs)}")

    # Pre-tokenizar
    print("Preprocesando textos...")
    tokenized = [set(normalize_text(ab)) for ab in abstracts]

    # Crear listas de argumentos para enviar a los procesos
    jaccard_args = [(tokenized, i, j) for i, j in pair_idxs]
    dice_args = [(tokenized, i, j) for i, j in pair_idxs]
    lev_args = [(abstracts, i, j) for i, j in pair_idxs]

    # === Calcular Jaccard ===
    print("\nCalculando Jaccard...")
    with ProcessPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(compute_jaccard_pair, jaccard_args), total=len(pair_idxs)))
    jac_pairs = {(i, j): val for i, j, val in results}
    print("✓ Jaccard completado")

    # === Calcular Dice ===
    print("\nCalculando coeficiente Dice...")
    with ProcessPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(compute_dice_pair, dice_args), total=len(pair_idxs)))
    dice_pairs = {(i, j): val for i, j, val in results}
    print("✓ Dice completado")

    # === Calcular Levenshtein ===
    print("\nCalculando similitud Levenshtein...")
    with ProcessPoolExecutor(max_workers=4) as ex:
        results = list(tqdm(ex.map(compute_levenshtein_pair, lev_args), total=len(pair_idxs)))
    lev_pairs = {(i, j): val for i, j, val in results}
    print("✓ Levenshtein completado")

    # === TF-IDF cosine ===
    print("\nCalculando TF-IDF Cosine...")
    tfidf_matrix = tfidf_cosine_similarity(abstracts)
    print("✓ TF-IDF completado")

    # === SBERT cosine ===
    print("\nCalculando SBERT Cosine...")
    sbert_matrix = sbert_cosine_similarity(abstracts)
    print("✓ SBERT completado")

    # === Convertir a matrices ===
    lev_mat = pair_results_to_matrix(lev_pairs, n)
    jac_mat = pair_results_to_matrix(jac_pairs, n)
    dice_mat = pair_results_to_matrix(dice_pairs, n)

    results = {
        "Levenshtein": (lev_mat, abstracts),
        "Jaccard": (jac_mat, abstracts),
        "Dice": (dice_mat, abstracts),
        "TFIDF_Cosine": (tfidf_matrix, abstracts),
        "SBERT_Cosine": (sbert_matrix, abstracts)
    }

    return results

def main_from_ris(ris_path, indices=None, output_dir="Requisito2_outputs", sample_size=200, truncate_len=1000):
    if load_ris is None:
        raise RuntimeError("No hay función load_ris disponible para leer archivos RIS.")

    # === 1. Cargar abstracts ===
    entries = load_ris(ris_path)

    if entries and isinstance(entries[0], dict):
        abstracts = []
        for e in entries:
            ab = e.get('AB') or e.get('ab') or e.get('Abstract') or ""
            abstracts.append(ab if isinstance(ab, str) else " ".join(ab) if isinstance(ab, list) else "")
    else:
        abstracts = entries  # ya es lista de strings

    total_abstracts = len(abstracts)
    print(f"\n Total de abstracts disponibles: {total_abstracts}")

    # === 2. Selección de muestra o índices ===
    if indices:
        abstracts = [abstracts[i] for i in indices if i < total_abstracts]
        print(f" Se analizarán los {len(abstracts)} abstracts seleccionados manualmente ({indices}).")
    else:
        if total_abstracts > sample_size:
            print(f"  Se tomarán aleatoriamente {sample_size} abstracts de {total_abstracts} para optimizar el rendimiento.")
            abstracts = random.sample(abstracts, sample_size)
        else:
            print(f" Se analizarán los {total_abstracts} abstracts disponibles (no se requiere muestreo).")

    # === 3. Truncar longitud para mejorar rendimiento ===
    abstracts = [ab[:truncate_len] for ab in abstracts]
    print(f" Cada abstract se truncó a un máximo de {truncate_len} caracteres.\n")

    # === 4. Mostrar información general ===
    n = len(abstracts)
    num_pairs = n * (n - 1) // 2
    print(f" Total de comparaciones a realizar por algoritmo: {num_pairs:,}\n")

    # === 5. Calcular similitudes ===
    results = compute_all_similarities(abstracts)

    # === 6. Guardar resultados ===
    os.makedirs(output_dir, exist_ok=True)
    excel_path = save_similarity_matrices(results)
    print(f" Resultados guardados en: {excel_path}")


    # === 7. Generar heatmaps ===
    for name, (matrix, labels) in results.items():
        safe_name = name.replace(" ", "_")
        out_png = os.path.join(output_dir, f"{safe_name}_heatmap.png")
        plot_heatmap(matrix, [f"A{i}" for i in range(len(labels))], title=name, out_path=out_png)
        plot_top_similar_heatmap(matrix, [f"A{i}" for i in range(len(labels))], title=name, out_path=out_png, top_n=10)
        

    print("\n Análisis de similitud completado con éxito.")
    return results

bib_file_path = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Codigo/Requisito1/articulos_unicos.ris"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Requerimiento2 - análisis de similitud textual")
    parser.add_argument("--ris", type=str, required=False, help="Ruta a archivo .ris")
    parser.add_argument("--indices", nargs="+", type=int, help="Indices de artículos a analizar (0-based)")
    parser.add_argument("--out", type=str, default="Requisito2_outputs", help="Directorio salida")
    args = parser.parse_args()

    # Si el usuario no pasa --ris, usamos la ruta por defecto
    ris_path = args.ris if args.ris else bib_file_path

    main_from_ris(ris_path, indices=args.indices, output_dir=args.out)


