from app import create_app, db
from app.models import User, Role

def init_db():
    app = create_app()
    
    with app.app_context():
        # Crear tablas
        db.create_all()
        
        # Crear rol de superadmin si no existe
        superadmin_role = Role.query.filter_by(name='Superadmin').first()
        if not superadmin_role:
            superadmin_role = Role(
                name='Superadmin',
                description='Superusuario con acceso total',
                materials_permission=2,
                inventory_permission=2,
                customers_permission=2,
                accounting_permission=2,
                suppliers_permission=2,
                reporting_permission=2,
                purchases_permission=2,
                sales_permission=2,
                users_permission=2
            )
            db.session.add(superadmin_role)
            db.session.commit()
        
        # Crear usuario superadmin si no existe
        superadmin = User.query.filter_by(username='admin').first()
        if not superadmin:
            superadmin = User(
                username='admin',
                email='admin@erp.com',
                is_superuser=True,
                role_id=superadmin_role.id
            )
            superadmin.set_password('admin123')
            db.session.add(superadmin)
            db.session.commit()
        
        print("Base de datos inicializada correctamente")
        print("Superusuario creado: admin / admin123")
        

if __name__ == '__main__':
    init_db()