import os
from flask import current_app
from flask_mail import Message
from extensions import mail

def send_styled_email(recipient, subject, title, body_text, items=None, total=0, attachments=None, client_info=None):
    """
    Envía un correo electrónico con el diseño premium original (Logo grande y degradado)
    e integra el recibo con estilo PDF si hay ítems disponibles.
    """
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient]
    )

    logo_path = os.path.join(current_app.root_path, 'static', 'images', 'logo_happychildren.jpg')
    has_logo = os.path.exists(logo_path)
    if has_logo:
        with current_app.open_resource(logo_path) as fp:
            msg.attach("logo.jpg", "image/jpeg", fp.read(), headers=[['Content-ID', '<logo>']])

    if attachments:
        for filename, content_type, data in attachments:
            msg.attach(filename, content_type, data)

    # Lógica de Recibo Estilo PDF (Aparece si hay items)
    receipt_html = ""
    if items and client_info:
        rows = ""
        for item in items:
            rows += f"""
            <tr style="border-bottom: 1px dashed #ccc;">
                <td style="padding: 10px 0; font-size: 14px;">{item.get('nombre', 'Producto')}</td>
                <td style="padding: 10px 0; text-align: center; font-size: 14px;">{item.get('cantidad', 1)}</td>
                <td style="padding: 10px 0; text-align: right; font-weight: bold; font-size: 14px;">${float(item.get('subtotal', 0)):,.2f}</td>
            </tr>
            """
        
        receipt_html = f"""
        <div style="margin-top: 30px; border: 1px solid #ddd; border-top: 5px solid #1565C0; border-radius: 8px; padding: 20px; background-color: #fff; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #1565C0; margin: 0; font-family: sans-serif; letter-spacing: 2px; font-size: 18px;">RECIBO DE COMPRA</h2>
                <div style="border-top: 1px dashed #ccc; margin: 10px 0;"></div>
            </div>
            
            <table style="width: 100%; font-size: 13px; color: #333; margin-bottom: 15px;">
                <tr>
                    <td style="font-weight: bold; width: 35%;">No. Documento:</td>
                    <td style="text-align: right;">{client_info.get('num_pedido', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold;">Fecha:</td>
                    <td style="text-align: right;">{client_info.get('fecha', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold;">Cliente:</td>
                    <td style="text-align: right;">{client_info.get('cliente', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold;">ID Identidad:</td>
                    <td style="text-align: right;">{client_info.get('documento', 'N/A')}</td>
                </tr>
            </table>

            <div style="background-color: #f1f8ff; padding: 8px 15px; border-radius: 5px; margin-bottom: 15px; border-left: 4px solid #1E88E5;">
                <p style="margin: 0; color: #1565C0; font-weight: bold; font-size: 12px;">📍 Detalles de Envío y Pago:</p>
            </div>

            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 2px solid #333;">
                        <th style="padding: 10px 0; text-align: left; font-size: 11px; color: #666; text-transform: uppercase;">Descripción</th>
                        <th style="padding: 10px 0; text-align: center; font-size: 11px; color: #666; text-transform: uppercase;">Cant</th>
                        <th style="padding: 10px 0; text-align: right; font-size: 11px; color: #666; text-transform: uppercase;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <div style="border-top: 1px dashed #ccc; margin: 15px 0;"></div>
            
            <table style="width: 100%;">
                <tr>
                    <td style="font-size: 16px; font-weight: bold; font-family: sans-serif;">TOTAL A PAGAR:</td>
                    <td style="text-align: right; font-size: 20px; font-weight: bold; color: #000;">${float(total):,.2f}</td>
                </tr>
            </table>
        </div>
        """

    # Template HTML Premium con Encabezado Original Restaurado
    msg.html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            .main-bg {{ background-color: #f4f7f9; padding: 30px 10px; }}
            .container {{
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 15px 45px rgba(0,0,0,0.1);
                border: 1px solid #eee;
            }}
            .header {{
                background: linear-gradient(135deg, #1565C0 0%, #1E88E5 100%);
                padding: 45px 20px;
                text-align: center;
                color: white;
            }}
            .logo-img {{
                max-width: 160px;
                width: 160px;
                height: auto;
                border-radius: 50%;
                border: 6px solid rgba(255,255,255,0.3);
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
                background-color: white;
                margin-bottom: 15px;
            }}
            .content {{
                padding: 40px;
                color: #444;
                line-height: 1.7;
            }}
            .footer {{
                background-color: #f9f9f9;
                padding: 25px;
                text-align: center;
                font-size: 12px;
                color: #999;
                border-top: 1px solid #f0f0f0;
            }}
            .btn {{
                display: inline-block;
                padding: 14px 30px;
                background-color: #1565C0;
                color: white !important;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                margin-top: 30px;
                box-shadow: 0 6px 20px rgba(21, 101, 192, 0.3);
            }}
        </style>
    </head>
    <body class="main-bg">
        <div class="container">
            <div class="header">
                {f'<img src="cid:logo" class="logo-img" alt="Logo">' if has_logo else ''}
                <h1 style="margin: 0; font-size: 26px; font-weight: 300; letter-spacing: 1.5px; text-transform: uppercase;">Happy Children</h1>
            </div>
            
            <div class="content">
                <h2 style="color: #1565C0; margin-top: 0; font-size: 22px;">{title}</h2>
                <div style="font-size: 16px;">
                    {body_text}
                </div>
                
                {receipt_html}
                
                <div style="text-align: center;">
                    <a href="http://127.0.0.1:5000" class="btn">Visitar Tienda en Línea</a>
                </div>
            </div>
            
            <div class="footer">
                <p style="margin: 5px 0; color: #444; font-size: 14px;"><strong>Piñatería Happy Children 🎈</strong></p>
                <p style="margin: 5px 0;">¡Donde la diversión nunca termina!</p>
                <div style="border-top: 1px solid #eee; margin: 15px 0; padding-top: 15px;">
                    <p style="margin: 0; font-size: 10px; color: #bbb;">Este correo fue enviado automáticamente por nuestro sistema de gestión. Por favor no responder.</p>
                    <p style="margin: 5px 0; font-size: 10px;">&copy; 2026 Happy Children | Barranquilla, Colombia</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar email: {str(e)}")
        return False
