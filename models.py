import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from flask_login import UserMixin
import datetime
class Rol(db.Model):
    __tablename__ = 'rol'
    id_rol = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre_rol = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='Activo')

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    tipo_documento = db.Column(db.String(20), nullable=False)
    numero_documento = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    estado = db.Column(db.String(20), nullable=False, default='Activo')
    direccion = db.Column(db.String(255))
    fecha_registro = db.Column(db.Date, nullable=False, default=datetime.date.today)
    password = db.Column(db.String(255))

class UsuarioCliente(db.Model, UserMixin):
    __tablename__ = 'usuario_cliente'
    id_usuario = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='Activo')
    fecha_creacion = db.Column(db.Date, nullable=False, default=datetime.date.today)

    cliente = db.relationship('Cliente', backref=db.backref('usuarios_cliente', lazy=True))
    rol = db.relationship('Rol')
    
    def get_id(self):
        return f"UC-{self.id_usuario}"

class Empleado(db.Model, UserMixin):
    __tablename__ = 'empleado'
    id_empleado = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    tipo_documento = db.Column(db.String(50), nullable=False)
    documento_identidad = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    fecha_contratacion = db.Column(db.Date, nullable=False, default=datetime.date.today)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id_rol'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='Activo')
    fecha_creacion = db.Column(db.Date, nullable=False, default=datetime.date.today)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)

    rol = db.relationship('Rol')
    
    def get_id(self):
        return f"EMP-{self.id_empleado}"

class Login(db.Model):
    __tablename__ = 'login'
    id_login = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleado.id_empleado'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario_cliente.id_usuario'))
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)

    empleado = db.relationship('Empleado')
    usuario = db.relationship('UsuarioCliente')

class CategoriaProducto(db.Model):
    __tablename__ = 'categoria_producto'
    id_categoria = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    activo = db.Column(db.String(20), nullable=False, default='Activo')

class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.String(255))
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria_producto.id_categoria'), nullable=False)
    precio_compra = db.Column(db.Numeric(10, 2), nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    stock_actual = db.Column(db.Integer, nullable=False)
    stock_minimo = db.Column(db.Integer, nullable=False)
    unidad_medida = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.String(20), nullable=False, default='Activo')
    fecha_creacion = db.Column(db.Date, nullable=False, default=datetime.date.today)
    imagen_url = db.Column(db.String(500))

    categoria = db.relationship('CategoriaProducto')

class Pedido(db.Model):
    __tablename__ = 'pedido'
    id_pedido = db.Column(db.Integer, primary_key=True)
    numero_pedido = db.Column(db.String(30), unique=True, nullable=False)
    fecha_pedido = db.Column(db.Date, nullable=False, default=datetime.date.today)
    fecha_entrega_esperada = db.Column(db.Date)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='Pendiente')
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    direccion_entrega = db.Column(db.String(255))
    observaciones = db.Column(db.String(255))

    cliente = db.relationship('Cliente')

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    id_detalle_pedido = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id_pedido'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    pedido = db.relationship('Pedido', backref=db.backref('detalles', lazy='dynamic'))
    producto = db.relationship('Producto')

class Venta(db.Model):
    __tablename__ = 'venta'
    id_venta = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(30), unique=True, nullable=False)
    fecha_venta = db.Column(db.Date, nullable=False, default=datetime.date.today)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleado.id_empleado'), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    metodo_pago = db.Column(db.String(30), nullable=False)
    observaciones = db.Column(db.String(255))

    cliente = db.relationship('Cliente')
    empleado = db.relationship('Empleado')

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id_detalle = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    id_venta = db.Column(db.Integer, db.ForeignKey('venta.id_venta'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    venta = db.relationship('Venta', backref=db.backref('detalles_venta', lazy='dynamic'))
    producto = db.relationship('Producto')

class MovimientoInventario(db.Model):
    __tablename__ = 'movimiento_inventario'
    id_movimiento = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    tipo_movimiento = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    stock_anterior = db.Column(db.Integer, nullable=False)
    stock_nuevo = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255))
    id_empleado = db.Column(db.Integer, db.ForeignKey('empleado.id_empleado'), nullable=False)
    fecha_movimiento = db.Column(db.Date, nullable=False, default=datetime.date.today)

    producto = db.relationship('Producto')
    empleado = db.relationship('Empleado')
