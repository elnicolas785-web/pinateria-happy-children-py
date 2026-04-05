from flask import render_template, request, redirect, url_for, flash # type: ignore
from routes import empleados_bp # type: ignore
from models import Empleado, Rol # type: ignore
from extensions import db, admin_required # Importamos admin_required
from flask_login import login_required, current_user # type: ignore
import datetime

@empleados_bp.route('/')
@admin_required
def listar_empleados():
    empleados = Empleado.query.all()
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=empleados, listaRoles=roles, empleado=None, readonly=False)

@empleados_bp.route('/ver/<int:id>')
@admin_required
def ver_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    lista_empleados = Empleado.query.all()
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=lista_empleados, listaRoles=roles, empleado=empleado, readonly=True)

@empleados_bp.route('/editar/<int:id>')
@admin_required
def editar_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    lista_empleados = Empleado.query.all()
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=lista_empleados, listaRoles=roles, empleado=empleado, readonly=False)

@empleados_bp.route('/cambiarEstado/<int:id>')
@admin_required
def cambiar_estado(id):
    empleado = Empleado.query.get_or_404(id)
    empleado.estado = 'Inactivo' if empleado.estado == 'Activo' else 'Activo'
    db.session.commit()
    flash('Estado del empleado actualizado.', 'success')
    return redirect(url_for('empleados.listar_empleados'))

@empleados_bp.route('/guardar', methods=['POST'])
@admin_required
def guardar():
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
        # --- LÓGICA PARA EDITAR ---
        empleado = Empleado.query.get(id_empleado)
        if empleado:
            # Validar que el nuevo email no esté ocupado por OTRO empleado
            email_duplicado = Empleado.query.filter(Empleado.email == email, Empleado.id_empleado != id_empleado).first()
            if email_duplicado:
                flash(f'Error: El correo {email} ya pertenece a otro empleado.', 'danger')
                return redirect(url_for('empleados.listar_empleados'))

            empleado.nombres = nombres
            empleado.apellidos = apellidos
            empleado.tipo_documento = tipo_doc
            empleado.documento_identidad = doc_id
            empleado.email = email
            empleado.id_rol = id_rol
            empleado.nombre_usuario = nombre_usuario
            empleado.estado = estado
            if contrasena_hash:
                empleado.contrasena_hash = contrasena_hash
            
            db.session.commit()
            flash('Empleado actualizado correctamente.', 'success')
    else:
        # --- LÓGICA PARA CREAR NUEVO ---
        
        # 1. Validar si el email ya existe
        if Empleado.query.filter_by(email=email).first():
            flash(f'Error: El correo {email} ya está registrado.', 'danger')
            return redirect(url_for('empleados.listar_empleados'))
        
        # 2. Validar si el documento de identidad ya existe
        if Empleado.query.filter_by(documento_identidad=doc_id).first():
            flash(f'Error: El documento {doc_id} ya está registrado.', 'danger')
            return redirect(url_for('empleados.listar_empleados'))

        # 3. Si todo está bien, crear
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
        db.session.commit() # Commit para el nuevo registro
        flash('Empleado creado correctamente.', 'success')
    
    if from_dashboard:
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('empleados.listar_empleados'))


@empleados_bp.route('/buscar', methods=['GET'])
@admin_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        empleados = Empleado.query.filter(
            db.or_(
                Empleado.nombres.ilike(f'%{busqueda}%'),
                Empleado.apellidos.ilike(f'%{busqueda}%'),
                (Empleado.nombres + ' ' + Empleado.apellidos).ilike(f'%{busqueda}%'),
                Empleado.documento_identidad.ilike(f'%{busqueda}%')
            )
        ).order_by(Empleado.fecha_contratacion.desc()).all()
    else:
        empleados = Empleado.query.order_by(Empleado.fecha_contratacion.desc()).all()
        
    from models import Rol
    roles = Rol.query.all()
    return render_template('empleados.html', listaEmpleados=empleados, listaRoles=roles, empleado=None, readonly=False)

