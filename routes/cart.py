from flask import render_template, request, redirect, url_for, session, flash # type: ignore
from routes import cart_bp # type: ignore
from models import Producto, Pedido, DetallePedido, CategoriaProducto, db # type: ignore
from extensions import db # type: ignore
from flask_login import current_user, login_required # type: ignore
import datetime
from .mailer import send_styled_email

@cart_bp.route('/')
@login_required
def ver_carrito():
    # Recuperamos el carrito de la sesión
    carrito = session.get('carrito', [])
    total = sum(item['subtotal'] for item in carrito)
    return render_template('cart.html', carrito=carrito, total=total)

@cart_bp.route('/catalogo')
def catalogo():
    id_categoria = request.args.get('id_categoria')
    if id_categoria:
        productos = Producto.query.filter_by(id_categoria=id_categoria, activo='Activo').all()
    else:
        productos = Producto.query.filter_by(activo='Activo').all()
    categorias = CategoriaProducto.query.all()
    return render_template('catalogo.html', productos=productos, categorias=categorias, categoriaSeleccionada=id_categoria)

@cart_bp.route('/add/<int:id_producto>', methods=['POST'])
@login_required
def add_to_cart(id_producto):
    cantidad = int(request.form.get('cantidad', 1))
    producto = Producto.query.get_or_404(id_producto)
    
    
    if producto.stock_actual < cantidad:
        flash(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}", "warning")
        return redirect(url_for('cart.catalogo'))

    carrito = session.get('carrito', [])
    
    encontrado = False
    for item in carrito:
        if item['id_producto'] == id_producto:
          
            if producto.stock_actual < (item['cantidad'] + cantidad):
                flash(f"No puedes agregar más de las {producto.stock_actual} unidades disponibles.", "warning")
                return redirect(url_for('cart.catalogo'))
            
            item['cantidad'] += cantidad
            item['subtotal'] = item['cantidad'] * float(producto.precio_venta)
            encontrado = True
            break
            
    if not encontrado:
        carrito.append({
            'id_producto': producto.id_producto,
            'nombre': producto.nombre,
            'cantidad': cantidad,
            'precio': float(producto.precio_venta),
            'subtotal': cantidad * float(producto.precio_venta)
        })
        
    session['carrito'] = carrito
    session.modified = True
    flash(f'{producto.nombre} agregado al carrito.', 'success')
    return redirect(url_for('cart.catalogo'))

