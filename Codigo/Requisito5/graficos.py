import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import imgkit
import plotly.io as pio

def generar_nube_palabras(texto_completo):
    wc = WordCloud(width=1200, height=600, background_color="white").generate(texto_completo)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/nube_palabras.png", dpi=300)
    plt.close()
    return "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/nube_palabras.png"

def generar_mapa_calor(df):
    """
    df debe tener columnas ['Autor', 'Pais', 'Cantidad']
    """
    # Creamos un DataFrame manual con Oxford y su conteo
    data = pd.DataFrame({
        "Ciudad": ["Oxford"],
        "Lat": [51.7520],   # Latitud de Oxford
        "Lon": [-1.2577],   # Longitud de Oxford
        "Cantidad": [1]
    })

    # Creamos un mapa de calor (scatter geo con tamaño o color)
    fig = px.scatter_geo(
        data,
        lat="Lat",
        lon="Lon",
        size="Cantidad",
        color="Cantidad",
        hover_name="Ciudad",
        color_continuous_scale="Viridis",
        projection="natural earth",
        title="Distribución geográfica de artículos — Oxford"
    )

    output_path = ""

    # Mostramos el mapa
    fig.show()

    return output_path


def generar_linea_tiempo(df, top_n=20):
    """
    Genera una línea temporal de publicaciones por año y revista.
    Solo grafica las revistas con frecuencia total >= 3.
    Usa las columnas 'PY' (año) y 'JO' (revista) del DataFrame RIS original.
    """

    # Renombrar columnas para mantener consistencia
    df = df.rename(columns={"PY": "Año", "JO": "Revista"})

    # Limpiar datos
    df = df.dropna(subset=["Año", "Revista"])
    df["Año"] = df["Año"].astype(str).str.extract(r"(\d{4})")
    df = df.dropna(subset=["Año"])
    df["Año"] = df["Año"].astype(int)

    # Contar publicaciones totales por revista
    conteo_total = df["Revista"].value_counts()

    # Filtrar solo las revistas con frecuencia >= 3
    revistas_filtradas = conteo_total[conteo_total >= 3].index

    # Aplicar filtro
    df_filtrado = df[df["Revista"].isin(revistas_filtradas)]

    # Si quieres además limitar al top_n (por si hay muchas)
    if top_n:
        top_revistas = df_filtrado["Revista"].value_counts().nlargest(top_n).index
        df_filtrado = df_filtrado[df_filtrado["Revista"].isin(top_revistas)]

    # Agrupar por año y revista
    conteo = df_filtrado.groupby(["Año", "Revista"]).size().reset_index(name="Cantidad")

    # Crear gráfico solo si hay datos
    if conteo.empty:
        print("No hay revistas con frecuencia >= 3 para graficar.")
        return None

    fig = px.line(
        conteo,
        x="Año",
        y="Cantidad",
        color="Revista",
        markers=True,
        title=f"Línea temporal de publicaciones (revistas con ≥3 artículos)"
    )

    # Mostrar y exportar
    output_path = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/linea_tiempo.png"
    fig.show()
    print(f"Gráfico generado (filtrado por frecuencia ≥ 3): {output_path}")

    return output_path