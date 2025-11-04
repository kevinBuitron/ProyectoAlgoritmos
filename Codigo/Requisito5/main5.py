import os
import pandas as pd
import sys

# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Requisito5.graficos import generar_linea_tiempo, generar_nube_palabras, generar_mapa_calor
from Requisito5.exportar_pdf import exportar_pdf
from Requisito3.analizar_abstracts import parse_large_ris

def main_requerimiento5():

    # === Simulación === (reemplaza con tu lectura real de .ris o dataset)
    df = parse_large_ris("C:/2025-2/day/Proyecto Final-K/Proyecto Final/Codigo/Requisito1/articulos_unicos.ris")  
    df = pd.DataFrame(df)
    print("\nColumnas disponibles en df:")
    print(df.columns.tolist())

    possible_abstract_cols = ["Abstract", "AB", "abstract", "Resumen"]
    possible_keywords_cols = ["Keywords", "KW", "keywords", "PalabrasClave"]

    abstract_col = next((c for c in possible_abstract_cols if c in df.columns), None)
    keywords_col = next((c for c in possible_keywords_cols if c in df.columns), None)

    texto_completo = " ".join(
        df[abstract_col].dropna().astype(str).tolist()
        + df[keywords_col].dropna().astype(str).tolist()
    )


    # Generar visualizaciones
    #mapa = generar_mapa_calor(df)
    nube = generar_nube_palabras(texto_completo)
    linea = generar_linea_tiempo(df, top_n=20)

    # Exportar PDF
    exportar_pdf({
        #"Mapa de calor geográfico": mapa,
        "Nube de palabras": nube,
        "Línea temporal": linea
    }, output_path="C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/analisis_visual.pdf")

if __name__ == "__main__":
    main_requerimiento5()
