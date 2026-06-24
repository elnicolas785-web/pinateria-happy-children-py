from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import datetime
import time 
import threading
from routes import clientes_bp

from models import Cliente, Venta
from extensions import db, employee_required
from .mailer import send_styled_email
from .pdf_utils import generar_recibo_pdf

@clientes_bp.route('/')
@employee_required
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=None, readonly=False)

@clientes_bp.route('/editar/<int:id>')
@employee_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=cliente, readonly=False)

@clientes_bp.route('/ver/<int:id>')
@employee_required
def ver_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=cliente, readonly=True)

@clientes_bp.route('/cambiarEstado/<int:id>')
@employee_required
def cambiar_estado(id):
    cliente = Cliente.query.get_or_404(id)
    cliente.estado = 'Inactivo' if cliente.estado == 'Activo' else 'Activo'
    db.session.commit()
    flash('Estado del cliente actualizado.', 'success')
    return redirect(url_for('clientes.listar_clientes'))

@clientes_bp.route('/guardar', methods=['POST'])
@employee_required
def guardar():
    id_cliente = request.form.get('id_cliente')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    tipo_doc = request.form.get('tipo_documento')
    num_doc = request.form.get('numero_documento')
    email = request.form.get('email')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    estado = request.form.get('estado', 'Activo')

    try:
        if id_cliente:
            cliente = Cliente.query.get(id_cliente)
            if cliente:
                cliente.nombres = nombres
                cliente.apellidos = apellidos
                cliente.tipo_documento = tipo_doc
                cliente.numero_documento = num_doc
                cliente.email = email
                cliente.telefono = telefono
                cliente.direccion = direccion
                cliente.estado = estado
                flash('Cliente actualizado correctamente.', 'success')
        else:
            ultimo_cliente = Cliente.query.order_by(Cliente.id_cliente.desc()).first()
            if ultimo_cliente and ultimo_cliente.codigo:
                try:
                    numero_actual = int(ultimo_cliente.codigo.replace('CLI', ''))
                    nuevo_numero = numero_actual + 1
                except:
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            nuevo_codigo = f"CLI{str(nuevo_numero).zfill(3)}"
            nuevo_cliente = Cliente(
                codigo=nuevo_codigo, 
                nombres=nombres,
                apellidos=apellidos,
                tipo_documento=tipo_doc,
                numero_documento=num_doc,
                email=email,
                telefono=telefono,
                direccion=direccion,
                estado='Activo',
                fecha_registro=datetime.date.today()
            )
            db.session.add(nuevo_cliente)
            flash(f'Cliente creado con código {nuevo_codigo}.', 'success')
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('Ocurrió un error al guardar el cliente.', 'danger')

    return redirect(url_for('clientes.listar_clientes'))

@clientes_bp.route('/buscar', methods=['GET'])
@employee_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        clientes = Cliente.query.filter(
            db.or_(
                Cliente.nombres.ilike(f'%{busqueda}%'),
                Cliente.apellidos.ilike(f'%{busqueda}%'),
                (Cliente.nombres + ' ' + Cliente.apellidos).ilike(f'%{busqueda}%'),
                Cliente.numero_documento.ilike(f'%{busqueda}%'),
                Cliente.codigo.ilike(f'%{busqueda}%')
            )
        ).order_by(Cliente.fecha_registro.desc()).all()
    else:
        clientes = Cliente.query.order_by(Cliente.fecha_registro.desc()).all()
        
    return render_template('clientes.html', listaClientes=clientes, cliente=None, readonly=False)

