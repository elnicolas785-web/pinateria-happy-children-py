import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Cliente, Producto, Rol
try:
    app = create_app()
    with app.app_context():
        print(f"Total clientes: {Cliente.query.count()}")
        print(f"Total productos: {Producto.query.count()}")
        print(f"Total roles: {Rol.query.count()}")
        print("Success: Can connect to the database and query tables.")
except Exception as e:
    print(f"Error: {e}")
