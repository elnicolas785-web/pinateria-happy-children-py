from flask import render_template, request, redirect, url_for, flash, session, current_app # type: ignore
from flask_login import login_user, logout_user # type: ignore
from routes import auth_bp # type: ignore
from models import Cliente, UsuarioCliente, Rol, Empleado # type: ignore
from extensions import db, mail # Se agrega mail a las extensiones
from flask_mail import Message # Para enviar el correo
from itsdangerous import URLSafeTimedSerializer as Serializer # Para el token seguro
import datetime
import re


def enviar_email_restablecimiento(usuario, tipo):
    s = Serializer(current_app.config['SECRET_KEY'])
    
    # Definimos el ID según el tipo
    user_id = usuario.id_cliente if tipo == 'cliente' else usuario.id_empleado
    token = s.dumps({'user_id': user_id, 'tipo': tipo}, salt='pw-reset')
    
    #Verifica que ambos modelos tengan el atributo .email
    destinatario = usuario.email 
    
    print(f"DEBUG: Intentando enviar correo de recuperación a: {destinatario}")

    msg = Message(
        subject='Restablecer Contraseña - Happy Children',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[destinatario]
    )
    
    enlace = url_for('auth.restablecer_token', token=token, _external=True)
    
    msg.html = f"""
    <div style="font-family: Arial; border: 1px solid #ddd; padding: 20px; border-radius: 10px; max-width: 500px;">
        <h2 style="color: #1565C0; text-align: center;">Happy Children 🎈</h2>
        <hr style="border: 0; border-top: 1px solid #eee;">
        <p>Hola, recibimos una solicitud para restablecer tu contraseña.</p>
        <p>Haz clic en el botón de abajo para continuar. Este enlace expirará en 30 minutos.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{enlace}" style="background-color: #1565C0; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Restablecer Contraseña</a>
        </div>
        <p style="font-size: 12px; color: #777;">Si no solicitaste este cambio, puedes ignorar este correo de forma segura.</p>
    </div>
    """
    
    try:
        mail.send(msg)
        print("DEBUG: Correo enviado exitosamente.")
    except Exception as e:
        print(f"DEBUG ERROR: No se pudo enviar el correo. Motivo: {e}")


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

        if not all([firstname, lastname, numeroDocumento, email, password]):
            return render_template('registro.html', errorGeneral="Complete todos los campos requeridos.")

        doc_existente = Cliente.query.filter_by(numero_documento=numeroDocumento).first()
        if doc_existente:
            return render_template('registro.html', errorGeneral="El número de documento ya se encuentra registrado.")

        email_en_cliente = Cliente.query.filter_by(email=email).first()
        email_en_usuario = UsuarioCliente.query.filter_by(nombre_usuario=email).first()
        
        if email_en_cliente or email_en_usuario:
            return render_template('registro.html', errorGeneral="El correo electrónico ya está en uso.")

        try:
            rol_cliente = Rol.query.filter(Rol.nombre_rol.ilike('CLIENTE')).first()

            nuevo_cliente = Cliente(
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
            db.session.add(nuevo_cliente)
            db.session.flush()

            nuevo_usuario = UsuarioCliente(
                id_cliente=nuevo_cliente.id_cliente,
                nombre_usuario=email,
                contrasena=password,
                id_rol=rol_cliente.id_rol if rol_cliente else 1,
                estado="Activo",
                codigo=f"USR-{int(datetime.datetime.now().timestamp() * 1000) % 10000:04d}"
            )
            db.session.add(nuevo_usuario)
            db.session.commit()

            flash('¡Registro exitoso! Ya puedes iniciar sesión en tu nueva cuenta.', 'success')
            return redirect(url_for('auth.login', registered=True))

        except Exception as e:
            db.session.rollback()
            print(f"Error en el registro: {str(e)}")
            return render_template('registro.html', errorGeneral="Ocurrió un error inesperado al procesar tu registro.")
        
    return render_template('registro.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.logout_success'))

@auth_bp.route('/logout-success')
def logout_success():
    return render_template('logout_success.html')


import re

# Página para pedir el correo (La que va en el Login)
@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        cliente = Cliente.query.filter_by(email=email).first()
        empleado = Empleado.query.filter_by(email=email).first()
        
        if cliente:
            enviar_email_restablecimiento(cliente, 'cliente')
            flash('Se ha enviado un correo con instrucciones.', 'info')
            return redirect(url_for('auth.login'))
        elif empleado:
            enviar_email_restablecimiento(empleado, 'empleado')
            flash('Se ha enviado un correo con instrucciones.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('No existe ninguna cuenta asociada a ese correo.', 'warning')
            
    return render_template('reset_request.html')

# Página para poner la clave nueva (La que llega por correo)
@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def restablecer_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt='pw-reset', max_age=1800)
        user_id = data['user_id']
        tipo = data['tipo']
    except:
        flash('El enlace es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.reset_request'))
    
    if request.method == 'POST':
        nueva_clave = request.form.get('password')
        confirmar = request.form.get('confirm_password')
        
        if nueva_clave != confirmar:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('reset_password.html')

        # VALIDACIONES ESTRICTAS
        reglas = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(reglas, nueva_clave):
            flash('Requisito: 8 caracteres, Mayúscula, Minúscula, Número y Carácter especial.', 'warning')
            return render_template('reset_password.html')

        try:
            if tipo == 'cliente':
                usuario_c = UsuarioCliente.query.filter_by(id_cliente=user_id).first()
                cliente = Cliente.query.get(user_id)
                if usuario_c: usuario_c.contrasena = nueva_clave
                if cliente: cliente.password = nueva_clave
            else:
                empleado = Empleado.query.get(user_id)
                if empleado: empleado.contrasena_hash = nueva_clave
                
            db.session.commit()
            flash('Tu contraseña ha sido actualizada exitosamente.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la contraseña.', 'danger')
        
    return render_template('reset_password.html')