import os
import sys
import uuid
import random
from app import create_app
from extensions import db
from models import Cliente, UsuarioCliente, Rol
from datetime import datetime, date

def generate_random_password(nombre):
    simbolos = ["*", "#", "@", "$", "-"]
    letras = "abcdefghijklmnopqrstuvwxyz"
    num_aleatorios = str(random.randint(100, 9999))
    simbolo_aleatorio = random.choice(simbolos)
    letras_aleatorias = "".join(random.choices(letras, k=3))
    return f"{nombre.lower().split()[0]}{num_aleatorios}{simbolo_aleatorio}{letras_aleatorias}"

def add_mock_clients():
    app = create_app()
    with app.app_context():
        # Obtener rol de CLIENTE
        rol_cliente = Rol.query.filter(Rol.nombre_rol.ilike('CLIENTE')).first()
        if not rol_cliente:
            print("No se encontro rol de CLIENTE, se intentara usar el rol de ID 2 o 1.")
            rol_cliente = Rol.query.get(2) or Rol.query.first()
            
        print(f"Usando rol para cliente: {rol_cliente.nombre_rol} (ID: {rol_cliente.id_rol})")

        # 1. Asignar contraseña y usuario a clientes existentes que no tengan
        clientes_existentes = Cliente.query.all()
        updated_count = 0
        used_usernames = {u.nombre_usuario for u in UsuarioCliente.query.all()}
        
        for cliente in clientes_existentes:
            necesita_actualizar = False
            
            # Si no tiene password en Cliente
            if not cliente.password:
                cliente.password = generate_random_password(cliente.nombres)
                necesita_actualizar = True
            
            # Revisar si tiene UsuarioCliente
            usuario_asociado = UsuarioCliente.query.filter_by(id_cliente=cliente.id_cliente).first()
            if not usuario_asociado:
                base_username = f"{cliente.nombres.split()[0].lower()}.{cliente.apellidos.split()[0].lower()}"
                username = base_username
                counter = 1
                while username in used_usernames:
                    username = f"{base_username}{counter}"
                    counter += 1
                used_usernames.add(username)
                
                unique_id = str(uuid.uuid4())[:4]
                usuario = UsuarioCliente(
                    id_cliente=cliente.id_cliente,
                    nombre_usuario=username,
                    contrasena=cliente.password,
                    id_rol=rol_cliente.id_rol,
                    estado="Activo",
                    codigo=f"USR-UPD-{unique_id}"
                )
                db.session.add(usuario)
                necesita_actualizar = True
                print(f"Actualizado existente: {cliente.nombres} | Usuario: {username} | Pass: {cliente.password}")
            
            if necesita_actualizar:
                updated_count += 1
        
        db.session.commit()
        print(f"Se actualizaron {updated_count} clientes existentes sin credenciales completas.\n")

        # 2. Crear 10 nuevos clientes mock
        nombres_list = [
            "Miguel", "Roberto", "Rosa", "Marta", "Juana", "Antonio", "Eduardo", "Silvia",
            "Diana", "Patricia", "Hugo", "Mario", "Elena", "Teresa", "Manuel", "Veronica"
        ]
        apellidos_list = [
            "Mendoza", "Vargas", "Rios", "Molina", "Silva", "Rojas", "Navarro", "Delgado",
            "Salazar", "Reyes", "Medina", "Aguilar", "Paredes", "Soto", "Valdez", "Peña"
        ]
        direcciones = [
            "Calle Falsa 123", "Av. Principal 456", "Cra 10 #20-30", "Diag. 1 #2-3",
            "Calle 100 Sur", "Boulevard Centro 5", "Avenida Siempreviva 742",
            "Calle Las Flores 12", "Urbanizacion El Sol Mz A Lte 2", "Av. del Parque 10"
        ]
        
        added_count = 0
        for i in range(1, 11):
            nombre_elegido = random.choice(nombres_list)
            apellido_elegido = random.choice(apellidos_list)
            
            base_username = f"{nombre_elegido.lower()}.{apellido_elegido.lower()}".replace(' ', '')
            username = base_username
            counter = 1
            while username in used_usernames:
                username = f"{base_username}{counter}"
                counter += 1
            used_usernames.add(username)
            
            email = f"{username}@gmail.com"
            password = generate_random_password(nombre_elegido)
            direccion_elegida = random.choice(direcciones)
            unique_id = str(uuid.uuid4())[:6]
            
            # Crear Cliente
            nuevo_cliente = Cliente(
                codigo=f"CLI-MOCK-{unique_id}",
                nombres=nombre_elegido,
                apellidos=apellido_elegido,
                tipo_documento="CC",
                numero_documento=f"40{random.randint(1000000, 9999999)}",
                email=email,
                telefono=f"320{random.randint(1000000, 9999999)}",
                estado="Activo",
                direccion=direccion_elegida,
                password=password
            )
            db.session.add(nuevo_cliente)
            db.session.flush() # Para obtener id_cliente
            
            # Crear UsuarioCliente
            nuevo_usuario = UsuarioCliente(
                id_cliente=nuevo_cliente.id_cliente,
                nombre_usuario=username,
                contrasena=password,
                id_rol=rol_cliente.id_rol,
                estado="Activo",
                codigo=f"USR-MOCK-{unique_id}"
            )
            db.session.add(nuevo_usuario)
            added_count += 1
            
            print(f"Creado: {nombre_elegido} {apellido_elegido} | Dir: {direccion_elegida} | Usuario: {username} | Email: {email} | Pass: {password}")
            
        try:
            db.session.commit()
            print(f"\nSuccessfully added {added_count} new clients.")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding new clients: {str(e)}")

if __name__ == "__main__":
    add_mock_clients()
