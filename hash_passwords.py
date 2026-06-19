import pymysql
from werkzeug.security import generate_password_hash

databases = ['sistema_feliz', 'sistema feliz', 'pinateria_bd', 'sistema_empresa']

for db_name in databases:
    print(f"\n--- Processing database: '{db_name}' ---")
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"Database '{db_name}' could not be accessed: {e}")
        continue

    try:
        with connection.cursor() as cursor:
            # 1. Check if 'empleado' table exists
            cursor.execute("SHOW TABLES LIKE 'empleado';")
            if cursor.fetchone():
                cursor.execute("SELECT id_empleado, nombre_usuario, contrasena_hash FROM empleado;")
                employees = cursor.fetchall()
                updated_emp = 0
                for emp in employees:
                    pwd = emp['contrasena_hash']
                    if pwd is None:
                        continue
                    clean_pwd = pwd[6:] if pwd.startswith('{noop}') else pwd
                    # If not hashed, hash it
                    if not (clean_pwd.startswith('pbkdf2:') or clean_pwd.startswith('scrypt:') or clean_pwd.startswith('sha256:')):
                        hashed = generate_password_hash(clean_pwd)
                        cursor.execute(
                            "UPDATE empleado SET contrasena_hash = %s WHERE id_empleado = %s;",
                            (hashed, emp['id_empleado'])
                        )
                        print(f"  [Employee] Hashed password for '{emp['nombre_usuario']}'")
                        updated_emp += 1
                if updated_emp > 0:
                    connection.commit()
                    print(f"  Successfully updated {updated_emp} employees.")
                else:
                    print("  No employees needed password hashing.")
            else:
                print("  Table 'empleado' does not exist in this database.")

            # 2. Check if 'usuario_cliente' table exists
            cursor.execute("SHOW TABLES LIKE 'usuario_cliente';")
            if cursor.fetchone():
                cursor.execute("SELECT id_usuario, nombre_usuario, contrasena FROM usuario_cliente;")
                clients = cursor.fetchall()
                updated_cli = 0
                for cli in clients:
                    pwd = cli['contrasena']
                    if pwd is None:
                        continue
                    clean_pwd = pwd[6:] if pwd.startswith('{noop}') else pwd
                    # If not hashed, hash it
                    if not (clean_pwd.startswith('pbkdf2:') or clean_pwd.startswith('scrypt:') or clean_pwd.startswith('sha256:')):
                        hashed = generate_password_hash(clean_pwd)
                        cursor.execute(
                            "UPDATE usuario_cliente SET contrasena = %s WHERE id_usuario = %s;",
                            (hashed, cli['id_usuario'])
                        )
                        print(f"  [Client] Hashed password for '{cli['nombre_usuario']}'")
                        updated_cli += 1
                if updated_cli > 0:
                    connection.commit()
                    print(f"  Successfully updated {updated_cli} clients.")
                else:
                    print("  No clients needed password hashing.")
            else:
                print("  Table 'usuario_cliente' does not exist in this database.")

    except Exception as e:
        print(f"Error while processing '{db_name}': {e}")
        connection.rollback()
    finally:
        connection.close()

print("\nAll database checks and hashing complete!")
