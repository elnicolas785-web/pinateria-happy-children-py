from flask import render_template, request, redirect, url_for # type: ignore
from routes import categorias_bp # type: ignore
from models import CategoriaProducto # type: ignore
from extensions import db # type: ignore

@categorias_bp.route('/')
def listar_categorias():
    categorias = CategoriaProducto.query.all()
    return render_template('categorias.html', categorias=categorias, categoria=CategoriaProducto(), readonly=False)

@categorias_bp.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form.get('codigo')
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')

    nueva_cat = CategoriaProducto(
        codigo=codigo,
        nombre=nombre,
        descripcion=descripcion,
        activo='Activo'
    )
    db.session.add(nueva_cat)
    db.session.commit()
    return redirect(url_for('categorias.listar_categorias'))
