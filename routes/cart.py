from flask import render_template, request, redirect, url_for, session, flash # type: ignore
from routes import cart_bp # type: ignore
from models import Producto, Pedido, DetallePedido, CategoriaProducto # type: ignore
from extensions import db # type: ignore
from flask_login import current_user, login_required # type: ignore
import datetime

@cart_bp.route('/')
@login_required
def ver_carrito():
    # Carrito muy simplificado, usando la sesión de Flask
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
    
    carrito = session.get('carrito', [])
    # Buscar si ya existe
    encontrado = False
    for item in carrito:
        if item['id_producto'] == id_producto:
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
    flash('Producto agregado al carrito')
    return redirect(url_for('cart.catalogo'))

@cart_bp.route('/increase/<int:id_producto>')
@login_required
def increase(id_producto):
    carrito = session.get('carrito', [])
    for item in carrito:
        if item['id_producto'] == id_producto:
            item['cantidad'] += 1
            item['subtotal'] = item['cantidad'] * float(item['precio'])
            break
    session['carrito'] = carrito
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
    return redirect(url_for('cart.ver_carrito'))

@cart_bp.route('/remove/<int:id_producto>')
@login_required
def remove(id_producto):
    carrito = session.get('carrito', [])
    carrito = [item for item in carrito if item['id_producto'] != id_producto]
    session['carrito'] = carrito
    return redirect(url_for('cart.ver_carrito'))

@cart_bp.route('/set/<int:id_producto>', methods=['POST'])
@login_required
def set_quantity(id_producto):
    cantidad = int(request.form.get('cantidad', 1))
    carrito = session.get('carrito', [])
    if cantidad <= 0:
        carrito = [item for item in carrito if item['id_producto'] != id_producto]
    else:
        for item in carrito:
            if item['id_producto'] == id_producto:
                item['cantidad'] = cantidad
                item['subtotal'] = item['cantidad'] * float(item['precio'])
                break
    session['carrito'] = carrito
    return redirect(url_for('cart.ver_carrito'))

@cart_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    carrito = session.get('carrito', [])
    if not carrito:
        return redirect(url_for('cart.ver_carrito'))
        
    total = sum(item['subtotal'] for item in carrito)
    observaciones = request.form.get('observaciones', '')
    direccion = request.form.get('direccionEntrega', '')
    
    # Crear pedido
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
    db.session.flush() # Para obtener el ID
    
    for item in carrito:
        detalle = DetallePedido(
            codigo=f"DET-{num_pedido}-{item['id_producto']}",
            id_pedido=nuevo_pedido.id_pedido,
            id_producto=item['id_producto'],
            cantidad=item['cantidad'],
            precio_unitario=item['precio'],
            subtotal=item['subtotal']
        )
        db.session.add(detalle)
        
    db.session.commit()
    session['carrito'] = [] # Vaciar carrito
    
    flash('Pedido realizado con éxito', 'success')
    return redirect(url_for('cart.compra_exitosa', id_pedido=nuevo_pedido.id_pedido))

@cart_bp.route('/success/<int:id_pedido>')
@login_required
def compra_exitosa(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    detalles = DetallePedido.query.filter_by(id_pedido=id_pedido).all()
    
    for d in detalles:
        d.producto = Producto.query.get(d.id_producto)
    
    # Renderizamos success.html pasando el pedido como 'venta' 
    # (la plantilla ha sido ajustada o será ajustada para usar los atributos de pedido)
    return render_template('success.html', venta=pedido, detalles=detalles)
