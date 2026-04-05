from flask import render_template, request, redirect, url_for # type: ignore
from flask_login import login_required, current_user
from routes import productos_bp # type: ignore
from models import Producto, CategoriaProducto # type: ignore
from extensions import db, employee_required # Importamos employee_required

@productos_bp.route('/')
@employee_required
def listar_productos():
    productos = Producto.query.all()
    categorias = CategoriaProducto.query.all()
    # Dummy empty producto
    producto = Producto()
    return render_template('crud_productos.html', listaProductos=productos, categorias=categorias, producto=producto, readonly=False)

@productos_bp.route('/guardar', methods=['POST'])
@employee_required
def guardar():
    # Lógica de guardado simplificada
    codigo = request.form.get('codigo')
    nombre = request.form.get('nombre')
    id_categoria = request.form.get('categoria.id_categoria')
    precio_compra = request.form.get('precio_compra')
    precio_venta = request.form.get('precio_venta')
    stock_actual = request.form.get('stock_actual')
    stock_minimo = request.form.get('stock_minimo')
    unidad_medida = request.form.get('unidad_medida')

    nuevo_prod = Producto(
        codigo=codigo,
        nombre=nombre,
        id_categoria=id_categoria,
        precio_compra=precio_compra,
        precio_venta=precio_venta,
        stock_actual=stock_actual,
        stock_minimo=stock_minimo,
        unidad_medida=unidad_medida,
        activo='Activo'
    )
    db.session.add(nuevo_prod)
    db.session.commit()
    return redirect(url_for('productos.listar_productos'))


@productos_bp.route('/buscar', methods=['GET'])
@employee_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        productos = Producto.query.join(CategoriaProducto).filter(
            db.or_(
                Producto.nombre.ilike(f'%{busqueda}%'),
                Producto.codigo.ilike(f'%{busqueda}%'),
                CategoriaProducto.nombre.ilike(f'%{busqueda}%')
            )
        ).all()
    else:
        productos = Producto.query.all()
        

    categorias = CategoriaProducto.query.all()
    # Provide dummy producto and readonly flag to prevent template errors
    producto = Producto()
    return render_template('crud_productos.html', listaProductos=productos, categorias=categorias, producto=producto, readonly=False)
