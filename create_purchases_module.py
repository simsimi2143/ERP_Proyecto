from app import create_app, db
from app.models import PurchaseOrder, PurchaseOrderLine
from datetime import datetime, timedelta

def init_purchases_module():
    """
    Script para inicializar las tablas del módulo de compras
    """
    app = create_app()
    
    with app.app_context():
        print("Inicializando módulo de compras...")
        
        # Crear tablas si no existen
        db.create_all()
        
        # Crear órdenes de compra de ejemplo
        print("Creando órdenes de compra de ejemplo...")
        example_orders = [
            {
                'id_purchase_order': 'OC-2024-001',
                'id_supplier': 'PROV-001',
                'issue_date': datetime.now() - timedelta(days=10),
                'estimated_delivery_date': datetime.now() + timedelta(days=20),
                'status': 'Aprobada',
                'currency': 'MXN',
                'notes': 'Orden de materiales para proyecto Q2',
                'created_by': 'admin'
            },
            {
                'id_purchase_order': 'OC-2024-002',
                'id_supplier': 'PROV-002',
                'issue_date': datetime.now() - timedelta(days=5),
                'estimated_delivery_date': datetime.now() + timedelta(days=15),
                'status': 'Pendiente',
                'currency': 'MXN',
                'notes': 'Materiales de construcción urgente',
                'created_by': 'admin'
            },
            {
                'id_purchase_order': 'OC-2024-003',
                'id_supplier': 'PROV-003',
                'issue_date': datetime.now() - timedelta(days=15),
                'estimated_delivery_date': datetime.now() - timedelta(days=2),
                'status': 'Recibida',
                'currency': 'USD',
                'notes': 'Importación de componentes electrónicos',
                'created_by': 'admin'
            }
        ]
        
        orders_created = 0
        for order_data in example_orders:
            order = PurchaseOrder.query.filter_by(id_purchase_order=order_data['id_purchase_order']).first()
            if not order:
                order = PurchaseOrder(**order_data)
                db.session.add(order)
                orders_created += 1
        
        db.session.commit()
        print(f"✓ Órdenes de compra creadas: {orders_created}")
        
        # Crear líneas de órdenes de ejemplo
        print("Creando líneas de órdenes de ejemplo...")
        example_lines = [
            # OC-2024-001
            {
                'id_purchase_order_line': 'OC-2024-001-1',
                'id_purchase_order': 'OC-2024-001',
                'id_material': 'MAT-001',
                'position': 1,
                'quantity': 1000,
                'unit_material': 'pza',
                'price': 2.50,
                'currency_suppliers': 'MXN',
                'created_by': 'admin'
            },
            {
                'id_purchase_order_line': 'OC-2024-001-2',
                'id_purchase_order': 'OC-2024-001',
                'id_material': 'MAT-002',
                'position': 2,
                'quantity': 500,
                'unit_material': 'm',
                'price': 45.00,
                'currency_suppliers': 'MXN',
                'created_by': 'admin'
            },
            # OC-2024-002
            {
                'id_purchase_order_line': 'OC-2024-002-1',
                'id_purchase_order': 'OC-2024-002',
                'id_material': 'MAT-004',
                'position': 1,
                'quantity': 50,
                'unit_material': 'pza',
                'price': 320.00,
                'currency_suppliers': 'MXN',
                'created_by': 'admin'
            },
            # OC-2024-003
            {
                'id_purchase_order_line': 'OC-2024-003-1',
                'id_purchase_order': 'OC-2024-003',
                'id_material': 'MAT-006',
                'position': 1,
                'quantity': 5,
                'unit_material': 'pza',
                'price': 1250.00,
                'currency_suppliers': 'USD',
                'created_by': 'admin'
            }
        ]
        
        lines_created = 0
        for line_data in example_lines:
            line = PurchaseOrderLine.query.filter_by(id_purchase_order_line=line_data['id_purchase_order_line']).first()
            if not line:
                line = PurchaseOrderLine(**line_data)
                db.session.add(line)
                lines_created += 1
        
        db.session.commit()
        print(f"✓ Líneas de órdenes creadas: {lines_created}")
        
        # Actualizar montos totales
        print("Actualizando montos totales...")
        orders = PurchaseOrder.query.all()
        for order in orders:
            lines = PurchaseOrderLine.query.filter_by(id_purchase_order=order.id_purchase_order).all()
            total = sum(line.quantity * line.price for line in lines)
            order.total_amount = total
        
        db.session.commit()
        
        # Mostrar resumen final
        print("\n" + "="*50)
        print("✅ MÓDULO DE COMPRAS INICIALIZADO EXITOSAMENTE")
        print("="*50)
        print(f"📋 Órdenes de compra: {PurchaseOrder.query.count()}")
        print(f"📦 Líneas de órdenes: {PurchaseOrderLine.query.count()}")
        
        print("\n📊 Órdenes por estado:")
        statuses = ['Pendiente', 'Aprobada', 'Enviada', 'Recibida', 'Cancelada']
        for status in statuses:
            count = PurchaseOrder.query.filter_by(status=status).count()
            print(f"   - {status}: {count} órdenes")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Accede al módulo de compras desde el dashboard")
        print("   2. Verifica que las órdenes de ejemplo estén cargadas")
        print("   3. Prueba los filtros y la exportación CSV")
        print("   4. Crea nuevas órdenes de compra")

if __name__ == '__main__':
    init_purchases_module()