from flask import render_template, request, redirect, url_for # type: ignore
from routes import roles_bp # type: ignore
from models import Rol # type: ignore
from extensions import db # type: ignore

@roles_bp.route('/')
def listar_roles():
    roles = Rol.query.all()
    return render_template('roles.html', listaRoles=roles, rol=Rol(), readonly=False)

@roles_bp.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form.get('codigo')
    nombre_rol = request.form.get('nombre_rol')

    nuevo_rol = Rol(
        codigo=codigo,
        nombre_rol=nombre_rol,
        estado='Activo'
    )
    db.session.add(nuevo_rol)
    db.session.commit()
    return redirect(url_for('roles.listar_roles'))
