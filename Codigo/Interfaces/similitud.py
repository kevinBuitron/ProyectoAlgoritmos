import streamlit as st
import tempfile
import os
import pandas as pd
import sys

# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importar funciones desde tus módulos
from Requisito2.algoritmos_similitud import (
    jaccard_similitud, dice_coefficient, normalized_levenshtein, tfidf_cosine_similarity, normalize_text
)
from Requisito2.modelos_IA import sbert_cosine_similarity, save_similarity_matrices
from Requisito2.evaluacion_resultados import build_pair_indices, pair_results_to_matrix, plot_heatmap, plot_top_similar_heatmap

# Si tienes un parser RIS (Requisito3), intenta importarlo — si no, permitimos subir CSV/TSV con abstracts.
try:
    from Requisito3.analizar_abstracts import parse_large_ris
except Exception:
    load_ris = None

# Ruta por defecto (igual que en tus scripts)
DEFAULT_RIS_PATH = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Codigo/Requisito1/articulos_unicos.ris"

def extract_abstracts_from_ris_text(ris_text):
    """
    Lectura sencilla: buscar líneas que empiezan por 'AB  -' o 'A1  -'...
    Devuelve lista de abstracts en el orden de aparición y lista de títulos (si existen).
    """
    abstracts = []
    titles = []
    current_ab = []
    current_title = None
    in_record = False

    for line in ris_text.splitlines():
        if line.startswith("TY  -"):
            in_record = True
            current_ab = []
            current_title = None
        elif line.startswith("ER  -"):
            in_record = False
            abstracts.append(" ".join(current_ab).strip())
            titles.append(current_title if current_title else f"A{len(abstracts)-1}")
        elif in_record:
            if line.startswith("AB  -"):
                current_ab.append(line.split(" - ",1)[1].strip())
            if line.startswith("TI  -") or line.startswith("T1  -"):
                current_title = line.split(" - ",1)[1].strip()
    return abstracts, titles

def compute_pairwise_classics(abstracts, pair_idxs):
    """
    Calcula Jaccard, Dice y Levenshtein por pares (devuelve dicts (i,j)->sim).
    """
    jac_pairs = {}
    dice_pairs = {}
    lev_pairs = {}
    # Pre-tokenizar para Jaccard/Dice
    tokenized = [set(normalize_text(ab)) for ab in abstracts]
    for i,j in pair_idxs:
        # Jaccard
        inter = tokenized[i].intersection(tokenized[j])
        union = tokenized[i].union(tokenized[j])
        jac = len(inter)/len(union) if union else 0.0
        jac_pairs[(i,j)] = float(jac)
        # Dice
        total = len(tokenized[i]) + len(tokenized[j])
        dice_val = (2 * len(inter)) / total if total > 0 else 0.0
        dice_pairs[(i,j)] = float(dice_val)
        # Levenshtein (normalized_levenshtein espera strings)
        lev_pairs[(i,j)] = float(normalized_levenshtein(abstracts[i], abstracts[j]))
    return jac_pairs, dice_pairs, lev_pairs

