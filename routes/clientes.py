from flask import render_template, request, redirect, url_for, flash
from routes import clientes_bp
from models import Cliente
from extensions import db
import datetime
from flask_login import login_required, current_user

@clientes_bp.route('/')
@login_required
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=None, readonly=False)

@clientes_bp.route('/editar/<int:id>')
@login_required
def editar_cliente(id):
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    cliente = Cliente.query.get_or_404(id)
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=cliente, readonly=False)

@clientes_bp.route('/ver/<int:id>')
@login_required
def ver_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=cliente, readonly=True)

@clientes_bp.route('/cambiarEstado/<int:id>')
@login_required
def cambiar_estado(id):
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
        
    cliente = Cliente.query.get_or_404(id)
    cliente.estado = 'Inactivo' if cliente.estado == 'Activo' else 'Activo'
    db.session.commit()
    flash('Estado del cliente actualizado.', 'success')
    return redirect(url_for('clientes.listar_clientes'))

@clientes_bp.route('/guardar', methods=['POST'])
@login_required
def guardar():
    if not current_user.rol or current_user.rol.nombre_rol.upper() not in ['ADMINISTRADOR', 'ADMIN', 'EMPLEADO']:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    id_cliente = request.form.get('id_cliente')
    codigo = request.form.get('codigo')
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
            cliente = Cliente.query.get(id_cliente)
            if cliente:
                if codigo:
                    cliente.codigo = codigo
                if nombres:
                    cliente.nombres = nombres
                if apellidos:
                    cliente.apellidos = apellidos
                if tipo_doc:
                    cliente.tipo_documento = tipo_doc
                if num_doc:
                    cliente.numero_documento = num_doc
                if email:
                    cliente.email = email
                if telefono is not None:
                    cliente.telefono = telefono
                if direccion is not None:
                    cliente.direccion = direccion
                cliente.estado = estado
                flash('Cliente actualizado correctamente.', 'success')
        else:
            nuevo_cliente = Cliente(
                codigo=codigo,
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
            flash('Cliente creado correctamente.', 'success')
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('Ocurrió un error al guardar el cliente.', 'danger')

    return redirect(url_for('clientes.listar_clientes'))


@clientes_bp.route('/buscar', methods=['GET'])
@login_required
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
