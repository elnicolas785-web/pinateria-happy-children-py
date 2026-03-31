from flask import render_template, request, redirect, url_for, flash # type: ignore
from routes import categorias_bp # type: ignore
from models import CategoriaProducto # type: ignore
from extensions import db # type: ignore
import uuid

@categorias_bp.route('/')
def listar_categorias():
    categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', listaCategorias=categorias, categoria=CategoriaProducto(), readonly=False)

@categorias_bp.route('/guardar', methods=['POST'])
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
def buscar():
    nombre = request.args.get('nombre', '')
    if nombre:
        categorias = CategoriaProducto.query.filter(CategoriaProducto.nombre.ilike(f'%{nombre}%')).all()
    else:
        categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', listaCategorias=categorias, categoria=CategoriaProducto(), readonly=False)

@categorias_bp.route('/editar/<int:id>')
def editar(id):
    categoria = CategoriaProducto.query.get_or_404(id)
    categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', listaCategorias=categorias, categoria=categoria, readonly=False)

@categorias_bp.route('/ver/<int:id>')
def ver(id):
    categoria = CategoriaProducto.query.get_or_404(id)
    categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', listaCategorias=categorias, categoria=categoria, readonly=True)

@categorias_bp.route('/cambiarEstado/<int:id>')
def cambiar_estado(id):
    categoria = CategoriaProducto.query.get_or_404(id)
    if categoria.activo == 'Activo':
        categoria.activo = 'Inactivo'
    else:
        categoria.activo = 'Activo'
    db.session.commit()
    return redirect(url_for('categorias.listar_categorias'))
