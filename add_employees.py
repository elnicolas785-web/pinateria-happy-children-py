import os
import sys
import uuid
from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db
from models import Empleado, Rol
from datetime import datetime, date

import random

def add_mock_employees():
    app = create_app()
    with app.app_context():
        # First remove previously added mock employees to avoid clutter
        old_mocks = Empleado.query.filter(Empleado.codigo.like('EMP-MOCK-%')).all()
        for mock in old_mocks:
            db.session.delete(mock)
        db.session.commit()
        print(f"Deleted {len(old_mocks)} old mock employees.")

        # Retrieve or create an appropriate role
        rol = Rol.query.filter_by(nombre_rol='Empleado').first()
        if not rol:
            rol = Rol.query.first()
        
        if not rol:
            print("No roles found in database. Cannot create employees.")
            return
        
        print(f"Using role: {rol.nombre_rol} (ID: {rol.id_rol})")
        
        nombres_list = [
            "Carlos", "Maria", "Juan", "Ana", "Luis", "Laura", "Pedro", "Sofia",
            "Diego", "Carmen", "Javier", "Isabella", "Andres", "Camila", "Fernando",
            "Valentina", "Ricardo", "Valeria", "Alejandro", "Daniela", "Jose", "Lucia"
        ]
        
        apellidos_list = [
            "Garcia", "Martinez", "Rodriguez", "Lopez", "Hernandez", "Perez", "Gonzalez",
            "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Gomez", "Diaz", "Cruz",
            "Morales", "Ortiz", "Gutierrez", "Chavez", "Ruiz", "Alvarez", "Castillo"
        ]

        used_usernames = set()
        added_count = 0
        for i in range(1, 21):
            unique_id = str(uuid.uuid4())[:8]
            
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
            
            # Generar contraseña aleatoria (ej: nombre + 3 o 4 numeros aleatorios + simbolo + 3 letras aleatorias)
            simbolos = ["*", "#", "@", "$", "-"]
            letras = "abcdefghijklmnopqrstuvwxyz"
            
            num_aleatorios = str(random.randint(100, 9999))
            simbolo_aleatorio = random.choice(simbolos)
            letras_aleatorias = "".join(random.choices(letras, k=3))
            
            simple_password = f"{nombre_elegido.lower()}{num_aleatorios}{simbolo_aleatorio}{letras_aleatorias}"
            
            # Create a mock employee
            new_empleado = Empleado(
                codigo=f"EMP-MOCK-{unique_id}",
                nombres=nombre_elegido,
                apellidos=apellido_elegido,
                tipo_documento="CC",
                documento_identidad=f"1{random.randint(0, 9)}{random.randint(10000000, 99999999)}",
                email=email,
                telefono=f"300{random.randint(1000000, 9999999)}",
                id_rol=rol.id_rol,
                estado="Activo",
                nombre_usuario=username,
                contrasena_hash=simple_password
            )
            db.session.add(new_empleado)
            added_count += 1
            
            # Print created credentials for the user to see
            print(f"Creado: {nombre_elegido} {apellido_elegido} | Usuario: {username} | Email: {email} | Pass: {simple_password}")
            
        try:
            db.session.commit()
            print(f"\nSuccessfully added {added_count} employees with realistic names, gmail and simple passwords.")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding employees: {str(e)}")

if __name__ == "__main__":
    add_mock_employees()
