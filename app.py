"""
Main application module for the Flask app.
"""
import os
import sys

# Ensure the app directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, mail
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
    mail.init_app(flask_app)

    # Crear tablas y semilla de datos si la base de datos está vacía
    with flask_app.app_context():
        try:
            db.create_all()
            from models import Rol, Empleado
            from werkzeug.security import generate_password_hash
            if Rol.query.count() == 0:
                admin_rol = Rol(codigo="ROL-ADMIN", nombre_rol="Administrador", estado="Activo")
                cliente_rol = Rol(codigo="ROL-CLIENTE", nombre_rol="Cliente", estado="Activo")
                empleado_rol = Rol(codigo="ROL-EMPLEADO", nombre_rol="Empleado", estado="Activo")
                db.session.add_all([admin_rol, cliente_rol, empleado_rol])
                db.session.commit()
                print("Default roles seeded successfully.")
            if Empleado.query.count() == 0:
                admin_rol = Rol.query.filter_by(nombre_rol="Administrador").first()
                if admin_rol:
                    admin_emp = Empleado(
                        codigo="EMP-ADMIN",
                        nombres="Administrador",
                        apellidos="Sistema",
                        tipo_documento="CC",
                        documento_identidad="0000000000",
                        email="admin@happychildren.com",
                        id_rol=admin_rol.id_rol,
                        estado="Activo",
                        nombre_usuario="admin",
                        contrasena_hash=generate_password_hash("admin123")
                    )
                    db.session.add(admin_emp)
                    db.session.commit()
                    print("Default administrator seeded successfully.")
        except Exception as e:
            print(f"Error checking/seeding database tables: {e}")


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

    @flask_app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', 
                             code=403, 
                             title="Acceso Denegado", 
                             icon="fa-lock",
                             message="Lo sentimos, no tienes los permisos necesarios para acceder a esta página."), 403

    @flask_app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', 
                             code=404, 
                             title="Página no encontrada", 
                             icon="fa-ghost",
                             message="¡Oops! La página que buscas parece haber desaparecido en una fiesta mágica."), 404

    return flask_app


# Instancia global de la aplicación requerida para el entorno de producción
app = create_app()

if __name__ == '__main__':
    # Lee el puerto dinámico de Railway; si no existe, usa 5000 por defecto
    puerto = int(os.environ.get("PORT", 5000))
    # debug=False es vital para evitar reinicios constantes y errores 502 en producción
    app.run(host='0.0.0.0', port=puerto, debug=False)