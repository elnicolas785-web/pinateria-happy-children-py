from flask import render_template, request, redirect, url_for, session, flash # type: ignore
from routes import cart_bp # type: ignore
from models import Producto, Pedido, DetallePedido, CategoriaProducto, db # type: ignore
from extensions import db # type: ignore
from flask_login import current_user, login_required # type: ignore
import datetime

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
    
    # VALIDACIÓN: Usamos 'stock_actual' como definiste en tu modelo
    if producto.stock_actual < cantidad:
        flash(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}", "warning")
        return redirect(url_for('cart.catalogo'))

    carrito = session.get('carrito', [])
    
    encontrado = False
    for item in carrito:
        if item['id_producto'] == id_producto:
            # Validar que la suma no supere el stock_actual
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
            # Vinculamos al cliente desde el UsuarioCliente logueado
            id_cliente=current_user.cliente.id_cliente if hasattr(current_user, 'cliente') and current_user.cliente else None
        )
        db.session.add(nuevo_pedido)
        db.session.flush() 

        # 2. Descontar STOCK_ACTUAL y crear Detalles
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

        # 3. Guardar cambios definitivos
        db.session.commit()
        session['carrito'] = [] 
        session.modified = True
        
        flash('¡Pedido realizado con éxito! El inventario ha sido actualizado.', 'success')
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