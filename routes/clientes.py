from flask import render_template, request, redirect, url_for, flash, current_app
from routes import clientes_bp
from models import Cliente
from extensions import mail, db, employee_required
import datetime
import time 
from flask_login import login_required, current_user
from flask_mail import Message

@clientes_bp.route('/')
@employee_required
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=None, readonly=False)

@clientes_bp.route('/editar/<int:id>')
@employee_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=cliente, readonly=False)

@clientes_bp.route('/ver/<int:id>')
@employee_required
def ver_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=cliente, readonly=True)

@clientes_bp.route('/cambiarEstado/<int:id>')
@employee_required
def cambiar_estado(id):
    cliente = Cliente.query.get_or_404(id)
    cliente.estado = 'Inactivo' if cliente.estado == 'Activo' else 'Activo'
    db.session.commit()
    flash('Estado del cliente actualizado.', 'success')
    return redirect(url_for('clientes.listar_clientes'))

@clientes_bp.route('/guardar', methods=['POST'])
@employee_required
def guardar():
    id_cliente = request.form.get('id_cliente')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    tipo_doc = request.form.get('tipo_documento')
    num_doc = request.form.get('numero_documento')
    email = request.form.get('email')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    estado = request.form.get('estado', 'Activo')

    try:
        if id_cliente:
            # --- EDITAR CLIENTE ---
            cliente = Cliente.query.get(id_cliente)
            if cliente:
                cliente.nombres = nombres
                cliente.apellidos = apellidos
                cliente.tipo_documento = tipo_doc
                cliente.numero_documento = num_doc
                cliente.email = email
                cliente.telefono = telefono
                cliente.direccion = direccion
                cliente.estado = estado
                flash('Cliente actualizado correctamente.', 'success')
        else:
            # --- CREAR CLIENTE NUEVO (Autogenerar Código) ---
            
            ultimo_cliente = Cliente.query.order_by(Cliente.id_cliente.desc()).first()
            
            if ultimo_cliente and ultimo_cliente.codigo:
                try:
                    numero_actual = int(ultimo_cliente.codigo.replace('CLI', ''))
                    nuevo_numero = numero_actual + 1
                except:
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            nuevo_codigo = f"CLI{str(nuevo_numero).zfill(3)}"

            nuevo_cliente = Cliente(
                codigo=nuevo_codigo, 
                nombres=nombres,
                apellidos=apellidos,
                tipo_documento=tipo_doc,
                numero_documento=num_doc,
                email=email,
                telefono=telefono,
                direccion=direccion,
                estado='Activo',
                fecha_registro=datetime.date.today()
            )
            db.session.add(nuevo_cliente)
            flash(f'Cliente creado con código {nuevo_codigo}.', 'success')
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('Ocurrió un error al guardar el cliente.', 'danger')

    return redirect(url_for('clientes.listar_clientes'))

@clientes_bp.route('/buscar', methods=['GET'])
@employee_required
def buscar():
    busqueda = request.args.get('busqueda', '')
    if busqueda:
        clientes = Cliente.query.filter(
            db.or_(
                Cliente.nombres.ilike(f'%{busqueda}%'),
                Cliente.apellidos.ilike(f'%{busqueda}%'),
                (Cliente.nombres + ' ' + Cliente.apellidos).ilike(f'%{busqueda}%'),
                Cliente.numero_documento.ilike(f'%{busqueda}%'),
                Cliente.codigo.ilike(f'%{busqueda}%')
            )
        ).order_by(Cliente.fecha_registro.desc()).all()
    else:
        clientes = Cliente.query.order_by(Cliente.fecha_registro.desc()).all()
        
    return render_template('clientes.html', listaClientes=clientes, cliente=None, readonly=False)


@clientes_bp.route('/enviar-publicidad-masiva')
@employee_required
def enviar_publicidad():
    """Envía un correo HTML profesional solo a clientes con estado 'Activo'."""
    clientes = Cliente.query.all()
    
    if not clientes:
        flash('No hay clientes registrados.', 'warning')
        return redirect(url_for('clientes.listar_clientes'))

    enviados = 0
    errores = 0

    try:
        with mail.connect() as conn:
            for cliente in clientes:
                # Solo envía si el estado es 'Activo'
                if cliente.estado == 'Activo' and cliente.email:
                    try:
                        msg = Message(
                            subject="🎈 ¡Novedades en Happy Children!",
                            sender="hchildren815@gmail.com",
                            recipients=[cliente.email]
                        )
                        
                        # EL MENSAJE BONITO (HTML)
                        msg.html = f"""
                        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 15px; overflow: hidden;">
                            <div style="background-color: #1565C0; padding: 20px; text-align: center;">
                                <h1 style="color: white; margin: 0;">Happy Children 🎈</h1>
                            </div>
                            <div style="padding: 30px; color: #333;">
                                <h2 style="color: #1565C0;">¡Hola, {cliente.nombres}!</h2>
                                <p style="font-size: 16px; line-height: 1.6;">
                                    En <strong>Happy Children</strong> queremos que tus celebraciones sean mágicas. 
                                    Tenemos nuevas piñatas personalizadas, globos y todo lo que necesitas para tu fiesta.
                                </p>
                                <div style="background-color: #f8f9fa; border-left: 4px solid #1565C0; padding: 15px; margin: 20px 0;">
                                    <p style="margin: 0; font-weight: bold;">🎁 ¡Regalo Especial!</p>
                                    <p style="margin: 5px 0 0;">Muestra este correo en tu próxima compra y recibe un 10% de descuento.</p>
                                </div>
                                <p style="font-size: 14px; color: #666;">Te esperamos en nuestra tienda física para asesorarte con la mejor decoración.</p>
                            </div>
                            <div style="background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #888;">
                                <p style="margin: 0;">&copy; 2026 Piñatería Happy Children | Gestión de Clientes</p>
                            </div>
                        </div>
                        """
                        
                        conn.send(msg)
                        enviados += 1
                        time.sleep(0.5) 
                    except Exception as e:
                        print(f"Error enviando a {cliente.email}: {e}")
                        errores += 1

        flash(f'Éxito: {enviados} correos enviados a clientes activos.', 'success')
    except Exception as e:
        flash(f'Error al conectar con el servidor: {str(e)}', 'danger')

    return redirect(url_for('clientes.listar_clientes'))