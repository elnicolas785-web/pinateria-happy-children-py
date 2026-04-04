import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='', db='sistema_feliz', connect_timeout=5)
    cur = conn.cursor()
    cur.execute("SELECT nombre, url_imagen FROM Producto WHERE nombre LIKE '%piñata%'")
    for row in cur.fetchall():
        print(f"{row[0]} | {row[1]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
