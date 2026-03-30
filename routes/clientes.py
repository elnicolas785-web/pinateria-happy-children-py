from flask import render_template, request, redirect, url_for # type: ignore
from routes import clientes_bp # type: ignore
from models import Cliente # type: ignore
from extensions import db # type: ignore
import datetime

@clientes_bp.route('/')
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', listaClientes=clientes, cliente=Cliente(), readonly=False)

@clientes_bp.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form.get('codigo')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    tipo_doc = request.form.get('tipo_documento')
    num_doc = request.form.get('numero_documento')
    email = request.form.get('email')

    try:
        nuevo_cliente = Cliente(
            codigo=codigo,
            nombres=nombres,
            apellidos=apellidos,
            tipo_documento=tipo_doc,
            numero_documento=num_doc,
            email=email,
            estado='Activo',
            fecha_registro=datetime.date.today()
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    return redirect(url_for('clientes.listar_clientes'))
