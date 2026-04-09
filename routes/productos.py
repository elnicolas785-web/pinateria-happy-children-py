from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from routes import productos_bp # type: ignore
from models import Producto, CategoriaProducto # type: ignore
from extensions import db, employee_required # Importamos employee_required

# --- 1. LISTAR / NUEVO ---
@productos_bp.route('/')
@employee_required
def listar_productos():
    productos = Producto.query.all()
    categorias = CategoriaProducto.query.all()
    # Formulario limpio para nuevo producto
    return render_template('crud_productos.html', 
                           listaProductos=productos, 
                           categorias=categorias, 
                           producto=Producto(), 
                           readonly=False,
                           editMode=False)

# --- 2. VER (SOLO LECTURA) ---
@productos_bp.route('/ver/<int:id>')
@employee_required
def ver(id):
    producto_a_ver = Producto.query.get_or_404(id)
    productos = Producto.query.all()
    categorias = CategoriaProducto.query.all()
    # Enviamos readonly=True para bloquear los inputs en el HTML
    return render_template('crud_productos.html', 
                           listaProductos=productos, 
                           categorias=categorias, 
                           producto=producto_a_ver, 
                           readonly=True,
                           editMode=False)

# --- 3. EDITAR (CARGAR DATOS) ---
@productos_bp.route('/editar/<int:id>')
@employee_required
def editar(id):
    producto_a_editar = Producto.query.get_or_404(id)
    productos = Producto.query.all()
    categorias = CategoriaProducto.query.all()
    # readonly=False permite escribir, editMode=True cambia el botón a "Actualizar"
    return render_template('crud_productos.html', 
                           listaProductos=productos, 
                           categorias=categorias, 
                           producto=producto_a_editar, 
                           readonly=False,
                           editMode=True)

# --- 4. GUARDAR NUEVO ---
@productos_bp.route('/guardar', methods=['POST'])
@employee_required
def guardar():
    try:
        nuevo_prod = Producto(
            codigo=request.form.get('codigo'),
            nombre=request.form.get('nombre'),
            id_categoria=request.form.get('id_categoria'),
            precio_compra=request.form.get('precio_compra'),
            precio_venta=request.form.get('precio_venta'),
            stock_actual=request.form.get('stock_actual'),
            stock_minimo=request.form.get('stock_minimo'),
            unidad_medida=request.form.get('unidad_medida'),
            activo='Activo'
        )
        db.session.add(nuevo_prod)
        db.session.commit()
        flash('Producto guardado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar: {str(e)}', 'danger')
    return redirect(url_for('productos.listar_productos'))

# --- 5. ACTUALIZAR EXISTENTE ---
@productos_bp.route('/actualizar/<int:id>', methods=['POST'])
@employee_required
def actualizar(id):
    producto = Producto.query.get_or_404(id)
    try:
        producto.codigo = request.form.get('codigo')
        producto.nombre = request.form.get('nombre')
        producto.id_categoria = request.form.get('id_categoria')
        producto.precio_compra = request.form.get('precio_compra')
        producto.precio_venta = request.form.get('precio_venta')
        producto.stock_actual = request.form.get('stock_actual')
        producto.stock_minimo = request.form.get('stock_minimo')
        producto.unidad_medida = request.form.get('unidad_medida')

        db.session.commit()
        flash('Producto actualizado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'danger')
    return redirect(url_for('productos.listar_productos'))

# --- 6. BUSCAR ---
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
    return render_template('crud_productos.html', 
                           listaProductos=productos, 
                           categorias=categorias, 
                           producto=Producto(), 
                           readonly=False,
                           editMode=False)
    
# --- 7. CAMBIAR ESTADO (ACTIVAR/DESACTIVAR) ---
@productos_bp.route('/cambiar_estado/<int:id>')
@employee_required
def cambiar_estado(id):
    producto = Producto.query.get_or_404(id)
    # Cambia el estado al opuesto
    producto.activo = 'Inactivo' if producto.activo == 'Activo' else 'Activo'
    db.session.commit()
    flash(f'Estado de {producto.nombre} actualizado', 'info')
    return redirect(url_for('productos.listar_productos'))