import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='', database='sistema_feliz')
    cursor = conn.cursor()
    
    # Update venta
    cursor.execute("UPDATE venta SET observaciones = NULL")
    
    # Update pedido
    cursor.execute("UPDATE pedido SET observaciones = NULL")
    
    conn.commit()
    print("Observaciones limpiadas exitosamente en ventas y pedidos.")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
