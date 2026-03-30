import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-muy-segura-pinateria'
    # Utilizando la base de datos 'sistema_feliz'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/sistema_feliz'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
