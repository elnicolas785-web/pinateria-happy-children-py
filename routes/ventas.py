from flask import render_template, request, redirect, url_for, flash # type: ignore
from routes import ventas_bp # type: ignore
from models import Venta, DetalleVenta, Cliente, Empleado # type: ignore
from extensions import db # type: ignore
from flask_login import login_required, current_user # type: ignore
import datetime

@ventas_bp.route('/')
@login_required
def listar_ventas():
    ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    return render_template('ventas.html', listaVentas=ventas, listaClientes=clientes, listaEmpleados=empleados, venta=None, readonly=False)

@ventas_bp.route('/ver/<int:id>')
@login_required
def ver_venta(id):
    venta = Venta.query.get_or_404(id)
    detalles = DetalleVenta.query.filter_by(id_venta=id).all()
    lista_ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    return render_template('ventas.html', listaVentas=lista_ventas, listaClientes=clientes, listaEmpleados=empleados, venta=venta, detalles=detalles, readonly=True)

@ventas_bp.route('/editar/<int:id>')
@login_required
def editar_venta(id):
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    venta = Venta.query.get_or_404(id)
    detalles = DetalleVenta.query.filter_by(id_venta=id).all()
    lista_ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    return render_template('ventas.html', listaVentas=lista_ventas, listaClientes=clientes, listaEmpleados=empleados, venta=venta, detalles=detalles, readonly=False)

@ventas_bp.route('/cambiarEstado/<int:id>')
@login_required
def cambiar_estado(id):
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    venta = Venta.query.get_or_404(id)
    venta.estado = 'Anulada' if venta.estado == 'Completada' else 'Completada'
    db.session.commit()
    flash('Estado de la venta actualizado.', 'success')
    return redirect(url_for('ventas.listar_ventas'))

@ventas_bp.route('/guardar', methods=['POST'])
@login_required
def guardar():
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    id_venta = request.form.get('id_venta')
    numero_factura = request.form.get('numero_factura')
    id_cliente = request.form.get('cliente.id_cliente')
    id_empleado = request.form.get('empleado.id_empleado')
    fecha_venta = request.form.get('fecha_venta')
    metodo_pago = request.form.get('metodo_pago', 'Efectivo')
    subtotal = request.form.get('subtotal', 0.0)
    total = request.form.get('total', 0.0)
    estado = request.form.get('estado', 'Completada')
    direccion_entrega = request.form.get('direccion_entrega')
    observaciones = request.form.get('observaciones')

    if id_venta:
        # Editar existente
        venta = Venta.query.get(id_venta)
        if venta:
            if id_cliente:
                venta.id_cliente = id_cliente
            venta.id_empleado = id_empleado
            if fecha_venta:
                venta.fecha_venta = fecha_venta
            venta.metodo_pago = metodo_pago
            venta.direccion_entrega = direccion_entrega
            venta.subtotal = float(subtotal)
            venta.total = float(total)
            venta.estado = estado
            venta.observaciones = observaciones
            flash('Venta actualizada correctamente.', 'success')
    else:
        # Crear nueva
        nuevo_num = numero_factura if numero_factura else f"FAC-{int(datetime.datetime.now().timestamp() * 1000) % 100000:05d}"
        nueva_venta = Venta(
            numero_factura=nuevo_num,
            id_cliente=id_cliente,
            id_empleado=id_empleado,
            fecha_venta=fecha_venta if fecha_venta else datetime.date.today(),
            metodo_pago=metodo_pago,
            direccion_entrega=direccion_entrega,
            subtotal=float(subtotal),
            total=float(total),
            estado=estado,
            observaciones=observaciones
        )
        db.session.add(nueva_venta)
        flash('Venta guardada correctamente.', 'success')

    db.session.commit()
    return redirect(url_for('ventas.listar_ventas'))


@ventas_bp.route('/buscar', methods=['GET'])
@login_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        lista_ventas = Venta.query.join(Cliente).filter(
            db.or_(
                Venta.numero_factura.ilike(f'%{busqueda}%'),
                Venta.estado.ilike(f'%{busqueda}%'),
                Cliente.nombres.ilike(f'%{busqueda}%'),
                Cliente.apellidos.ilike(f'%{busqueda}%')
            )
        ).order_by(Venta.fecha_venta.desc()).all()
    else:
        lista_ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    return render_template('ventas.html', listaVentas=lista_ventas, listaClientes=clientes, listaEmpleados=empleados, venta=None, readonly=False)
