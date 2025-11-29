from app import create_app, db
from app.models import Country, Currency, Customer
from datetime import datetime

def init_customers_module():
    """
    Script para inicializar las tablas del módulo de clientes
    """
    app = create_app()
    
    with app.app_context():
        print("Inicializando módulo de clientes...")
        
        # Crear tablas si no existen
        db.create_all()
        
        # Verificar que existan países y monedas (usamos los mismos que para proveedores)
        # Si no existen, crearlos
        if Country.query.count() == 0:
            print("Creando países...")
            default_countries = [
                {'name': 'Mexico', 'symbol': 'MX'},
                {'name': 'United States', 'symbol': 'US'},
                {'name': 'Canada', 'symbol': 'CA'},
                {'name': 'Colombia', 'symbol': 'CO'},
                {'name': 'Brazil', 'symbol': 'BR'},
                {'name': 'Argentina', 'symbol': 'AR'},
                {'name': 'Chile', 'symbol': 'CL'},
                {'name': 'Peru', 'symbol': 'PE'},
                {'name': 'Spain', 'symbol': 'ES'},
                {'name': 'China', 'symbol': 'CN'},
                {'name': 'Germany', 'symbol': 'DE'},
                {'name': 'France', 'symbol': 'FR'},
                {'name': 'United Kingdom', 'symbol': 'UK'},
                {'name': 'Japan', 'symbol': 'JP'},
            ]
            
            for country_data in default_countries:
                country = Country(
                    name=country_data['name'],
                    symbol=country_data['symbol']
                )
                db.session.add(country)
        
        if Currency.query.count() == 0:
            print("Creando monedas...")
            default_currencies = [
                {'name': 'Mexican Peso', 'symbol': 'MXN'},
                {'name': 'US Dollar', 'symbol': 'USD'},
                {'name': 'Euro', 'symbol': 'EUR'},
                {'name': 'Canadian Dollar', 'symbol': 'CAD'},
                {'name': 'Pound Sterling', 'symbol': 'GBP'},
                {'name': 'Yen', 'symbol': 'JPY'},
                {'name': 'Yuan', 'symbol': 'CNY'},
                {'name': 'Brazilian Real', 'symbol': 'BRL'},
                {'name': 'Argentine Peso', 'symbol': 'ARS'},
                {'name': 'Chilean Peso', 'symbol': 'CLP'},
                {'name': 'Colombian Peso', 'symbol': 'COP'},
                {'name': 'Peruvian Sol', 'symbol': 'PEN'},
            ]
            
            for currency_data in default_currencies:
                currency = Currency(
                    name=currency_data['name'],
                    symbol=currency_data['symbol']
                )
                db.session.add(currency)
        
        db.session.commit()
        
        # Crear algunos clientes de ejemplo
        print("Creando clientes de ejemplo...")
        example_customers = [
            {
                'id_customer': 'CLI-001',
                'legal_name': 'Empresa ABC S.A. de C.V.',
                'name': 'ABC Corp',
                'country': 'Mexico',
                'currency': 'Mexican Peso',
                'text_id': 'ABC001234567',
                'state_province': 'Jalisco',
                'city': 'Guadalajara',
                'address': 'Av. Principal 123, Col. Centro',
                'zip_code': '44100',
                'phone': '+52 33 1234 5678',
                'email': 'contacto@abccorp.com',
                'contact_name': 'Ana Garcia',
                'contact_role': 'Gerente de Compras',
                'category': 'Retail',
                'payments_terms': '30 días',
                'payment_method': 'Transferencia',
                'bank_account': '1234567890',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_customer': 'CLI-002',
                'legal_name': 'Comercializadora XYZ S.A.',
                'name': 'XYZ Comercial',
                'country': 'Mexico',
                'currency': 'Mexican Peso',
                'text_id': 'XYZ7654321',
                'state_province': 'Nuevo Leon',
                'city': 'Monterrey',
                'address': 'Blvd. Comercial 456, Zona Industrial',
                'zip_code': '64000',
                'phone': '+52 81 9876 5432',
                'email': 'ventas@xyz.com',
                'contact_name': 'Pedro Martinez',
                'contact_role': 'Director de Compras',
                'category': 'Distribucion',
                'payments_terms': '15 días',
                'payment_method': 'Cheque',
                'bank_account': '0987654321',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_customer': 'CLI-003',
                'legal_name': 'Importadora Chile S.A.',
                'name': 'ImportChile',
                'country': 'Chile',
                'currency': 'Chilean Peso',
                'text_id': 'ICH123456789',
                'state_province': 'Santiago',
                'city': 'Santiago',
                'address': 'Av. Principal 789',
                'zip_code': '8320000',
                'phone': '+56 2 2345 6789',
                'email': 'contacto@importchile.cl',
                'contact_name': 'Carlos Ruiz',
                'contact_role': 'Director',
                'category': 'Importaciones',
                'payments_terms': '60 días',
                'payment_method': 'Transferencia',
                'bank_account': '1122334455',
                'status': True,
                'created_by': 'admin'
            }
        ]
        
        customers_created = 0
        for customer_data in example_customers:
            customer = Customer.query.filter_by(id_customer=customer_data['id_customer']).first()
            if not customer:
                customer = Customer(**customer_data)
                db.session.add(customer)
                customers_created += 1
        
        db.session.commit()
        print(f"✓ Clientes de ejemplo creados: {customers_created}")
        
        # Mostrar resumen final
        print("\n" + "="*50)
        print("✅ MÓDULO DE CLIENTES INICIALIZADO EXITOSAMENTE")
        print("="*50)
        print(f"🌎 Países: {Country.query.count()}")
        print(f"💰 Monedas: {Currency.query.count()}")
        print(f"👥 Clientes creados: {Customer.query.count()}")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Accede al módulo de clientes desde el dashboard")
        print("   2. Verifica que los clientes de ejemplo estén cargados")
        print("   3. Prueba los filtros y la exportación CSV")
        print("   4. Usa la carga masiva para agregar más clientes")

if __name__ == '__main__':
    init_customers_module()