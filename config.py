import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-muy-segura-pinateria'
    
    # 1. Intentamos obtener la URL de la base de datos de Railway
    _RAILWAY_DB = os.environ.get('MYSQL_URL')
    
    if _RAILWAY_DB:
        # Railway genera la URL como 'mysql://...', pero Flask-SQLAlchemy 
        # necesita obligatoriamente saber el driver ('mysql+pymysql://')
        if _RAILWAY_DB.startswith("mysql://"):
            SQLALCHEMY_DATABASE_URI = _RAILWAY_DB.replace("mysql://", "mysql+pymysql://", 1)
        else:
            SQLALCHEMY_DATABASE_URI = _RAILWAY_DB
    else:
        # 2. Si no está en Railway, usa tu phpMyAdmin local por defecto
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/sistema_feliz'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

# CONFIGURACIÓN DE FLASK-MAIL
    MAIL_SERVER = 'smtp.gmail.com'          # Servidor de Gmail
    MAIL_PORT = 587                         # Puerto estándar para TLS
    MAIL_USE_TLS = True                     # Activa la seguridad
    MAIL_USERNAME = 'hchildren815@gmail.com'  # correo real
    
    # Es una "Contraseña de Aplicación" de 16 letras.
    MAIL_PASSWORD = 'hkcwqghazwroverq'