@cart_bp.route('/increase/<int:id_producto>')
@login_required
def increase(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    carrito = session.get('carrito', [])
    for item in carrito:
        if item['id_producto'] == id_producto:
            if producto.stock_actual > item['cantidad']:
                item['cantidad'] += 1
                item['subtotal'] = item['cantidad'] * float(item['precio'])
            else:
                flash("Límite de stock alcanzado.", "warning")
            break
    session['carrito'] = carrito
    session.modified = True
    return redirect(url_for('cart.ver_carrito'))

@cart_bp.route('/decrease/<int:id_producto>')
@login_required
def decrease(id_producto):
    carrito = session.get('carrito', [])
    for item in carrito:
        if item['id_producto'] == id_producto:
            item['cantidad'] -= 1
            if item['cantidad'] <= 0:
                carrito.remove(item)
            else:
                item['subtotal'] = item['cantidad'] * float(item['precio'])
            break
    session['carrito'] = carrito
    session.modified = True
    return redirect(url_for('cart.ver_carrito'))

@cart_bp.route('/remove/<int:id_producto>')
@login_required
def remove(id_producto):
    carrito = session.get('carrito', [])
    carrito = [item for item in carrito if item['id_producto'] != id_producto]
    session['carrito'] = carrito
    session.modified = True
    return redirect(url_for('cart.ver_carrito'))

@cart_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    carrito = session.get('carrito', [])
    if not carrito:
        flash("El carrito está vacío.", "warning")
        return redirect(url_for('cart.ver_carrito'))
        
    total = sum(item['subtotal'] for item in carrito)
    observaciones = request.form.get('observaciones', '')
    direccion = request.form.get('direccionEntrega', '')
    
    items_para_email = list(carrito)
    
    try:
        # 1. Crear el Pedido
        num_pedido = f"PED-{int(datetime.datetime.now().timestamp() * 1000) % 10000:04d}"
        nuevo_pedido = Pedido(
            numero_pedido=num_pedido,
            fecha_pedido=datetime.datetime.now(),
            estado='Pendiente',
            subtotal=total,
            total=total,
            observaciones=observaciones,
            direccion_entrega=direccion,
         
            id_cliente=current_user.cliente.id_cliente if hasattr(current_user, 'cliente') and current_user.cliente else None
        )
        db.session.add(nuevo_pedido)
        db.session.flush() 

       
        for item in carrito:
            prod = Producto.query.get(item['id_producto'])
            
            if prod:
                # Verificación final de stock antes de confirmar
                if prod.stock_actual < item['cantidad']:
                    db.session.rollback()
                    flash(f"Error: El producto {prod.nombre} ya no tiene stock suficiente.", "danger")
                    return redirect(url_for('cart.ver_carrito'))
                
                # RESTA REAL EN LA BASE DE DATOS
                prod.stock_actual -= item['cantidad']
                
                # Registro del detalle
                detalle = DetallePedido(
                    codigo=f"DET-{num_pedido}-{item['id_producto']}",
                    id_pedido=nuevo_pedido.id_pedido,
                    id_producto=item['id_producto'],
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                    subtotal=item['subtotal']
                )
                db.session.add(detalle)

        # 4. ENVÍO DE RECIBO POR CORREO 
        # Detecta el correo según el tipo de usuario (Cliente o Empleado)
        email_destino = None
        nombre_destino = "Cliente"
        doc_destino = "N/A"
        
        if hasattr(current_user, 'cliente') and current_user.cliente:
            email_destino = current_user.cliente.email
            nombre_destino = f"{current_user.cliente.nombres} {current_user.cliente.apellidos}"
            doc_destino = current_user.cliente.numero_documento
        elif hasattr(current_user, 'email'):
            email_destino = current_user.email
            nombre_destino = f"{current_user.nombres} {current_user.apellidos}"
            doc_destino = getattr(current_user, 'documento_identidad', 'N/A')

        if email_destino:
            try:
                from .pdf_utils import generar_recibo_pdf
                
                asunto = "🎉 ¡Compra Exitosa! - Happy Children"
                titulo = "¡Compra Exitosa!"
                mensaje = f"¡Felicidades <strong>{nombre_destino}</strong>! Tu pedido <strong>{num_pedido}</strong> ha sido recibido con éxito. Estamos preparando todo para que tu celebración sea inolvidable."
                
                # Generar PDF para el nuevo pedido
                pdf_data = generar_recibo_pdf(nuevo_pedido)
                adjuntos = [(f"Recibo_Compra_{num_pedido}.pdf", "application/pdf", pdf_data)]
                
                # Datos para el diseño del recibo en el cuerpo del correo
                info_cliente = {
                    'num_pedido': num_pedido,
                    'fecha': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'cliente': nombre_destino,
                    'documento': doc_destino
                }
                
                send_styled_email(
                    recipient=email_destino,
                    subject=asunto,
                    title=titulo,
                    body_text=mensaje,
                    items=items_para_email,
                    total=total,
                    attachments=adjuntos,
                    client_info=info_cliente
                )
            except Exception as e:
                print(f"Error al enviar correo de compra exitosa: {e}")

        # Guardar cambios 
        db.session.commit()
        session['carrito'] = [] 
        session.modified = True
        
        flash('¡Compra exitosa! El recibo detallado ha sido enviado a tu correo.', 'success')
        return redirect(url_for('cart.compra_exitosa', id_pedido=nuevo_pedido.id_pedido))

    except Exception as e:
        db.session.rollback()
        print(f"Error en Checkout: {str(e)}")
        flash(f"Error al procesar el pedido: {str(e)}", "danger")
        return redirect(url_for('cart.ver_carrito'))

@cart_bp.route('/success/<int:id_pedido>')
@login_required
def compra_exitosa(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    detalles = DetallePedido.query.filter_by(id_pedido=id_pedido).all()
    
    for d in detalles:
        d.producto = Producto.query.get(d.id_producto)
    
    return render_template('success.html', venta=pedido, detalles=detalles) 