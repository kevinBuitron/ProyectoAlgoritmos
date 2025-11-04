import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generar_mapa_calor(df):
    """
    df debe tener columnas ['Autor', 'Pais', 'Cantidad']
    """
    # Asegurar que existe columna de país
    if "CY" not in df.columns:
        raise ValueError("No se encontró la columna 'CY' (país del primer autor) en el DataFrame.")

    # Contar artículos por país
    conteo = df["CY"].dropna().value_counts().reset_index()
    conteo.columns = ["País", "Cantidad"]

    # Crear mapa coroplético
    fig = px.choropleth(
        conteo,
        locations="País",
        locationmode="country names",
        color="Cantidad",
        hover_name="País",
        color_continuous_scale="Viridis",
        title="Distribución geográfica de artículos por país"
    )

    # Exportar a imagen
    output_path = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/mapa_calor_geografico.png"
    fig.write_image(output_path, scale=2)
    print(f"Mapa de calor guardado en: {output_path}")

    return output_path

def generar_nube_palabras(texto_completo):
    wc = WordCloud(width=1200, height=600, background_color="white").generate(texto_completo)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/nube_palabras.png", dpi=300)
    plt.close()
    return "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/nube_palabras.png"

def generar_linea_tiempo(df,top_n=20):
    """
    Genera una línea temporal de publicaciones por año y revista.
    Usa las columnas 'PY' (año) y 'JO' (revista) del DataFrame RIS original.
    """

    # Renombrar columnas para mantener consistencia
    df = df.rename(columns={"PY": "Año", "JO": "Revista"})

    # Limpiar datos
    df = df.dropna(subset=["Año", "Revista"])
    df["Año"] = df["Año"].astype(str).str.extract(r"(\d{4})")
    df = df.dropna(subset=["Año"])
    df["Año"] = df["Año"].astype(int)

    # Contar publicaciones por revista
    conteo_revistas = df["Revista"].value_counts().nlargest(top_n).index

    # Filtrar solo las más frecuentes
    df_filtrado = df[df["Revista"].isin(conteo_revistas)]

    # Agrupar por año y revista
    conteo = df_filtrado.groupby(["Año", "Revista"]).size().reset_index(name="Cantidad")

    # Crear gráfico
    fig = px.line(
        conteo,
        x="Año",
        y="Cantidad",
        color="Revista",
        markers=True,
        title=f"Línea temporal de publicaciones (Top {top_n} revistas)"
    )

    # Definir ruta de salida
    output_path = "C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/linea_tiempo.png"

    # Guardar o mostrar el gráfico
    try:
        fig.write_image(output_path, scale=2)
        print(f" Línea temporal guardada en: {output_path}")
    except Exception as e:
        print(f" Error exportando el gráfico con Kaleido: {e}")
        print("Mostrando gráfico en pantalla en lugar de exportar.")
        fig.show()

    return output_path