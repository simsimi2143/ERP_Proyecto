from app import create_app, db
from app.models import (
    SaleOrder, SaleOrderLine, Customer, Material, 
    Location, InventoryStock, AccountAccount, AccountGroup
)
from datetime import datetime

def init_sales_module():
    app = create_app()
    
    with app.app_context():
        print("Iniciando inicialización del módulo de ventas...")
        
        # 1. Crear tablas
        db.create_all()
        print("✓ Tablas de ventas verificadas/creadas")

        # 2. Asegurar Cuentas Contables para el flujo de ventas
        # Buscamos grupos existentes creados por create_accounting_module.py
        grupo_ingresos = AccountGroup.query.filter(AccountGroup.id_account_group.like('4%')).first()
        grupo_activo = AccountGroup.query.filter(AccountGroup.id_account_group.like('1%')).first()

        if not grupo_ingresos or not grupo_activo:
            print("⚠️ Advertencia: Ejecuta primero create_accounting_module.py para tener los grupos contables.")
            return

        # Crear cuenta de ingresos si no existe
        cta_ventas = AccountAccount.query.filter_by(id_account='4105').first()
        if not cta_ventas:
            cta_ventas = AccountAccount(
                id_account='4105',
                name='Ventas al por mayor',
                group_id=grupo_ingresos.id,
                created_by='admin'
            )
            db.session.add(cta_ventas)

        # Crear cuenta de clientes si no existe
        cta_clientes = AccountAccount.query.filter_by(id_account='1105').first()
        if not cta_clientes:
            cta_clientes = AccountAccount(
                id_account='1105',
                name='Clientes Nacionales',
                group_id=grupo_activo.id,
                created_by='admin'
            )
            db.session.add(cta_clientes)

        db.session.commit()

        # 3. Crear Venta de Ejemplo
        customer = Customer.query.first()
        material = Material.query.first()
        location = Location.query.filter_by(main_location=True).first()

        if customer and material and location:
            sale_id = "VTA-2024-001"
            existing_sale = SaleOrder.query.filter_by(id_sale_order=sale_id).first()
            
            if not existing_sale:
                print(f"Creando venta de ejemplo {sale_id}...")
                new_sale = SaleOrder(
                    id_sale_order=sale_id,
                    id_customer=customer.id_customer,
                    issue_date=datetime.now(),
                    status='aprobado',
                    total_amount=500.0,
                    created_by='admin'
                )
                db.session.add(new_sale)
                
                line = SaleOrderLine(
                    id_sale_order=sale_id,
                    id_material=material.id_material,
                    quantity=1,
                    unit_price=500.0,
                    subtotal=500.0
                )
                db.session.add(line)
                db.session.commit()
                print("✓ Venta de ejemplo creada exitosamente")

        print("\n✅ MÓDULO DE VENTAS INICIALIZADO")

if __name__ == '__main__':
    init_sales_module()