from flask import render_template, request, redirect, url_for, flash, session # type: ignore
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
            session.pop('_flashes', None)
            login_user(cliente_u)
            flash(f'¡Bienvenido {cliente_u.cliente.nombres}!', 'success')
            return redirect(url_for('dashboard.dashboard'))
            
        # Validar Empleado
        empleado = Empleado.query.filter_by(nombre_usuario=username).first()
        if empleado and empleado.contrasena_hash == password:
            session.pop('_flashes', None)
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

        # Validación de campos obligatorios
        if not all([firstname, lastname, numeroDocumento, email, password]):
            return render_template('registro.html', errorGeneral="Complete todos los campos requeridos.")

        # Validación de duplicados (Crucial para evitar el IntegrityError)
        # Revisa si el número de documento ya existe en la base de datos
        doc_existente = Cliente.query.filter_by(numero_documento=numeroDocumento).first()
        if doc_existente:
            return render_template('registro.html', errorGeneral="El número de documento ya se encuentra registrado.")

        # Revisa si el correo ya existe en Cliente o UsuarioCliente
        email_en_cliente = Cliente.query.filter_by(email=email).first()
        email_en_usuario = UsuarioCliente.query.filter_by(nombre_usuario=email).first()
        
        if email_en_cliente or email_en_usuario:
            return render_template('registro.html', errorGeneral="El correo electrónico ya está en uso.")

        # Proceso de registro con manejo de errores
        try:
            rol_cliente = Rol.query.filter(Rol.nombre_rol.ilike('CLIENTE')).first()

            # Creación del objeto Cliente
            nuevo_cliente = Cliente(
                nombres=firstname,
                apellidos=lastname,
                numero_documento=numeroDocumento,
                tipo_documento=tipoDocumento,
                email=email,
                password=password, # Considera usar un hash en el futuro
                estado="Activo",
                fecha_registro=datetime.date.today(),
                codigo=f"CLI-{int(datetime.datetime.now().timestamp() * 1000) % 10000:04d}"
            )
            db.session.add(nuevo_cliente)
            # flush() genera el ID del cliente sin cerrar la transacción
            db.session.flush()

            # Creación del objeto UsuarioCliente vinculado al cliente
            nuevo_usuario = UsuarioCliente(
                id_cliente=nuevo_cliente.id_cliente,
                nombre_usuario=email,
                contrasena=password,
                id_rol=rol_cliente.id_rol if rol_cliente else 1,
                estado="Activo",
                codigo=f"USR-{int(datetime.datetime.now().timestamp() * 1000) % 10000:04d}"
            )
            db.session.add(nuevo_usuario)
            
            # Commit final para guardar ambos registros
            db.session.commit()

            flash('¡Registro exitoso! Ya puedes iniciar sesión en tu nueva cuenta.', 'success')
            return redirect(url_for('auth.login', registered=True))

        except Exception as e:
            # Si algo falla (ej. error de base de datos), limpiamos la sesión
            db.session.rollback()
            print(f"Error en el registro: {str(e)}") # Útil para depurar en consola
            return render_template('registro.html', errorGeneral="Ocurrió un error inesperado al procesar tu registro.")
        
    return render_template('registro.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.logout_success'))

@auth_bp.route('/logout-success')
def logout_success():
    return render_template('logout_success.html')
