from flask import render_template, redirect, url_for, flash, request # type: ignore
from routes import dashboard_bp # type: ignore
from flask_login import login_required, current_user # type: ignore
from models import Producto, Venta, Cliente, Empleado, Rol, UsuarioCliente, CategoriaProducto, db # type: ignore

@dashboard_bp.route('/')
def root():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Dispatcher para redirigir según el rol del usuario
    if isinstance(current_user, UsuarioCliente):
        return redirect(url_for('dashboard.cliente_dashboard'))
    
    if isinstance(current_user, Empleado):
        if current_user.rol and current_user.rol.nombre_rol.upper() in ['ADMINISTRADOR', 'ADMIN']:
            return redirect(url_for('dashboard.admin_dashboard'))
        else:
            return redirect(url_for('dashboard.empleado_dashboard'))
            
    # Fallback si por alguna razón no coincide nada
    return redirect(url_for('dashboard.root'))

@dashboard_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Solo administradores
    if not isinstance(current_user, Empleado) or not (current_user.rol and current_user.rol.nombre_rol.upper() in ['ADMINISTRADOR', 'ADMIN']):
        flash("Acceso denegado: Se requiere rol de Administrador.", "danger")
        return redirect(url_for('dashboard.root'))

    # Lógica del dashboard de administrador
    cant_productos = Producto.query.count()
    cant_empleados = Empleado.query.count()
    cant_ventas = Venta.query.count()
    cant_clientes = Cliente.query.count()
    cant_categorias = CategoriaProducto.query.count()
    cant_roles = Rol.query.count()
    cant_usuarios = UsuarioCliente.query.count()

    lista_empleados = Empleado.query.order_by(Empleado.id_empleado.desc()).all()
    lista_roles = Rol.query.all()
    lista_usuarios = UsuarioCliente.query.order_by(UsuarioCliente.id_usuario.desc()).limit(10).all()
    lista_clientes = Cliente.query.all()
    
    # Obtener distribución de categorías para el gráfico
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
    # Solo empleados
    if not isinstance(current_user, Empleado):
        flash("Acceso denegado: Área exclusiva de empleados.", "danger")
        return redirect(url_for('dashboard.root'))
        
    # Datos necesarios para la vista (modales de registro si existen, etc.)
    # Nota: El dashboard de empleado original parece aceptar listas para gestionar datos, 
    # proveyendolas de ser requeridas por componentes UI aun si no son admin.
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
    # Solo clientes
    if not isinstance(current_user, UsuarioCliente):
        flash("Acceso denegado: Área exclusiva de clientes.", "danger")
        return redirect(url_for('dashboard.root'))
        
    return render_template('dashboard-cliente.html')
