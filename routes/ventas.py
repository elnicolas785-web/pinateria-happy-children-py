from flask import render_template, request, redirect, url_for # type: ignore
from routes import ventas_bp # type: ignore
from models import Venta, DetalleVenta # type: ignore
from extensions import db # type: ignore
import datetime # type: ignore

@ventas_bp.route('/')
def listar_ventas():
    ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    return render_template('ventas.html', listaVentas=ventas)

@ventas_bp.route('/detalle/<int:id_venta>')
def detalle_venta(id_venta):
    venta = Venta.query.get_or_404(id_venta)
    detalles = DetalleVenta.query.filter_by(id_venta=id_venta).all()
    return render_template('success.html', venta=venta, detalles=detalles)
