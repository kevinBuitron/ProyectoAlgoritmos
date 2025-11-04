from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

def exportar_pdf(imagenes, output_path="C:/2025-2/day/Proyecto Final-K/Proyecto Final/Datos/Requerimiento5/analisis_visual.pdf"):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph("<b>Análisis Visual de la Producción Científica</b>", styles['Title']))
    elementos.append(Spacer(1, 20))

    for nombre, ruta in imagenes.items():
        elementos.append(Paragraph(f"<b>{nombre}</b>", styles['Heading2']))
        elementos.append(Image(ruta, width=500, height=300))
        elementos.append(Spacer(1, 20))

    doc.build(elementos)
    print(f" PDF exportado: {output_path}")
    return output_path
