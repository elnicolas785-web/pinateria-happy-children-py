import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-muy-segura-pinateria'
    
    # Variables que Railway SÍ provee (las que vimos en tu panel)
    _host = os.environ.get('MYSQLHOST')
    _user = os.environ.get('MYSQLUSER')
    _password = os.environ.get('MYSQLPASSWORD')
    _port = os.environ.get('MYSQLPORT', '3306')
    _database = os.environ.get('MYSQLDATABASE')

    if _host:
        # Estamos en Railway
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_database}"
    else:
        # Local con phpMyAdmin
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/sistema_feliz'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CONFIGURACIÓN DE FLASK-MAIL
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'hchildren815@gmail.com'
    MAIL_PASSWORD = 'hkcwqghazwroverq'