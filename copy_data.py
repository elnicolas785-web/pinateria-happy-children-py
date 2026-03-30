import pymysql

try:
    connection = pymysql.connect(host='localhost', user='root', password='')
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        
        cursor.execute("SHOW TABLES IN sistema_empresa;")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            try:
                cursor.execute(f"SHOW COLUMNS FROM sistema_feliz.{table};")
                target_cols = [row[0] for row in cursor.fetchall()]
                
                cursor.execute(f"SHOW COLUMNS FROM sistema_empresa.{table};")
                source_cols = [row[0] for row in cursor.fetchall()]
                
                common_cols = [c for c in target_cols if c in source_cols]
                
                if not common_cols:
                    print(f"Skipping {table}, no common columns.")
                    continue
                
                cols_str = ", ".join([f"`{c}`" for c in common_cols])
                
                cursor.execute(f"DELETE FROM sistema_feliz.{table};")
                cursor.execute(f"INSERT INTO sistema_feliz.{table} ({cols_str}) SELECT {cols_str} FROM sistema_empresa.{table};")
                print(f"✅ Data for '{table}' successfully copied.")
            except Exception as e:
                print(f"❌ Error copying table '{table}': {e}")
                
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    connection.commit()
    connection.close()
    print("Database data separation complete!")
except Exception as e:
    print(f"Fatal Error: {e}")
