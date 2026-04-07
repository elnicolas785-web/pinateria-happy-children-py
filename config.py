import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-muy-segura-pinateria'
    # Utilizando la base de datos 'sistema_feliz'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/sistema_feliz'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
# CONFIGURACIÓN DE FLASK-MAIL
    MAIL_SERVER = 'smtp.gmail.com'          # Servidor de Gmail
    MAIL_PORT = 587                         # Puerto estándar para TLS
    MAIL_USE_TLS = True                     # Activa la seguridad
    MAIL_USERNAME = 'hchildren815@gmail.com'  #correo real
    
    # Es una "Contraseña de Aplicación" de 16 letras.
    MAIL_PASSWORD = 'hkcwqghazwroverq'