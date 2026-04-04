from flask import render_template, request, redirect, url_for, flash
from routes import pedidos_bp
from models import Pedido, DetallePedido, Cliente, Producto
from extensions import db
from flask_login import current_user, login_required
import datetime

@pedidos_bp.route('/')
@login_required
def listar_pedidos():
    pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    clientes = Cliente.query.all()
    return render_template('pedidos.html', listaPedidos=pedidos, listaClientes=clientes, pedido=None, readonly=False)

@pedidos_bp.route('/mis-pedidos')
@login_required
def mis_pedidos():
    # Asume que el current_user tiene relación con Cliente
    id_cliente = current_user.id_cliente if hasattr(current_user, 'id_cliente') else None
    pedidos = Pedido.query.filter_by(id_cliente=id_cliente).order_by(Pedido.fecha_pedido.desc()).all() if id_cliente else []
    
    lista_detalles = []
    total_gastado = 0
    for p in pedidos:
        total_gastado += p.total
        detalles = DetallePedido.query.filter_by(id_pedido=p.id_pedido).all()
        for d in detalles:
            d.pedido = p
            d.producto = Producto.query.get(d.id_producto)
            lista_detalles.append(d)
            
    return render_template('mis-pedidos.html', pedidos=pedidos, listaDetalles=lista_detalles, totalGastado=total_gastado)

@pedidos_bp.route('/detalle/<int:id_pedido>')
@login_required
def detalle_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    detalles = DetallePedido.query.filter_by(id_pedido=id_pedido).all()
    return render_template('mis-entregas.html', pedido=pedido, listaDetalles=detalles)

@pedidos_bp.route('/editar/<int:id>')
@login_required
def editar_pedido(id):
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    pedido = Pedido.query.get_or_404(id)
    detalles = DetallePedido.query.filter_by(id_pedido=id).all()
    lista_pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    clientes = Cliente.query.all()
    
    for d in detalles:
        d.producto = Producto.query.get(d.id_producto)
        
    return render_template('pedidos.html', listaPedidos=lista_pedidos, listaClientes=clientes, pedido=pedido, detalles=detalles, readonly=False)

@pedidos_bp.route('/ver/<int:id>')
@login_required
def ver_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    detalles = DetallePedido.query.filter_by(id_pedido=id).all()
    lista_pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    clientes = Cliente.query.all()
    
    for d in detalles:
        d.producto = Producto.query.get(d.id_producto)
        
    return render_template('pedidos.html', listaPedidos=lista_pedidos, listaClientes=clientes, pedido=pedido, detalles=detalles, readonly=True)

@pedidos_bp.route('/cambiarEstado/<int:id>')
@login_required
def cambiar_estado(id):
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    pedido = Pedido.query.get_or_404(id)
    pedido.estado = 'Pendiente' if pedido.estado == 'Cancelado' else 'Cancelado'
    db.session.commit()
    flash('Estado del pedido actualizado.', 'success')
    return redirect(url_for('pedidos.listar_pedidos'))

@pedidos_bp.route('/guardar', methods=['POST'])
@login_required
def guardar_pedido():
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    id_pedido = request.form.get('id_pedido')
    numero_pedido = request.form.get('numero_pedido')
    id_cliente = request.form.get('cliente.id_cliente')
    fecha_pedido = request.form.get('fecha_pedido')
    fecha_entrega_esperada = request.form.get('fecha_entrega_esperada')
    direccion_entrega = request.form.get('direccion_entrega')
    subtotal = request.form.get('subtotal', 0.0)
    total = request.form.get('total', 0.0)
    estado = request.form.get('estado', 'Pendiente')
    observaciones = request.form.get('observaciones')

    if id_pedido:
        pedido = Pedido.query.get(id_pedido)
        if pedido:
            if id_cliente:
                pedido.id_cliente = id_cliente
            if fecha_pedido:
                pedido.fecha_pedido = fecha_pedido
            if fecha_entrega_esperada:
                pedido.fecha_entrega_esperada = fecha_entrega_esperada
            pedido.direccion_entrega = direccion_entrega
            pedido.subtotal = float(subtotal)
            pedido.total = float(total)
            pedido.estado = estado
            pedido.observaciones = observaciones
            flash('Pedido actualizado correctamente.', 'success')
    else:
        nuevo_num = numero_pedido if numero_pedido else f"PED-{int(datetime.datetime.now().timestamp() * 1000) % 100000:05d}"
        nuevo_pedido = Pedido(
            numero_pedido=nuevo_num,
            id_cliente=id_cliente,
            fecha_pedido=fecha_pedido if fecha_pedido else datetime.date.today(),
            fecha_entrega_esperada=fecha_entrega_esperada if fecha_entrega_esperada else None,
            direccion_entrega=direccion_entrega,
            subtotal=float(subtotal),
            total=float(total),
            estado=estado,
            observaciones=observaciones
        )
        db.session.add(nuevo_pedido)
        flash('Pedido creado correctamente.', 'success')

    db.session.commit()
    return redirect(url_for('pedidos.listar_pedidos'))


@pedidos_bp.route('/buscar', methods=['GET'])
@login_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        pedidos = Pedido.query.join(Cliente).filter(
            db.or_(
                Pedido.numero_pedido.ilike(f'%{busqueda}%'),
                Pedido.estado.ilike(f'%{busqueda}%'),
                Cliente.nombres.ilike(f'%{busqueda}%'),
                Cliente.apellidos.ilike(f'%{busqueda}%')
            )
        ).order_by(Pedido.fecha_pedido.desc()).all()
    else:
        pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
        
    clientes = Cliente.query.all()
    return render_template('pedidos.html', listaPedidos=pedidos, listaClientes=clientes, pedido=None, readonly=False)
