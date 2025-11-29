import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-muy-secreta'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///erp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de logos
    LOGO_LOGIN = 'images/logos/logo.jpg'
    LOGO_NAVBAR = 'images/logos/logo.jpg'
    FAVICON = 'images/logos/favicon.ico'
    APP_NAME = 'ERP InfiWebSPA'