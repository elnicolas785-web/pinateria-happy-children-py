from flask import render_template, request, redirect, url_for, flash # type: ignore
from routes import categorias_bp # type: ignore
from models import CategoriaProducto # type: ignore
from extensions import db, employee_required # Importamos employee_required
import uuid

@categorias_bp.route('/')
@employee_required
def listar_categorias():
    categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', listaCategorias=categorias, categoria=CategoriaProducto(), readonly=False)

@categorias_bp.route('/guardar', methods=['POST'])
@employee_required
def guardar():
    id_categoria = request.form.get('id_categoria')
    codigo = request.form.get('codigo')
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    activo = request.form.get('activo', 'Activo')

    if id_categoria:
        # Update existing
        categoria = CategoriaProducto.query.get(id_categoria)
        if categoria:
            categoria.nombre = nombre
            categoria.descripcion = descripcion
            categoria.activo = activo
    else:
        # Create new
        if not codigo:
            codigo = f"CAT-{uuid.uuid4().hex[:6].upper()}"
        
        nueva_cat = CategoriaProducto(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            activo=activo
        )
        db.session.add(nueva_cat)
        
    db.session.commit()
    return redirect(url_for('categorias.listar_categorias'))

@categorias_bp.route('/buscar', methods=['GET'])
@employee_required
def buscar():
    nombre = request.args.get('nombre', '')
    if nombre:
        categorias = CategoriaProducto.query.filter(CategoriaProducto.nombre.ilike(f'%{nombre}%')).all()
    else:
        categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', listaCategorias=categorias, categoria=CategoriaProducto(), readonly=False)

@categorias_bp.route('/editar/<int:id>')
@employee_required
def editar(id):
    categoria = CategoriaProducto.query.get_or_404(id)
    categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', listaCategorias=categorias, categoria=categoria, readonly=False)

@categorias_bp.route('/ver/<int:id>')
@employee_required
def ver(id):
    categoria = CategoriaProducto.query.get_or_404(id)
    categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', listaCategorias=categorias, categoria=categoria, readonly=True)

@categorias_bp.route('/cambiarEstado/<int:id>')
@employee_required
def cambiar_estado(id):
    categoria = CategoriaProducto.query.get_or_404(id)
    if categoria.activo == 'Activo':
        categoria.activo = 'Inactivo'
    else:
        categoria.activo = 'Activo'
    db.session.commit()
    return redirect(url_for('categorias.listar_categorias'))
