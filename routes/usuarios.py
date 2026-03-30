from flask import render_template, request, redirect, url_for # type: ignore
from routes import usuarios_bp # type: ignore
from models import UsuarioCliente, Cliente, Rol # type: ignore
from extensions import db # type: ignore
import datetime # type: ignore

@usuarios_bp.route('/')
def listar_usuarios():
    usuarios = UsuarioCliente.query.all()
    clientes = Cliente.query.all()
    roles = Rol.query.all()
    return render_template('usuarios.html', listaUsuarios=usuarios, listaClientes=clientes, listaRoles=roles, usuario=UsuarioCliente(), readonly=False)

@usuarios_bp.route('/guardar', methods=['POST'])
def guardar():
    id_cliente = request.form.get('cliente.id_cliente')
    nombre_usuario = request.form.get('nombreUsuario')
    contrasena = request.form.get('contrasena')
    id_rol = request.form.get('rol.id_rol')
    codigo = request.form.get('codigo')

    nuevo_usuario = UsuarioCliente(
        codigo=codigo,
        id_cliente=id_cliente,
        nombre_usuario=nombre_usuario,
        contrasena=contrasena,
        id_rol=id_rol,
        estado='Activo',
        fecha_creacion=datetime.date.today()
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return redirect(url_for('usuarios.listar_usuarios'))
