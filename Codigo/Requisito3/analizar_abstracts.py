import re
import unicodedata
from collections import Counter
from tqdm import tqdm

"""
Esta clase analiza archivos RIS grandes, extrayendo campos relevantes como título, autores, palabras clave y resumen.
También permite contar la frecuencia de palabras clave en los abstracts.
"""

def parse_large_ris(file_path):
    """Analiza archivos RIS grandes y devuelve una lista de entradas (diccionarios)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    entries = []
    entry = {}

    for line in tqdm(lines, desc="Analizando entradas"):
        line = line.strip()

        # Fin de una entrada
        if line.startswith("ER  -"):
            if entry:
                entries.append(entry)
                entry = {}
            continue

        # Coincidir con líneas RIS del tipo "XX  - valor"
        match = re.match(r"^([A-Z0-9]{2})  - (.*)", line)
        if match:
            key, value = match.groups()
            key = key.strip()
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('utf-8').strip()

            # Algunos campos pueden repetirse (por ejemplo, AU, KW)
            if key in entry:
                if isinstance(entry[key], list):
                    entry[key].append(value)
                else:
                    entry[key] = [entry[key], value]
            else:
                entry[key] = value

    return entries


def load_ris(file_path):
    """Carga el archivo RIS y extrae los abstracts."""
    entries = parse_large_ris(file_path)

    abstracts = []
    for entry in entries:
        abstract = entry.get("AB")
        if abstract:
            # Si hay varias líneas de abstract (raro, pero posible)
            if isinstance(abstract, list):
                abstract = " ".join(abstract)
            abstracts.append(abstract)

    print(f"\nSe encontraron {len(abstracts)} abstracts en el archivo.")
    print(f"Total de entradas en el archivo: {len(entries)}")

    if not abstracts and len(entries) > 0:
        print("\nDepuración: Mostrando claves de la primera entrada:")
        print(list(entries[0].keys()))

    return abstracts


def count_keywords(abstracts, keywords_dict):
    """Cuenta la frecuencia de palabras clave en los abstracts."""
    keyword_data = []
    keyword_counts = Counter()

    for abstract in abstracts:
        abstract_lower = abstract.lower()
        for category, terms in keywords_dict.items():
            for term, synonyms in terms.items():
                for synonym in synonyms:
                    if synonym.lower() in abstract_lower:
                        found = False
                        for entry in keyword_data:
                            if entry["Término"] == term and entry["Categoría"] == category:
                                entry["Frecuencia"] += 1
                                found = True
                                break
                        if not found:
                            keyword_data.append({
                                "Término": term,
                                "Categoría": category,
                                "Frecuencia": 1
                            })
                        keyword_counts[term] += 1
                        break
    return keyword_data, keyword_counts


def extract_new_terms(abstracts, keywords_dict, top_n=15):
    """
    Extrae términos frecuentes de los abstracts que no estén ya en keywords_dict.
    """
    all_text = " ".join(abstracts).lower()
    words = re.findall(r"\b[a-zA-Z-]+\b", all_text)

    known_terms = {syn.lower() for terms in keywords_dict.values() for syns in terms.values() for syn in syns}

    stopwords = {
        "the","and","of","to","in","for","with","on","by","is","are",
        "an","at","from","this","that","as","we","our","a"
    }

    filtered = [w for w in words if w not in stopwords and w not in known_terms]
    counter = Counter(filtered)
    return counter.most_common(top_n)
