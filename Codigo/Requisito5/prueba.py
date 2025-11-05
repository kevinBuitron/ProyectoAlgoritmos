import os
import sys
from collections import Counter

# Agregar la carpeta raíz al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Requisito3.analizar_abstracts import parse_large_ris

def obtener_paises_unicos_cy(archivo_ris):
    """
    Extrae los valores únicos del campo CY (país) y su frecuencia del archivo RIS.
    
    Args:
        archivo_ris: Ruta al archivo RIS
    
    Returns:
        Counter con los valores únicos y su frecuencia
    """
    print(f"Leyendo archivo RIS: {archivo_ris}")
    entries = parse_large_ris(archivo_ris)
    
    print(f"Total de registros encontrados: {len(entries)}")
    
    # Extraer todos los valores del campo CY
    paises = []
    for entry in entries:
        cy_value = entry.get("CY")
        if cy_value:
            # Si es una lista (múltiples valores), agregar todos
            if isinstance(cy_value, list):
                paises.extend([p.strip() for p in cy_value if p.strip()])
            else:
                # Si es un string, agregarlo directamente
                pais = str(cy_value).strip()
                if pais:
                    paises.append(pais)
    
    # Contar frecuencia de cada país único
    frecuencia_paises = Counter(paises)
    
    return frecuencia_paises

if __name__ == "__main__":
    # Ruta al archivo RIS
    archivo_ris = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "Requisito1",
        "articulos_unicos.ris"
    )
    
    # Obtener países únicos y su frecuencia
    frecuencia_paises = obtener_paises_unicos_cy(archivo_ris)
    
    # Imprimir resultados
    print("\n" + "="*60)
    print("VALORES ÚNICOS DEL CAMPO CY (PAÍS) Y SU FRECUENCIA")
    print("="*60)
    
    if frecuencia_paises:
        # Ordenar por frecuencia descendente
        paises_ordenados = sorted(frecuencia_paises.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\nTotal de países únicos encontrados: {len(frecuencia_paises)}")
        print(f"Total de registros con campo CY: {sum(frecuencia_paises.values())}\n")
        
        print(f"{'País':<40} {'Frecuencia':<15}")
        print("-" * 60)
        
        for pais, frecuencia in paises_ordenados:
            print(f"{pais:<40} {frecuencia:<15}")
    else:
        print("\nNo se encontraron valores en el campo CY.")

