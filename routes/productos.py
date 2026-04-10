import pandas as pd
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from routes import productos_bp # type: ignore
from models import Producto, CategoriaProducto # type: ignore
from extensions import db, employee_required 

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
            descripcion=request.form.get('descripcion'),
            imagenUrl=request.form.get('imagenUrl'),
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
        producto.descripcion = request.form.get('descripcion')
        producto.imagenUrl = request.form.get('imagenUrl')
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
    producto.activo = 'Inactivo' if producto.activo == 'Activo' else 'Activo'
    db.session.commit()
    flash(f'Estado de {producto.nombre} actualizado', 'info')
    return redirect(url_for('productos.listar_productos'))

# --- 8. IMPORTAR DESDE EXCEL ---
@productos_bp.route('/importar', methods=['POST'])
@employee_required
def importar_excel():
    if 'archivo' not in request.files:
        flash('No se seleccionó ningún archivo', 'danger')
        return redirect(url_for('productos.listar_productos'))
    
    file = request.files['archivo']
    try:
        df = pd.read_excel(file, engine='openpyxl')
        print("--- COLUMNAS DETECTADAS EN EL EXCEL ---")
        print(df.columns.tolist()) # Esto saldrá en tu terminal
        
        nuevos = 0
        actualizados = 0

        for index, row in df.iterrows():
            codigo = str(row['codigo']).strip()
            # Debug por cada fila
            print(f"Procesando fila {index}: Código {codigo}")

            prod_existente = Producto.query.filter_by(codigo=codigo).first()
            
            # Aseguramos conversión limpia de datos
            id_cat = int(row['id_categoria'])
            p_compra = float(row['precio_compra'])
            p_venta = float(row['precio_venta'])
            s_actual = int(row['stock_actual'])
            s_min = int(row['stock_minimo'])

            if prod_existente:
                prod_existente.nombre = row['nombre']
                prod_existente.id_categoria = id_cat
                prod_existente.precio_compra = p_compra
                prod_existente.precio_venta = p_venta
                prod_existente.stock_actual = s_actual
                prod_existente.stock_minimo = s_min
                prod_existente.unidad_medida = row['unidad_medida']
                actualizados += 1
            else:
                nuevo_p = Producto(
                    codigo=codigo,
                    nombre=row['nombre'],
                    id_categoria=id_cat,
                    precio_compra=p_compra,
                    precio_venta=p_venta,
                    stock_actual=s_actual,
                    stock_minimo=s_min,
                    unidad_medida=row['unidad_medida'],
                    activo='Activo'
                )
                db.session.add(nuevo_p)
                nuevos += 1
        
        db.session.commit()
        print(f"COMMIT EXITOSO: {nuevos} creados.")
        flash(f'¡Éxito! {nuevos} nuevos y {actualizados} actualizados.', 'success')
        
    except Exception as error_desc:
        db.session.rollback()
        # ESTO ES LO MÁS IMPORTANTE: Mira tu terminal cuando esto falle
        print("---------- ERROR CRÍTICO ----------")
        print(error_desc)
        print("-----------------------------------")
        flash(f'Error al procesar: {str(error_desc)}', 'danger')
        
    return redirect(url_for('productos.listar_productos'))