def similitud_view():
    st.title("🔎 Requerimiento 2 — Análisis de similitud textual")
    st.write("Selecciona o sube un archivo RIS (o pega abstracts) y elige los artículos a comparar. Se ejecutan 4 algoritmos clásicos y 2 de IA (SBERT).")

    # === Cargar archivo RIS por defecto ===
    if not os.path.exists(DEFAULT_RIS_PATH):
        st.error(f"No se encontró el archivo por defecto:\n{DEFAULT_RIS_PATH}")
        if st.button("🏠 Volver al Home"):
            st.session_state.current_view = "home"
        return

    try:
        with open(DEFAULT_RIS_PATH, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except Exception as e:
        st.error(f"Error al leer el archivo por defecto: {e}")
        if st.button("🏠 Volver al Home"):
            st.session_state.current_view = "home"
        return

    # === Extraer abstracts y títulos del RIS ===
    abstracts, titles = extract_abstracts_from_ris_text(raw_text)

    if not abstracts:
        st.warning("El archivo RIS no contiene abstracts detectables (líneas con 'AB  -').")
        if st.button("🏠 Volver al Home"):
            st.session_state.current_view = "home"
        return

    st.markdown(f"**Abstracts cargados:** {len(abstracts)}")

    # Mostrar lista y permitir selección múltiple
    show_table = st.checkbox("Mostrar lista de títulos / abstracts (tabla)")
    if show_table:
        df_view = pd.DataFrame({
            "idx": list(range(len(abstracts))),
            "title": titles,
            "abstract_preview": [a[:200] for a in abstracts]
        })
        st.dataframe(df_view)

    selected = st.multiselect(
        "Selecciona 2 o más artículos (por índice) para analizar:",
        options=list(range(len(abstracts))),
        format_func=lambda x: f"{x} - {titles[x]}",
        default=[0, 1] if len(abstracts) > 1 else [0]
    )
    
    if len(selected) < 2:
        st.warning("Selecciona al menos 2 artículos.")
    else:
        # Opciones de preprocesamiento
        sample_truncate = st.number_input("Truncar abstracts a N caracteres (0 = sin truncar):", min_value=0, value=1000)
        abstracts_sel = [abstracts[i][:sample_truncate] if sample_truncate>0 else abstracts[i] for i in selected]
        labels = [f"A{idx}" for idx in selected]

        st.markdown("### ▶ Ejecutar algoritmos de similitud")
        if st.button("Calcular similitudes"):
            with st.spinner("Calculando similitudes..."):
                n = len(abstracts_sel)
                pair_idxs = build_pair_indices(n)

                # 1) Clásicos por pares: Jaccard, Dice, Levenshtein
                jac_pairs, dice_pairs, lev_pairs = compute_pairwise_classics(abstracts_sel, pair_idxs)

                # 2) TF-IDF Cosine (matriz completa)
                tfidf_mat = tfidf_cosine_similarity(abstracts_sel)

                # 3) SBERT Cosine (modelo IA)
                sbert_mat = sbert_cosine_similarity(abstracts_sel)

                # Convertir pares a matrices
                lev_mat = pair_results_to_matrix(lev_pairs, n)
                jac_mat = pair_results_to_matrix(jac_pairs, n)
                dice_mat = pair_results_to_matrix(dice_pairs, n)

                results = {
                    "Levenshtein": (lev_mat, labels),
                    "Jaccard": (jac_mat, labels),
                    "Dice": (dice_mat, labels),
                    "TFIDF_Cosine": (tfidf_mat, labels),
                    "SBERT_Cosine": (sbert_mat, labels)
                }

                st.success("Cálculo completado ✅")

                # Mostrar matrices y permitir descargar
                for name, (mat, lab) in results.items():
                    st.subheader(name)
                    dfm = pd.DataFrame(mat, index=lab, columns=lab)
                    st.dataframe(dfm.style.format("{:.4f}"))
                    # explicación paso a paso (ver sección explicativa abajo)
                    if st.expander(f"Mostrar explicación matemática y algorítmica de {name}", expanded=False):
                        show_algorithm_explanation(name)

                # Guardar resultados en Excel usando save_similarity_matrices (tu implementación)
                output_excel = save_similarity_matrices(results)
                st.markdown(f"Resultados guardados en Excel: `{output_excel}`")

                # Generar y mostrar heatmap (guardado en ruta prescrita por tu módulo)
                for name, (mat, lab) in results.items():
                    # Intentamos usar las funciones de graficado si están disponibles
                    try:
                        # plot_heatmap usa ruta interna; aquí solo mostramos el plot en Streamlit si se genera.
                        out_png = os.path.join(os.path.dirname(output_excel), f"{name}_heatmap.png")
                        plot_heatmap(mat, lab, title=name, out_path=out_png)
                        st.image(out_png, caption=f"Heatmap - {name}")
                    except Exception as e:
                        st.write(f"No fue posible generar/mostrar heatmap para {name}: {e}")

                # Ofrecer descarga del Excel
                with open(output_excel, "rb") as f:
                    btn = st.download_button("⬇️ Descargar matrices (Excel)", data=f, file_name=os.path.basename(output_excel))

    if st.button("🏠 Volver al Home"):
        st.session_state.current_view = "home"


# ---------- Explicaciones matemáticas (mostradas en UI) ----------
def show_algorithm_explanation(name):
    """
    Muestra la explicación paso a paso para cada algoritmo.
    (Texto explicativo exhaustivo — suficiente para tu informe)
    """
    if name == "Levenshtein":
        st.write("""
**Distancia de Levenshtein (Edición)** — explicación paso a paso:

1. *Definición*: la distancia de Levenshtein entre cadenas `a` y `b` es el número mínimo de operaciones (inserción, borrado, sustitución) necesarias para convertir `a` en `b`.
2. *DP (programación dinámica)*:
   - Construimos una matriz `dp` de tamaño (n+1) x (m+1) donde `n = len(a)`, `m = len(b)`.
   - `dp[i][0] = i` (coste de borrar i caracteres), `dp[0][j] = j` (coste de insertar j caracteres).
   - Recurrencia: 
     `dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)` donde `cost = 0` si `a[i-1]==b[j-1]` sino `1`.
   - Al final `dp[n][m]` es la distancia.
3. *Normalización* (para convertir a similitud entre 0 y 1): usamos `sim = 1 - dist / max(len(a), len(b))`.
   - Si `a==b` => `sim = 1.0`.
   - Si cadenas muy distintas, `sim` se aproxima a 0.
4. *Complejidad*: O(n*m) tiempo y O(n*m) memoria (se puede optimizar a O(min(n,m)) en memoria).
""")
    elif name == "Jaccard":
        st.write("""
**Similitud de Jaccard (nivel token)** — explicación paso a paso:

1. *Definición*: para dos conjuntos A, B:
   `J(A,B) = |A ∩ B| / |A ∪ B|`
2. *Preprocesamiento*:
   - Tokenizamos texto (función `normalize_text`) → tokens alfanuméricos normalizados.
   - Convertimos a conjuntos para eliminar duplicados de tokens por documento.
3. *Cálculo*:
   - Intersección: tokens comunes.
   - Unión: tokens totales únicos.
   - Si ambos conjuntos vacíos, definimos similitud = 1.0 (caso especial).
4. *Interpretación*: J=1 → conjuntos idénticos; J=0 → sin tokens comunes.
5. *Complejidad*: O(|A| + |B|) promedio (para construir sets y calcular inter/union).
""")
    elif name == "Dice":
        st.write("""
**Coeficiente de Sørensen–Dice (nivel token)** — explicación paso a paso:

1. *Definición*: `D(A,B) = 2 * |A ∩ B| / (|A| + |B|)` donde A,B son multisets o sets de tokens.
2. *Relación con Jaccard*: es otra medida de solapamiento; por ejemplo para conjuntos pequeños puede enfatizar coincidencias.
3. *Cálculo*:
   - Igual que Jaccard: tokenizar, formar sets, calcular intersección e insertar en la fórmula.
4. *Interpretación*: valores en [0,1], donde 1 indica coincidencia total.
""")
    elif name == "TFIDF_Cosine":
        st.write("""
**Similitud Coseno sobre vectores TF-IDF** — explicación paso a paso:

1. *Vectorización TF-IDF*:
   - Construimos la matriz `X` de tamaño (n_docs x n_features) con `TF-IDF(d, t) = TF(d,t) * IDF(t)`.
   - `TF(d,t)` = frecuencia (o frecuencia normalizada) del término `t` en documento `d`.
   - `IDF(t) = log(N / (1 + df_t))` donde `df_t` es el número de documentos que contienen `t`.
2. *Producto interno y coseno*:
   - Para vectores `v_i` y `v_j` (filas de X): `cos(v_i, v_j) = (v_i · v_j) / (||v_i|| * ||v_j||)`.
   - Resultado en [-1,1], pero TF-IDF produce vectores no negativos => rango [0,1].
3. *Propiedades*:
   - Captura similitud temática; robusto a longitud del documento por la normalización.
   - Depende del vocabulario y del preprocesamiento (stopwords, n-grams).
4. *Complejidad*: vectorización O(N * V) aproximadamente, cómputo de similitud matricial O(n^2 * d) para d dimensión.
""")
    elif name == "SBERT_Cosine":
        st.write("""
**SBERT (Sentence-BERT) + Cosine** — explicación paso a paso:

1. *Embeddings de oraciones*:
   - SBERT encadena una arquitectura Transformer que produce un embedding fijo por texto.
   - Modelo preentrenado (ej. `all-MiniLM-L6-v2`) transforma cada abstract `t` a un vector `e_t` de dimensión `d` (normalizado si lo requiere).
2. *Similitud por coseno*:
   - Igual que con TF-IDF: `sim(e_i, e_j) = (e_i · e_j) / (||e_i|| * ||e_j||)`.
   - Si el embedding se normaliza (unit norm), entonces `cos` es simplemente el producto punto y está en [-1,1] (usualmente en [0,1] para modelos semánticos).
3. *Ventaja*: captura semántica y parafraseo mejor que TF-IDF; maneja sinónimos y estructuras complejas.
4. *Coste*: inferencia del modelo (CPU/GPU) — tradeoff entre precisión y costo computacional.
""")
    else:
        st.write("Explicación no disponible.")
