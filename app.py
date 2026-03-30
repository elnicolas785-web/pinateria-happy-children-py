"""
Main application module for the Flask app.
"""
import os
import sys

# Ensure the app directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from extensions import db, login_manager
from routes import (
    auth_bp, dashboard_bp, productos_bp, clientes_bp,
    categorias_bp, empleados_bp, roles_bp, usuarios_bp,
    ventas_bp, pedidos_bp, cart_bp, reportes_bp
)
from models import UsuarioCliente, Empleado


def create_app():
    """Create and configure an instance of the Flask application."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(flask_app)
    login_manager.init_app(flask_app)

    # Registrar blueprints (rutas)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(dashboard_bp)
    flask_app.register_blueprint(productos_bp, url_prefix='/productos')
    flask_app.register_blueprint(clientes_bp, url_prefix='/clientes')
    flask_app.register_blueprint(categorias_bp, url_prefix='/categorias')
    flask_app.register_blueprint(empleados_bp, url_prefix='/empleados')
    flask_app.register_blueprint(roles_bp, url_prefix='/roles')
    flask_app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    flask_app.register_blueprint(ventas_bp, url_prefix='/ventas')
    flask_app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
    flask_app.register_blueprint(cart_bp, url_prefix='/cart')
    flask_app.register_blueprint(reportes_bp, url_prefix='/reportes')

    @login_manager.user_loader
    def load_user(user_id):
        if user_id.startswith('UC-'):
            return UsuarioCliente.query.get(int(user_id.split('-')[1]))
        if user_id.startswith('EMP-'):
            return Empleado.query.get(int(user_id.split('-')[1]))
        return None

    @flask_app.route('/ping')
    def ping():
        return "Pong! El servidor Flask está funcionando correctamente."

    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
