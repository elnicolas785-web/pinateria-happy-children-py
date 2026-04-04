import uuid
from app import create_app
from extensions import db
from models import Cliente

def update_client_codes():
    app = create_app()
    with app.app_context():
        clientes = Cliente.query.all()
        updated_count = 0
        for cliente in clientes:
            # Generar código con el formato CLI- aleatorio
            unique_part = str(uuid.uuid4())[:6].upper()
            nuevo_codigo = f"CLI-{unique_part}"
            cliente.codigo = nuevo_codigo
            updated_count += 1
            
        try:
            db.session.commit()
            print(f"Se actualizaron exitosamente los códigos de {updated_count} clientes.")
        except Exception as e:
            db.session.rollback()
            print(f"Error actualizando códigos de clientes: {str(e)}")

if __name__ == "__main__":
    update_client_codes()
