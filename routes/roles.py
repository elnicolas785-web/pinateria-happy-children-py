from flask import render_template, request, redirect, url_for, flash # type: ignore
from routes import roles_bp # type: ignore
from models import Rol # type: ignore
from extensions import db, admin_required # Importamos admin_required
import uuid

@roles_bp.route('/')
@admin_required
def listar_roles():
    roles = Rol.query.all()
    return render_template('roles.html', listaRoles=roles, rol=Rol(), readonly=False)

@roles_bp.route('/guardar', methods=['POST'])
@admin_required
def guardar():
    id_rol = request.form.get('id_rol')
    codigo = request.form.get('codigo')
    nombre_rol = request.form.get('nombre_rol')
    estado = request.form.get('estado', 'Activo')

    if id_rol:
        rol = Rol.query.get(id_rol)
        if rol:
            rol.nombre_rol = nombre_rol
            rol.estado = estado
    else:
        if not codigo:
            codigo = f"ROL-{uuid.uuid4().hex[:6].upper()}"
        
        nuevo_rol = Rol(
            codigo=codigo,
            nombre_rol=nombre_rol,
            estado=estado
        )
        db.session.add(nuevo_rol)

    db.session.commit()
    return redirect(url_for('roles.listar_roles'))

@roles_bp.route('/buscar', methods=['GET'])
@admin_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        roles = Rol.query.filter(Rol.nombre_rol.ilike(f'%{busqueda}%')).all()
    else:
        roles = Rol.query.all()
    return render_template('roles.html', listaRoles=roles, rol=Rol(), readonly=False)

@roles_bp.route('/editar/<int:id>')
@admin_required
def editar(id):
    rol = Rol.query.get_or_404(id)
    roles = Rol.query.all()
    return render_template('roles.html', listaRoles=roles, rol=rol, readonly=False)

@roles_bp.route('/ver/<int:id>')
@admin_required
def ver(id):
    rol = Rol.query.get_or_404(id)
    roles = Rol.query.all()
    return render_template('roles.html', listaRoles=roles, rol=rol, readonly=True)

@roles_bp.route('/cambiarEstado/<int:id>')
@admin_required
def cambiar_estado(id):
    rol = Rol.query.get_or_404(id)
    if rol.estado == 'Activo':
        rol.estado = 'Inactivo'
    else:
        rol.estado = 'Activo'
    db.session.commit()
    return redirect(url_for('roles.listar_roles'))
