from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'users.login'
    
    from app.routes.users import bp as users_bp
    from app.routes.materials import bp as materials_bp  # materiales
    from app.routes.suppliers import bp as suppliers_bp  # proveedores
    from app.routes.customers import bp as customers_bp  # clientes
    from app.routes.purchases import bp as purchases_bp # compras
    from app.routes.inventory import bp as inventory_bp # inventario
    app.register_blueprint(inventory_bp) # inventario
    app.register_blueprint(purchases_bp) # compras
    app.register_blueprint(users_bp)    
    app.register_blueprint(materials_bp)  # materialeso
    app.register_blueprint(suppliers_bp)  # proveedores
    app.register_blueprint(customers_bp)  # clientes
    
    @app.template_filter('getattr')
    def getattr_filter(obj, attr):
        return getattr(obj, attr, None)
    
    return app