def enviar_publicidad_async_thread(app):
    """Función de fondo para enviar correos de publicidad masiva usando API de Brevo."""
    with app.app_context():
        print("[BULK EMAIL] Iniciando envío de correos masivos en segundo plano...")
        try:
            clientes = Cliente.query.filter_by(estado='Activo').all()
            clientes_con_correo = [c for c in clientes if c.email]
            
            if not clientes_con_correo:
                print("[BULK EMAIL] No hay clientes activos con correos para enviar.")
                return

            enviados = 0
            errores = 0
            
            print(f"[BULK EMAIL] Se enviarán correos a {len(clientes_con_correo)} clientes.")

            for cliente in clientes_con_correo:
                print(f"[BULK EMAIL] Enviando correo a: {cliente.nombres} ({cliente.email})")
                try:
                    ultima_venta = Venta.query.filter_by(id_cliente=cliente.id_cliente).order_by(Venta.fecha_venta.desc()).first()
                    
                    items_recibo = []
                    total_recibo = 0
                    adjuntos = []
                    
                    if ultima_venta:
                        total_recibo = ultima_venta.total
                        for detalle in ultima_venta.detalles_venta.all():
                            items_recibo.append({
                                'nombre': detalle.producto.nombre if detalle.producto else "Producto",
                                'cantidad': detalle.cantidad,
                                'precio': float(detalle.precio_unitario),
                                'subtotal': float(detalle.subtotal)
                            })
                        pdf_data = generar_recibo_pdf(ultima_venta)
                        adjuntos.append((f"Recibo_{ultima_venta.numero_factura}.pdf", "application/pdf", pdf_data))

                    asunto = "🎈 ¡Novedades y sorpresas en Happy Children!"
                    titulo = f"¡Hola, {cliente.nombres}!"
                    mensaje_body = f"""
                    En <strong>Happy Children</strong> queremos que tus celebraciones sean mágicas. 
                    Tenemos nuevas piñatas personalizadas, globos y todo lo que necesitas para tu fiesta.
                    <br><br>
                    Te recordamos que te esperamos en nuestra tienda física para asesorarte con la mejor decoración.
                    """
                    
                    if ultima_venta:
                        mensaje_body += f"<p>Adjunto a este correo encontrarás el recibo de tu última compra (<b>{ultima_venta.numero_factura}</b>) para tu control personal.</p>"
                    else:
                        mensaje_body += """
                        <div style="background-color: #ebf5ff; border-left: 4px solid #1E88E5; padding: 15px; margin: 20px 0; border-radius: 8px;">
                            <p style="margin: 0; font-weight: bold; color: #1565C0;">🎁 ¡Regalo de Bienvenida!</p>
                            <p style="margin: 5px 0 0;">Muestra este correo en tu primera compra y recibe un <strong>10% de descuento</strong>.</p>
                        </div>
                        """

                    info_cliente = {
                        'num_pedido': ultima_venta.numero_factura if ultima_venta else 'N/A',
                        'fecha': ultima_venta.fecha_venta.strftime('%Y-%m-%d') if ultima_venta else 'N/A',
                        'cliente': f"{cliente.nombres} {cliente.apellidos}",
                        'documento': cliente.numero_documento
                    }

                    # Usar API HTTP de Brevo (sin conexión SMTP)
                    exito = send_styled_email(
                        recipient=cliente.email,
                        subject=asunto,
                        title=titulo,
                        body_text=mensaje_body,
                        items=items_recibo,
                        total=total_recibo,
                        attachments=adjuntos,
                        client_info=info_cliente if ultima_venta else None
                    )
                    
                    if exito:
                        enviados += 1
                        print(f"[BULK EMAIL] Correo enviado con éxito a {cliente.email}")
                    else:
                        errores += 1
                        print(f"[BULK EMAIL] Error al enviar correo a {cliente.email}")
                    
                    time.sleep(1.5)
                    
                except Exception as e:
                    print(f"[BULK EMAIL] Error procesando cliente {cliente.email}: {e}")
                    errores += 1
                        
            print(f"[BULK EMAIL] Proceso finalizado. Enviados: {enviados}, Errores: {errores}")
        except Exception as e:
            print(f"[BULK EMAIL] Error general en el envío asíncrono: {e}")
        finally:
            db.session.remove()

@clientes_bp.route('/enviar-publicidad-masiva')
@employee_required
def enviar_publicidad():
    """Inicia el envío masivo de correos en segundo plano."""
    clientes_activos = Cliente.query.filter_by(estado='Activo').all()
    clientes_con_correo = [c for c in clientes_activos if c.email]
    
    if not clientes_con_correo:
        flash('No hay clientes activos con correos electrónicos registrados.', 'warning')
        return redirect(url_for('clientes.listar_clientes'))

    app = current_app._get_current_object()
    hilo = threading.Thread(target=enviar_publicidad_async_thread, args=(app,))
    hilo.daemon = True
    hilo.start()

    flash(f'El envío masivo a {len(clientes_con_correo)} clientes ha comenzado en segundo plano.', 'info')
    return redirect(url_for('clientes.listar_clientes'))
