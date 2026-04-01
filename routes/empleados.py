from flask import render_template, request, redirect, url_for, flash # type: ignore
from routes import empleados_bp # type: ignore
from models import Empleado, Rol # type: ignore
from extensions import db # type: ignore
from flask_login import login_required, current_user # type: ignore
import datetime

@empleados_bp.route('/')
@login_required
def listar_empleados():
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado. No eres administrador ni empleado con permisos.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    empleados = Empleado.query.all()
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=empleados, listaRoles=roles, empleado=None, readonly=False)

@empleados_bp.route('/ver/<int:id>')
@login_required
def ver_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    lista_empleados = Empleado.query.all()
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=lista_empleados, listaRoles=roles, empleado=empleado, readonly=True)

@empleados_bp.route('/editar/<int:id>')
@login_required
def editar_empleado(id):
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    empleado = Empleado.query.get_or_404(id)
    lista_empleados = Empleado.query.all()
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=lista_empleados, listaRoles=roles, empleado=empleado, readonly=False)

@empleados_bp.route('/cambiarEstado/<int:id>')
@login_required
def cambiar_estado(id):
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    empleado = Empleado.query.get_or_404(id)
    empleado.estado = 'Inactivo' if empleado.estado == 'Activo' else 'Activo'
    db.session.commit()
    flash('Estado del empleado actualizado.', 'success')
    return redirect(url_for('empleados.listar_empleados'))

@empleados_bp.route('/guardar', methods=['POST'])
@login_required
def guardar():
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    from_dashboard = request.form.get('fromDashboard')
    id_empleado = request.form.get('id_empleado')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    tipo_doc = request.form.get('tipo_documento')
    doc_id = request.form.get('documento_identidad')
    email = request.form.get('email')
    id_rol = request.form.get('rol.id_rol')
    nombre_usuario = request.form.get('nombre_usuario')
    contrasena_hash = request.form.get('contrasena_hash')
    estado = request.form.get('estado', 'Activo')

    if id_empleado:
        # Editar existente
        empleado = Empleado.query.get(id_empleado)
        if empleado:
            empleado.nombres = nombres
            empleado.apellidos = apellidos
            empleado.tipo_documento = tipo_doc
            empleado.documento_identidad = doc_id
            empleado.email = email
            empleado.id_rol = id_rol
            empleado.nombre_usuario = nombre_usuario
            empleado.estado = estado
            if contrasena_hash:  # Solo actualiza si ingresó una nueva
                empleado.contrasena_hash = contrasena_hash
            flash('Empleado actualizado correctamente.', 'success')
    else:
        # Crear nuevo
        nuevo_codigo = f"EMP-{int(datetime.datetime.now().timestamp() * 1000) % 10000:04d}"
        nuevo_emp = Empleado(
            codigo=nuevo_codigo,
            nombres=nombres,
            apellidos=apellidos,
            tipo_documento=tipo_doc,
            documento_identidad=doc_id,
            email=email,
            fecha_contratacion=datetime.date.today(),
            id_rol=id_rol,
            estado='Activo',
            fecha_creacion=datetime.date.today(),
            nombre_usuario=nombre_usuario,
            contrasena_hash=contrasena_hash if contrasena_hash else '12345'
        )
        db.session.add(nuevo_emp)
        flash('Empleado creado correctamente.', 'success')

    db.session.commit()
    
    if from_dashboard:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('empleados.listar_empleados'))
