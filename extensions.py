from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from functools import wraps
from flask import abort, redirect, url_for
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()

# --- AQUÍ AGREGAMOS LOS DECORADORES DE SEGURIDAD ---

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. ¿Está logueado?
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # 2. ¿Es un empleado? (Los clientes no tienen id_empleado)
        if not hasattr(current_user, 'id_empleado'):
            abort(403) 
            
        # 3. ¿Tiene rol de ADMIN?
        rol_nombre = current_user.rol.nombre_rol.upper() if current_user.rol else ""
        if rol_nombre not in ['ADMINISTRADOR', 'ADMIN']:
            return redirect(url_for('dashboard.empleado_dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. ¿Está logueado?
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # 2. ¿Es un empleado?
        if not hasattr(current_user, 'id_empleado'):
            abort(403)
            
        return f(*args, **kwargs)
    return decorated_function