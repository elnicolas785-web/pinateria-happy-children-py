from flask import render_template # type: ignore
from routes import dashboard_bp # type: ignore
from models import Producto, Venta, Cliente, Empleado, Rol, UsuarioCliente # type: ignore

@dashboard_bp.route('/')
def root():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    # Esta es una versión simplificada del dashboard administrador
    cant_productos = Producto.query.count()
    cant_empleados = Empleado.query.count()
    cant_ventas = Venta.query.count()
    cant_clientes = Cliente.query.count()

    lista_empleados = Empleado.query.order_by(Empleado.id_empleado.desc()).all()
    lista_roles = Rol.query.all()

    return render_template('dashboard-pinata.html', 
                          cantProductos=cant_productos, 
                          cantEmpleados=cant_empleados,
                          cantVentas=cant_ventas,
                          cantClientes=cant_clientes,
                          listaEmpleados=lista_empleados,
                          listaRoles=lista_roles)
