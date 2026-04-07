from flask import render_template, request, redirect, url_for, flash, abort # type: ignore
from routes import ventas_bp # type: ignore
from models import Venta, DetalleVenta, Cliente, Empleado, Producto, Pedido, db # type: ignore
from extensions import employee_required 
from flask_login import login_required, current_user # type: ignore
import datetime

def obtener_historial_combinado():
    """Función auxiliar para no repetir código de mezcla de tablas"""
    ventas = Venta.query.all()
    pedidos = Pedido.query.all()
    lista = ventas + pedidos
    # Ordenar por fecha_venta o fecha_pedido según disponibilidad
    lista.sort(key=lambda x: x.fecha_venta if hasattr(x, 'fecha_venta') else x.fecha_pedido, reverse=True)
    return lista

@ventas_bp.route('/')
@employee_required
def listar_ventas():
    lista_combinada = obtener_historial_combinado()
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    productos = Producto.query.filter_by(activo='Activo').all()
    
    return render_template('ventas.html', 
                           listaVentas=lista_combinada, 
                           listaClientes=clientes, 
                           listaEmpleados=empleados, 
                           listaProductos=productos, 
                           venta=None, 
                           readonly=False,
                           es_pedido=False)

@ventas_bp.route('/ver/<string:tipo>/<int:id>')
@employee_required
def ver_venta(tipo, id):
    # Ahora pasamos el tipo (venta o pedido) en la URL para evitar confusiones
    es_pedido = (tipo == 'pedido')
    detalles = []
    
    if es_pedido:
        venta = Pedido.query.get_or_404(id)
        # Asumiendo que en models.py Pedido tiene una relación 'detalles'
        detalles = venta.detalles if hasattr(venta, 'detalles') else []
    else:
        venta = Venta.query.get_or_404(id)
        detalles = DetalleVenta.query.filter_by(id_venta=id).all()

    lista_combinada = obtener_historial_combinado()
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    productos = Producto.query.filter_by(activo='Activo').all()
    
    return render_template('ventas.html', 
                           listaVentas=lista_combinada, 
                           listaClientes=clientes, 
                           listaEmpleados=empleados, 
                           listaProductos=productos, 
                           venta=venta, 
                           detalles=detalles, 
                           readonly=True,
                           es_pedido=es_pedido)

@ventas_bp.route('/editar/<string:tipo>/<int:id>')
@employee_required
def editar_venta(id, tipo):
    es_pedido = (tipo == 'pedido')
    if es_pedido:
        venta = Pedido.query.get_or_404(id)
        detalles = venta.detalles if hasattr(venta, 'detalles') else []
    else:
        venta = Venta.query.get_or_404(id)
        detalles = DetalleVenta.query.filter_by(id_venta=id).all()
        
    lista_combinada = obtener_historial_combinado()
    clientes = Cliente.query.all()
    empleados = Empleado.query.all()
    productos = Producto.query.filter_by(activo='Activo').all()
    
    return render_template('ventas.html', 
                           listaVentas=lista_combinada, 
                           listaClientes=clientes, 
                           listaEmpleados=empleados, 
                           listaProductos=productos, 
                           venta=venta, 
                           detalles=detalles,
                           readonly=False,
                           es_pedido=es_pedido)

@ventas_bp.route('/cambiarEstado/<string:tipo>/<int:id>')
@employee_required
def cambiar_estado(tipo, id):
    if tipo == 'venta':
        venta = Venta.query.get_or_404(id)
        detalles = DetalleVenta.query.filter_by(id_venta=id).all()
        try:
            if venta.estado == 'Completada':
                venta.estado = 'Anulada'
                for d in detalles:
                    prod = Producto.query.get(d.id_producto)
                    if prod: prod.stock_actual += d.cantidad
                flash('Venta anulada y stock devuelto.', 'warning')
            else:
                venta.estado = 'Completada'
                flash('Venta reactivada.', 'success')
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
    else:
        pedido = Pedido.query.get_or_404(id)
        pedido.estado = 'Anulado' if pedido.estado != 'Anulado' else 'Completado'
        db.session.commit()
        flash('Estado del pedido web actualizado.', 'info')

    return redirect(url_for('ventas.listar_ventas'))

@ventas_bp.route('/guardar', methods=['POST'])
@employee_required
def guardar():
    id_venta = request.form.get('id_venta')
    id_cliente = request.form.get('id_cliente')
    id_empleado = request.form.get('id_empleado')
    total = float(request.form.get('total', 0.0))
    
    ids_productos = request.form.getlist('productos[]')
    cantidades = request.form.getlist('cantidades[]')

    try:
        if not id_venta:
            nueva_venta = Venta(
                numero_factura=f"FAC-{int(datetime.datetime.now().timestamp() * 1000) % 100000:05d}",
                id_cliente=id_cliente,
                id_empleado=id_empleado,
                fecha_venta=datetime.date.today(),
                metodo_pago=request.form.get('metodo_pago', 'Efectivo'),
                subtotal=total,
                total=total,
                estado='Completada'
            )
            db.session.add(nueva_venta)
            db.session.flush() 

            for i in range(len(ids_productos)):
                id_p = int(ids_productos[i])
                cant = int(cantidades[i])
                prod = Producto.query.get(id_p)
                if prod:
                    if prod.stock_actual < cant:
                        db.session.rollback()
                        flash(f"¡STOCK INSUFICIENTE! {prod.nombre} solo tiene {prod.stock_actual}.", "danger")
                        return redirect(url_for('ventas.listar_ventas'))
                    
                    prod.stock_actual -= cant
                    detalle = DetalleVenta(
                        codigo=f"DET-{nueva_venta.numero_factura}-{id_p}",
                        id_venta=nueva_venta.id_venta,
                        id_producto=id_p,
                        cantidad=cant,
                        precio_unitario=prod.precio_venta,
                        subtotal=cant * float(prod.precio_venta)
                    )
                    db.session.add(detalle)

            db.session.commit()
            flash('Venta registrada con éxito.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar: {str(e)}', 'danger')

    return redirect(url_for('ventas.listar_ventas'))

@ventas_bp.route('/buscar', methods=['GET'])
@employee_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    ventas = Venta.query.join(Cliente).filter(
        db.or_(
            Venta.numero_factura.ilike(f'%{busqueda}%'), 
            Cliente.nombres.ilike(f'%{busqueda}%'),
            Cliente.apellidos.ilike(f'%{busqueda}%'),
            (Cliente.nombres + ' ' + Cliente.apellidos).ilike(f'%{busqueda}%')
        )
    ).all()
    
    pedidos = Pedido.query.join(Cliente).filter(
        db.or_(
            Pedido.numero_pedido.ilike(f'%{busqueda}%'), 
            Cliente.nombres.ilike(f'%{busqueda}%'),
            Cliente.apellidos.ilike(f'%{busqueda}%'),
            (Cliente.nombres + ' ' + Cliente.apellidos).ilike(f'%{busqueda}%')
        )
    ).all()
    
    lista_combinada = ventas + pedidos
    lista_combinada.sort(key=lambda x: x.fecha_venta if hasattr(x, 'fecha_venta') else x.fecha_pedido, reverse=True)
    
    return render_template('ventas.html', 
                           listaVentas=lista_combinada, 
                           listaClientes=Cliente.query.all(), 
                           listaEmpleados=Empleado.query.all(), 
                           listaProductos=Producto.query.filter_by(activo='Activo').all(),
                           venta=None, 
                           readonly=False)