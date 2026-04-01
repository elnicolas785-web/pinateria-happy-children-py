import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='', database='sistema_feliz')
    cursor = conn.cursor()
    
    # Update cliente
    cursor.execute("""
        UPDATE cliente 
        SET direccion = CONCAT('Carrera ', FLOOR(RAND() * 100), ' #', FLOOR(RAND() * 100), '-', FLOOR(RAND() * 100), ', Bogota') 
        WHERE direccion IS NULL OR direccion = ''
    """)
    
    # Update venta
    cursor.execute("""
        UPDATE venta 
        SET direccion_entrega = CONCAT('Carrera ', FLOOR(RAND() * 100), ' #', FLOOR(RAND() * 100), '-', FLOOR(RAND() * 100), ', Bogota') 
        WHERE direccion_entrega IS NULL OR direccion_entrega = ''
    """)
    
    # Update pedido
    cursor.execute("""
        UPDATE pedido 
        SET direccion_entrega = CONCAT('Carrera ', FLOOR(RAND() * 100), ' #', FLOOR(RAND() * 100), '-', FLOOR(RAND() * 100), ', Bogota') 
        WHERE direccion_entrega IS NULL OR direccion_entrega = ''
    """)
    
    conn.commit()
    print(f"Addresses populated successfully!")
    print(f"Clientes updated: {cursor.rowcount} (estimate)")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
