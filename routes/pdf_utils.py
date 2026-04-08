import io
import os
import datetime
from flask import current_app
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

def generar_recibo_pdf(obj):
    """
    Genera un PDF del recibo para una Venta o Pedido, idéntico a la Imagen 2.
    :param obj: Instancia de Venta o Pedido
    :return: Bytes del PDF
    """
    buffer = io.BytesIO()
    # Usamos un tamaño de página un poco más angosto para que parezca recibo de punto de venta si se desea, 
    # pero mantendremos letter para consistencia, ajustando márgenes.
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=70, 
        leftMargin=70, 
        topMargin=40, 
        bottomMargin=40
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # --- ESTILOS ---
    company_name_style = ParagraphStyle(
        'CompanyName', parent=styles['Heading1'], alignment=TA_CENTER, 
        fontSize=22, textColor=colors.HexColor('#1565C0'), fontName='Helvetica-Bold', spaceAfter=2
    )
    slogan_style = ParagraphStyle(
        'Slogan', parent=styles['Normal'], alignment=TA_CENTER, 
        fontSize=10, textColor=colors.gray, fontName='Helvetica', spaceAfter=2
    )
    nit_style = ParagraphStyle(
        'NIT', parent=styles['Normal'], alignment=TA_CENTER, 
        fontSize=9, textColor=colors.gray, fontName='Helvetica', spaceAfter=15
    )
    label_style = ParagraphStyle(
        'Label', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold'
    )
    value_style = ParagraphStyle(
        'Value', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT
    )
    blue_bar_style = ParagraphStyle(
        'BlueBar', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#1565C0'), 
        fontName='Helvetica-Bold', leftIndent=10
    )
    total_label_style = ParagraphStyle(
        'TotalLabel', parent=styles['Normal'], fontSize=16, fontName='Helvetica-Bold'
    )
    total_value_style = ParagraphStyle(
        'TotalValue', parent=styles['Normal'], fontSize=18, fontName='Helvetica-Bold', alignment=TA_RIGHT
    )
    thanks_style = ParagraphStyle(
        'Thanks', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, textColor=colors.gray, spaceBefore=20
    )
    url_style = ParagraphStyle(
        'URL', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=colors.gray
    )

    # --- 1. CABECERA (LOGO Y NOMBRE) ---
    logo_path = os.path.join(current_app.root_path, 'static', 'images', 'logo_happychildren.jpg')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=80, height=80)
        elements.append(img)
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("HAPPY CHILDREN", company_name_style))
    elements.append(Paragraph("La Mejor Piñatería 🪅", slogan_style))
    elements.append(Paragraph("NIT: 123.456.789-0", nit_style))
    
    # Línea punteada superior
    elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey, dash=[2, 2]))
    elements.append(Spacer(1, 15))

    # --- 2. INFORMACIÓN DEL CLIENTE/PEDIDO ---
    is_pedido = hasattr(obj, 'numero_pedido')
    num_doc_val = obj.numero_pedido if is_pedido else obj.numero_factura
    fecha_val = obj.fecha_pedido if is_pedido else obj.fecha_venta
    cliente_nombre = f"{obj.cliente.nombres} {obj.cliente.apellidos}" if obj.cliente else "Cliente General"
    doc_identidad = obj.cliente.numero_documento if obj.cliente else "N/A"

    info_data = [
        [Paragraph("<b>No. Pedido:</b>", label_style), Paragraph(num_doc_val, value_style)],
        [Paragraph("<b>Fecha:</b>", label_style), Paragraph(fecha_val.strftime('%Y-%m-%d'), value_style)],
        [Paragraph("<b>Cliente:</b>", label_style), Paragraph(cliente_nombre, value_style)],
        [Paragraph("<b>Documento:</b>", label_style), Paragraph(doc_identidad, value_style)],
    ]
    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # --- 3. BARRA AZUL DE DETALLES ---
    # Simulamos el cuadro azul con una tabla de una sola celda
    detail_bar_data = [[Paragraph("📍 Detalles de Envío y Pago:", blue_bar_style)]]
    detail_bar_table = Table(detail_bar_data, colWidths=[450])
    detail_bar_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f1f8ff')),
        ('BOX', (0, 0), (0, 0), 0.5, colors.HexColor('#e1effe')),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, 0), (0, 0), 8),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    elements.append(detail_bar_table)
    elements.append(Spacer(1, 20))

    # --- 4. TABLA DE PRODUCTOS ---
    # Línea sólida gruesa antes de los encabezados
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.black))
    
    # Encabezados en mayúsculas
    data = [['DESCRIPCIÓN', 'CANT', 'TOTAL']]
    
    detalles = obj.detalles.all() if is_pedido else obj.detalles_venta.all()
    for d in detalles:
        data.append([
            d.producto.nombre.upper() if d.producto else "PRODUCTO",
            str(d.cantidad),
            f"${float(d.subtotal):,.2f}"
        ])
    
    products_table = Table(data, colWidths=[280, 80, 90])
    products_table.setStyle(TableStyle([
        # Estilo Encabezados
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'), # CANT centrado
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'), # TOTAL derecha
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
        # Estilo Filas
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        # Línea sólida después de encabezados
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(products_table)
    
    # Línea punteada final de la tabla
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey, dash=[2, 2]))
    elements.append(Spacer(1, 25))

    # --- 5. TOTAL ---
    total_data = [[Paragraph("TOTAL A PAGAR:", total_label_style), Paragraph(f"${float(obj.total):,.2f}", total_value_style)]]
    total_table = Table(total_data, colWidths=[250, 200])
    total_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(total_table)

    # --- 6. FOOTER ---
    elements.append(Paragraph("¡Gracias por su compra!", thanks_style))
    elements.append(Paragraph("www.happychildren.com", url_style))
    
    # Construir PDF
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
