from flask import render_template, request, redirect, url_for # type: ignore
from routes import pedidos_bp # type: ignore
from models import Pedido, DetallePedido, Cliente, Producto # type: ignore
from extensions import db # type: ignore
from flask_login import current_user, login_required # type: ignore

@pedidos_bp.route('/')
def listar_pedidos():
    pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    return render_template('pedidos.html', listaPedidos=pedidos)

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
def detalle_pedido(id_pedido):
    pedido = Pedido.query.get_or_404(id_pedido)
    detalles = DetallePedido.query.filter_by(id_pedido=id_pedido).all()
    return render_template('mis-entregas.html', pedido=pedido, listaDetalles=detalles)
