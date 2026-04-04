from flask import render_template, redirect, url_for, flash, request, abort # type: ignore
from routes import dashboard_bp # type: ignore
from flask_login import login_required, current_user # type: ignore
from models import Producto, Venta, Cliente, Empleado, Rol, UsuarioCliente, CategoriaProducto, db # type: ignore
from extensions import admin_required # Importamos tu nuevo "guardaespaldas"

@dashboard_bp.route('/')
def root():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Ruta puente: Redirige al usuario a su panel específico 
    según su tipo de cuenta y rol.
    """
    if isinstance(current_user, UsuarioCliente):
        return redirect(url_for('dashboard.cliente_dashboard'))
    
    if isinstance(current_user, Empleado):
        # Verificamos si el empleado tiene rango de jefe
        rol_nombre = current_user.rol.nombre_rol.upper() if current_user.rol else ""
        if rol_nombre in ['ADMINISTRADOR', 'ADMIN']:
            return redirect(url_for('dashboard.admin_dashboard'))
        else:
            return redirect(url_for('dashboard.empleado_dashboard'))
            
    return redirect(url_for('dashboard.root'))

@dashboard_bp.route('/admin/dashboard')
@login_required
@admin_required # Solo permite el paso a Administradores
def admin_dashboard():
    # Consultas para las tarjetas de estadísticas
    cant_productos = Producto.query.count()
    cant_empleados = Empleado.query.count()
    cant_ventas = Venta.query.count()
    cant_clientes = Cliente.query.count()
    cant_categorias = CategoriaProducto.query.count()
    cant_roles = Rol.query.count()
    cant_usuarios = UsuarioCliente.query.count()

    # Listas para las tablas del dashboard
    lista_empleados = Empleado.query.order_by(Empleado.id_empleado.desc()).all()
    lista_roles = Rol.query.all()
    lista_usuarios = UsuarioCliente.query.order_by(UsuarioCliente.id_usuario.desc()).limit(10).all()
    lista_clientes = Cliente.query.all()
    
    # Lógica para el gráfico de categorías
    categorias_nombres = []
    categorias_conteos = []
    categorias = CategoriaProducto.query.all()
    for cat in categorias:
        count = Producto.query.filter_by(id_categoria=cat.id_categoria).count()
        categorias_nombres.append(cat.nombre)
        categorias_conteos.append(count)

    return render_template('dashboard-pinata.html', 
                          cantProductos=cant_productos, 
                          cantEmpleados=cant_empleados,
                          cantVentas=cant_ventas,
                          cantClientes=cant_clientes,
                          cantCategorias=cant_categorias,
                          cantRoles=cant_roles,
                          cantUsuarios=cant_usuarios,
                          listaEmpleados=lista_empleados,
                          listaRoles=lista_roles,
                          listaUsuarios=lista_usuarios,
                          listaClientes=lista_clientes,
                          catLabels=categorias_nombres,
                          catValues=categorias_conteos)

@dashboard_bp.route('/empleado/dashboard')
@login_required
def empleado_dashboard():
    """
    Panel operativo para empleados. 
    Bloqueamos a Clientes y redirigimos a Admins.
    """
    # 1. Seguridad: Si es un Admin, lo mandamos a SU dashboard
    rol_nombre = current_user.rol.nombre_rol.upper() if current_user.rol else ""
    if rol_nombre in ['ADMINISTRADOR', 'ADMIN']:
        return redirect(url_for('dashboard.admin_dashboard'))

    # 2. Seguridad: Si no es empleado (es cliente), prohibido el paso
    if not isinstance(current_user, Empleado):
        abort(403)
        
    # Datos para la gestión operativa
    lista_empleados = Empleado.query.order_by(Empleado.id_empleado.desc()).all()
    lista_roles = Rol.query.all()
    lista_usuarios = UsuarioCliente.query.order_by(UsuarioCliente.id_usuario.desc()).limit(10).all()
    lista_clientes = Cliente.query.all()

    return render_template('dashboard-empleado.html',
                           listaEmpleados=lista_empleados,
                           listaRoles=lista_roles,
                           listaUsuarios=lista_usuarios,
                           listaClientes=lista_clientes)

@dashboard_bp.route('/cliente/dashboard')
@login_required
def cliente_dashboard():
    # Seguridad: Solo clientes reales entran aquí
    if not isinstance(current_user, UsuarioCliente):
        abort(403)
        
    return render_template('dashboard-cliente.html')