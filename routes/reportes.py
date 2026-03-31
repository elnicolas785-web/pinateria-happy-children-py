import io
import os
import datetime
from flask import render_template, make_response, send_file, current_app # type: ignore
from routes import reportes_bp # type: ignore
from models import Venta, Pedido # type: ignore

try:
    from reportlab.lib.pagesizes import letter, landscape # type: ignore
    from reportlab.lib import colors # type: ignore
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image # type: ignore
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT # type: ignore
except ImportError:
    pass

@reportes_bp.route('/ventas/pdf')
def exportar_ventas_pdf():
    ventas = Venta.query.all()
    
    buffer = io.BytesIO()
    pdf_title = f"Reporte de Ventas - {datetime.date.today().strftime('%Y-%m-%d')}"
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(letter), 
        rightMargin=30, 
        leftMargin=30, 
        topMargin=40, 
        bottomMargin=30,
        title=pdf_title,
        author="Happy Children"
    )
    elements = []
    
    styles = getSampleStyleSheet()
    
    slogan_style = ParagraphStyle(
        'Slogan',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        textColor=colors.gray,
        fontSize=10
    )
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1565C0'),
        fontSize=22,
        spaceBefore=20,
        spaceAfter=30
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.dimgray,
        spaceAfter=15
    )
    
    total_style = ParagraphStyle(
        'TotalCol',
        parent=styles['Normal'],
        textColor=colors.HexColor('#ff9800'),
        fontName='Helvetica-Bold',
        fontSize=10
    )
    
    # Header Elements
    logo_path = os.path.join(current_app.root_path, 'static', 'images', 'logo_happychildren.jpg')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=80, height=80)
        elements.append(img)
    
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("¡Donde la diversión nunca termina!", slogan_style))
    elements.append(Paragraph("REPORTE OFICIAL DE VENTAS", title_style))
    
    now_str = datetime.datetime.now().strftime("%a %b %d %H:%M:%S COT %Y")
    elements.append(Paragraph(f"Fecha de Emisión: {now_str}", date_style))
    
    # Table Data
    data = [['ID', 'Factura', 'Cliente', 'Empleado', 'Método', 'Productos', 'Fecha', 'Total']]
    
    for v in ventas:
        cliente_nombre = f"{v.cliente.nombres} {v.cliente.apellidos}" if v.cliente else "Desconocido"
        empleado_nombre = f"{v.empleado.nombres} {v.empleado.apellidos}" if v.empleado else "Desconocido"
        
        cli_str = cliente_nombre[:25] + '...' if len(cliente_nombre) > 25 else cliente_nombre
        emp_str = empleado_nombre[:20] + '...' if len(empleado_nombre) > 20 else empleado_nombre
        
        total_val = v.total if v.total else 0
        total_str = f"${total_val:.2f}"
        
        data.append([
            str(v.id_venta),
            str(v.numero_factura),
            cli_str,
            emp_str,
            str(v.metodo_pago),
            "Sin detalles",
            v.fecha_venta.strftime('%Y-%m-%d') if v.fecha_venta else '',
            Paragraph(total_str, total_style)
        ])
        
    col_widths = [40, 95, 130, 110, 80, 110, 80, 85]
    t = Table(data, colWidths=col_widths)
    
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 12),
        
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=False,
        download_name=f'Reporte_Ventas_{datetime.date.today().strftime("%Y%m%d")}.pdf',
        mimetype='application/pdf'
    )

@reportes_bp.route('/pedidos/pdf')
def exportar_pedidos_pdf():
    # Similar functionality for pedidos but out of scope for the screenshot fix
    # Provided as a simple fallback
    return "Reporte de pedidos pendiente de actualización visual", 200
