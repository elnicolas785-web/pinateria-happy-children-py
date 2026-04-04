import random
from app import create_app
from extensions import db
from models import Cliente, Empleado

def add_mock_phones():
    app = create_app()
    with app.app_context():
        # Update Clientes
        clientes = Cliente.query.all()
        clientes_updated = 0
        for cliente in clientes:
            if not cliente.telefono or len(cliente.telefono.strip()) < 5:
                # Generate a random 10-digit phone number starting with 3 (like mobile numbers in some Latin American countries)
                prefijos = ["300", "301", "310", "312", "315", "320", "321", "350"]
                prefijo = random.choice(prefijos)
                resto = f"{random.randint(1000000, 9999999):07d}"
                cliente.telefono = f"{prefijo}{resto}"
                clientes_updated += 1

        # Update Empleados
        empleados = Empleado.query.all()
        empleados_updated = 0
        for empleado in empleados:
            if not empleado.telefono or len(empleado.telefono.strip()) < 5:
                prefijos = ["300", "301", "310", "312", "315", "320", "321", "350"]
                prefijo = random.choice(prefijos)
                resto = f"{random.randint(1000000, 9999999):07d}"
                empleado.telefono = f"{prefijo}{resto}"
                empleados_updated += 1

        try:
            db.session.commit()
            print(f"Se actualizaron los telefonos de {clientes_updated} clientes.")
            print(f"Se actualizaron los telefonos de {empleados_updated} empleados.")
        except Exception as e:
            db.session.rollback()
            print(f"Error actualizando telefonos: {str(e)}")

if __name__ == "__main__":
    add_mock_phones()
