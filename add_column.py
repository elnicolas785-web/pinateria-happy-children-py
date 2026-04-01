import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='', database='sistema_feliz')
    cursor = conn.cursor()
    
    # Check if column exists first
    cursor.execute("SHOW COLUMNS FROM cliente LIKE 'direccion'")
    result = cursor.fetchone()
    
    if not result:
        cursor.execute("ALTER TABLE cliente ADD COLUMN direccion VARCHAR(255)")
        conn.commit()
        print("Column direccion added to cliente table successfully!")
    else:
        print("Column already exists.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
