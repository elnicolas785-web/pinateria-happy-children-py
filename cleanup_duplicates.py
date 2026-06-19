import pymysql

try:
    connection = pymysql.connect(host='localhost', user='root', password='', database='sistema_feliz')
    with connection.cursor() as cursor:
        # Delete duplicate usernames 'admin' and 'empleado' from usuario_cliente
        affected = cursor.execute("DELETE FROM usuario_cliente WHERE nombre_usuario IN ('admin', 'empleado');")
        print(f"Deleted {affected} conflictive rows from usuario_cliente.")
    connection.commit()
    connection.close()
except Exception as e:
    print(f"Error cleaning up database: {e}")
