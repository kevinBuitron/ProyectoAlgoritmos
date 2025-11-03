from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx
import os
import sys
from tqdm import tqdm
import pandas as pd

# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Requisito3.palabras import keywords
from Requisito3.interpretacion_visual import plot_bar_chart, generate_wordcloud
from Requisito3.analizar_abstracts import load_ris, count_keywords, extract_new_terms

# Paso 6: Guardar resultados en un archivo Excel
def guardar_keywords_en_excel(keyword_data, output_path):
    df = pd.DataFrame(keyword_data)
    df = df.sort_values(by=["Categoría", "Frecuencia"], ascending=[True, False])
    df.to_excel(output_path, index=False)

# Paso 7: Integrar todo el flujo
def main(bib_file_path):
    try:
        # Cargar abstracts
        abstracts = load_ris(bib_file_path)
        
        if not abstracts:
            print("Advertencia: No se encontraron abstracts en el archivo.")
            print("Verifica que los campos 'AB' existan en las entradas .ris")
            return
        
        # Contar palabras clave
        keyword_data, keyword_counts = count_keywords(abstracts, keywords)

        # Descubrimiento de nuevas palabras
        new_terms = extract_new_terms(abstracts, keywords, top_n=15)

        # Convertir a DataFrame
        df_new_terms = pd.DataFrame(new_terms, columns=["Término", "Frecuencia"])
        
        if not keyword_counts:
            print("Advertencia: No se encontraron coincidencias con las palabras clave.")
            print("Verifica que los abstracts contengan los términos buscados.")
            return
        
        # Mostrar resultados
        print("\nFrecuencias de Palabras Clave:")
        for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{keyword}: {count}")

        # Guardar resultados en Excel
        output_excel = os.path.join(ruta_graficos, "frecuencia_keywords_categorizadas.xlsx")
        guardar_keywords_en_excel(keyword_data, output_excel)
        print(f"Archivo Excel guardado en: {output_excel}")

        # Guardar nuevas palabras
        output_excel_nuevas = os.path.join(ruta_graficos, "nuevas_palabras.xlsx")
        df_new_terms.to_excel(output_excel_nuevas, index=False)
        print(f"Nuevas palabras asociadas a terminos guardadas en: {output_excel_nuevas}")

        # Graficar resultados
        plot_bar_chart(keyword_counts)
        generate_wordcloud(output_excel_nuevas)
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    bib_file_path = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Codigo/Requisito1/articulos_unicos.ris"
    ruta_graficos = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento3"
    
    # Ejecutar el flujo principal
    main(bib_file_path)
    print(f"Análisis de palabras clave completado. Gráficos guardados en {ruta_graficos}.")