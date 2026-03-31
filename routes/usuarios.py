from flask import render_template, request, redirect, url_for, flash # type: ignore
from routes import usuarios_bp # type: ignore
from models import UsuarioCliente, Cliente, Rol # type: ignore
from extensions import db # type: ignore
import datetime # type: ignore
import uuid

@usuarios_bp.route('/')
def listar_usuarios():
    usuarios = UsuarioCliente.query.all()
    clientes = Cliente.query.all()
    roles = Rol.query.all()
    return render_template('usuarios.html', listaUsuarios=usuarios, listaClientes=clientes, listaRoles=roles, usuario=UsuarioCliente(), readonly=False)

@usuarios_bp.route('/guardar', methods=['POST'])
def guardar():
    id_usuario = request.form.get('id_usuario')
    id_cliente = request.form.get('id_cliente')
    nombre_usuario = request.form.get('nombreUsuario')
    contrasena = request.form.get('contrasena')
    id_rol = request.form.get('id_rol')
    codigo = request.form.get('codigo')
    estado = request.form.get('estado', 'Activo')

    if id_usuario:
        usuario = UsuarioCliente.query.get(id_usuario)
        if usuario:
            usuario.id_cliente = id_cliente
            usuario.nombre_usuario = nombre_usuario
            if contrasena:  # Solo act si la pasa
                usuario.contrasena = contrasena
            usuario.id_rol = id_rol
            usuario.estado = estado
    else:
        if not codigo:
            codigo = f"USR-{uuid.uuid4().hex[:6].upper()}"
            
        nuevo_usuario = UsuarioCliente(
            codigo=codigo,
            id_cliente=id_cliente,
            nombre_usuario=nombre_usuario,
            contrasena=contrasena,
            id_rol=id_rol,
            estado=estado,
            fecha_creacion=datetime.date.today()
        )
        db.session.add(nuevo_usuario)

    db.session.commit()
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.route('/buscar', methods=['GET'])
def buscar():
    busqueda = request.args.get('busqueda', '')
    clientes = Cliente.query.all()
    roles = Rol.query.all()
    if busqueda:
        usuarios = UsuarioCliente.query.filter(UsuarioCliente.nombre_usuario.ilike(f'%{busqueda}%')).all()
    else:
        usuarios = UsuarioCliente.query.all()
    return render_template('usuarios.html', listaUsuarios=usuarios, listaClientes=clientes, listaRoles=roles, usuario=UsuarioCliente(), readonly=False)

@usuarios_bp.route('/editar/<int:id>')
def editar(id):
    usuario = UsuarioCliente.query.get_or_404(id)
    usuarios = UsuarioCliente.query.all()
    clientes = Cliente.query.all()
    roles = Rol.query.all()
    return render_template('usuarios.html', listaUsuarios=usuarios, listaClientes=clientes, listaRoles=roles, usuario=usuario, readonly=False)

@usuarios_bp.route('/ver/<int:id>')
def ver(id):
    usuario = UsuarioCliente.query.get_or_404(id)
    usuarios = UsuarioCliente.query.all()
    clientes = Cliente.query.all()
    roles = Rol.query.all()
    return render_template('usuarios.html', listaUsuarios=usuarios, listaClientes=clientes, listaRoles=roles, usuario=usuario, readonly=True)

@usuarios_bp.route('/cambiarEstado/<int:id>')
def cambiar_estado(id):
    usuario = UsuarioCliente.query.get_or_404(id)
    if usuario.estado == 'Activo':
        usuario.estado = 'Inactivo'
    else:
        usuario.estado = 'Activo'
    db.session.commit()
    return redirect(url_for('usuarios.listar_usuarios'))
