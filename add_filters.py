import os

def append_to_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write("\n" + content)

def fix_filters():
    # 1. routes/ventas.py
    ventas_path = r"j:\Desktop\pinateria- happy children\routes\ventas.py"
    with open(ventas_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "@ventas_bp.route('/buscar'" not in content:
        append_to_file(ventas_path, """
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
""")
        print("Añadido buscar a ventas.py")

    # 2. routes/pedidos.py
    pedidos_path = r"j:\Desktop\pinateria- happy children\routes\pedidos.py"
    with open(pedidos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "@pedidos_bp.route('/buscar'" not in content:
        append_to_file(pedidos_path, """
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
""")
        print("Añadido buscar a pedidos.py")

    # 3. routes/productos.py
    productos_path = r"j:\Desktop\pinateria- happy children\routes\productos.py"
    with open(productos_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "@productos_bp.route('/buscar'" not in content:
        append_to_file(productos_path, """
@productos_bp.route('/buscar', methods=['GET'])
@login_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        from models import CategoriaProducto
        productos = Producto.query.join(CategoriaProducto).filter(
            db.or_(
                Producto.nombre.ilike(f'%{busqueda}%'),
                Producto.codigo.ilike(f'%{busqueda}%'),
                CategoriaProducto.nombre.ilike(f'%{busqueda}%')
            )
        ).all()
    else:
        productos = Producto.query.all()
        
    from models import CategoriaProducto
    categorias = CategoriaProducto.query.all()
    return render_template('crud_productos.html', listaProductos=productos, categorias=categorias)
""")
        print("Añadido buscar a productos.py")

    # 4. routes/clientes.py
    clientes_path = r"j:\Desktop\pinateria- happy children\routes\clientes.py"
    with open(clientes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "@clientes_bp.route('/buscar'" not in content:
        append_to_file(clientes_path, """
@clientes_bp.route('/buscar', methods=['GET'])
@login_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        clientes = Cliente.query.filter(
            db.or_(
                Cliente.nombres.ilike(f'%{busqueda}%'),
                Cliente.apellidos.ilike(f'%{busqueda}%'),
                Cliente.numero_documento.ilike(f'%{busqueda}%'),
                Cliente.codigo.ilike(f'%{busqueda}%')
            )
        ).order_by(Cliente.fecha_registro.desc()).all()
    else:
        clientes = Cliente.query.order_by(Cliente.fecha_registro.desc()).all()
        
    return render_template('clientes.html', listaClientes=clientes)
""")
        print("Añadido buscar a clientes.py")

    # 5. routes/empleados.py
    empleados_path = r"j:\Desktop\pinateria- happy children\routes\empleados.py"
    with open(empleados_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if "@empleados_bp.route('/buscar'" not in content:
        append_to_file(empleados_path, """
@empleados_bp.route('/buscar', methods=['GET'])
@login_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        empleados = Empleado.query.filter(
            db.or_(
                Empleado.nombres.ilike(f'%{busqueda}%'),
                Empleado.apellidos.ilike(f'%{busqueda}%'),
                Empleado.documento_identidad.ilike(f'%{busqueda}%')
            )
        ).order_by(Empleado.fecha_contratacion.desc()).all()
    else:
        empleados = Empleado.query.order_by(Empleado.fecha_contratacion.desc()).all()
        
    from models import Rol
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=empleados, listaRoles=roles)
""")
        print("Añadido buscar a empleados.py")

if __name__ == '__main__':
    fix_filters()
