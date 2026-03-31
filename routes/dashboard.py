from flask import render_template # type: ignore
from routes import dashboard_bp # type: ignore
from models import Producto, Venta, Cliente, Empleado, Rol, UsuarioCliente, CategoriaProducto, db # type: ignore

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
    cant_categorias = CategoriaProducto.query.count()
    cant_roles = Rol.query.count()
    cant_usuarios = UsuarioCliente.query.count()

    lista_empleados = Empleado.query.order_by(Empleado.id_empleado.desc()).all()
    lista_roles = Rol.query.all()
    
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
                          catLabels=categorias_nombres,
                          catValues=categorias_conteos)
