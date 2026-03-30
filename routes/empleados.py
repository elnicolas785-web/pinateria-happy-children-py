from flask import render_template, request, redirect, url_for # type: ignore
from routes import empleados_bp # type: ignore
from models import Empleado, Rol # type: ignore
from extensions import db # type: ignore
import datetime # type: ignore

@empleados_bp.route('/')
def listar_empleados():
    empleados = Empleado.query.all()
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=empleados, listaRoles=roles, empleado=Empleado(), readonly=False)

@empleados_bp.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form.get('codigo')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    tipo_doc = request.form.get('tipo_documento')
    doc_id = request.form.get('documento_identidad')
    email = request.form.get('email')
    telefono = request.form.get('telefono')
    id_rol = request.form.get('rol.id_rol')

    nuevo_emp = Empleado(
        codigo=codigo,
        nombres=nombres,
        apellidos=apellidos,
        tipo_documento=tipo_doc,
        documento_identidad=doc_id,
        email=email,
        telefono=telefono,
        fecha_contratacion=datetime.date.today(),
        id_rol=id_rol,
        estado='Activo',
        fecha_creacion=datetime.date.today(),
        nombre_usuario=email,
        contrasena_hash='por_defecto'
    )
    db.session.add(nuevo_emp)
    db.session.commit()
    return redirect(url_for('empleados.listar_empleados'))
