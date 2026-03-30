import pymysql
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    connection = pymysql.connect(host='localhost', user='root', password='')
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_feliz;")
    connection.commit()
    connection.close()
    print("Database created or verified successfully.")
except Exception as e:
    print(f"Error creating database: {e}")
    sys.exit(1)

from app import create_app
from extensions import db
import models

app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables initialized successfully.")
