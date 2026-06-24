import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-muy-segura-pinateria'
    
    _host = os.environ.get('MYSQLHOST')
    _user = os.environ.get('MYSQLUSER')
    _password = os.environ.get('MYSQLPASSWORD')
    _port = os.environ.get('MYSQLPORT', '3306')
    _database = os.environ.get('MYSQLDATABASE')

    if _host:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_database}"
    else:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/sistema_feliz'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CONFIGURACIÓN BREVO SMTP
    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('BREVO_USERNAME')
    MAIL_PASSWORD = os.environ.get('BREVO_PASSWORD')