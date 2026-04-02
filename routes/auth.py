from flask import render_template, request, redirect, url_for, flash # type: ignore
from flask_login import login_user, logout_user # type: ignore
from routes import auth_bp # type: ignore
from models import Cliente, UsuarioCliente, Rol, Empleado # type: ignore
from extensions import db # type: ignore
import datetime

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validar Cliente
        cliente_u = UsuarioCliente.query.filter_by(nombre_usuario=username).first()
        if cliente_u and cliente_u.contrasena == password:
            login_user(cliente_u)
            flash(f'¡Bienvenido {cliente_u.cliente.nombres}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
            
        # Validar Empleado
        empleado = Empleado.query.filter_by(nombre_usuario=username).first()
        if empleado and empleado.contrasena_hash == password:
            login_user(empleado)
            rol_nombre = empleado.rol.nombre_rol.capitalize() if empleado.rol else 'Empleado'
            if rol_nombre.upper() in ['ADMINISTRADOR', 'ADMIN']:
                rol_nombre = 'Administrador'
            flash(f'¡Bienvenido {rol_nombre} {empleado.nombres}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
            
        return render_template('login.html', errorGeneral="Usuario o contraseña incorrectos")
        
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        tipoDocumento = request.form.get('tipoDocumento')
        numeroDocumento = request.form.get('numeroDocumento')
        email = request.form.get('email')
        password = request.form.get('password')

        # Simple validation
        if not firstname or not email or not password:
            return render_template('registro.html', errorGeneral="Complete todos los campos requeridos.")

        # Check existing
        if UsuarioCliente.query.filter_by(nombre_usuario=email).first() or Cliente.query.filter_by(email=email).first():
            return render_template('registro.html', errorGeneral="El usuario o correo ya existe.")

        rol_cliente = Rol.query.filter(Rol.nombre_rol.ilike('CLIENTE')).first()

        cliente = Cliente(
            nombres=firstname,
            apellidos=lastname,
            numero_documento=numeroDocumento,
            tipo_documento=tipoDocumento,
            email=email,
            password=password,
            estado="Activo",
            fecha_registro=datetime.date.today(),
            codigo=f"CLI-{int(datetime.datetime.now().timestamp() * 1000) % 10000:04d}"
        )
        db.session.add(cliente)
        db.session.flush()

        usuario = UsuarioCliente(
            id_cliente=cliente.id_cliente,
            nombre_usuario=email,
            contrasena=password, # Asumiendo texto plano por ahora (migracion)
            id_rol=rol_cliente.id_rol if rol_cliente else 1,
            estado="Activo",
            codigo=f"USR-{int(datetime.datetime.now().timestamp() * 1000) % 10000:04d}"
        )
        db.session.add(usuario)
        db.session.commit()

        flash('¡Registro exitoso! Ya puedes iniciar sesión en tu nueva cuenta.', 'success')
        return redirect(url_for('auth.login', registered=True))
        
    return render_template('registro.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.logout_success'))

@auth_bp.route('/logout-success')
def logout_success():
    return render_template('logout_success.html')
