from flask import Blueprint # type: ignore

auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
productos_bp = Blueprint('productos', __name__)
clientes_bp = Blueprint('clientes', __name__)
categorias_bp = Blueprint('categorias', __name__)
empleados_bp = Blueprint('empleados', __name__)
roles_bp = Blueprint('roles', __name__)
usuarios_bp = Blueprint('usuarios', __name__)
ventas_bp = Blueprint('ventas', __name__)
pedidos_bp = Blueprint('pedidos', __name__)
cart_bp = Blueprint('cart', __name__)
reportes_bp = Blueprint('reportes', __name__)

from . import auth, dashboard, productos, clientes, categorias, empleados, roles, usuarios, ventas, pedidos, cart, reportes # type: ignore
