from app import create_app, db
from app.models import Country, Currency, Supplier
from datetime import datetime

def init_suppliers_module():
    """
    Script para inicializar las tablas del módulo de proveedores
    """
    app = create_app()
    
    with app.app_context():
        print("Inicializando módulo de proveedores...")
        
        # Crear tablas si no existen
        db.create_all()
        
        # Crear países por defecto
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
        
        countries_created = 0
        for country_data in default_countries:
            country = Country.query.filter_by(symbol=country_data['symbol']).first()
            if not country:
                country = Country(
                    name=country_data['name'],
                    symbol=country_data['symbol']
                )
                db.session.add(country)
                countries_created += 1
        
        db.session.commit()
        print(f"✓ Países creados: {countries_created}")
        
        # Crear monedas por defecto
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
        
        currencies_created = 0
        for currency_data in default_currencies:
            currency = Currency.query.filter_by(symbol=currency_data['symbol']).first()
            if not currency:
                currency = Currency(
                    name=currency_data['name'],
                    symbol=currency_data['symbol']
                )
                db.session.add(currency)
                currencies_created += 1
        
        db.session.commit()
        print(f"✓ Monedas creadas: {currencies_created}")
        
        # Crear algunos proveedores de ejemplo
        print("Creando proveedores de ejemplo...")
        example_suppliers = [
            {
                'id_suplier': 'PROV-001',
                'legal_name': 'Tecnologia Global S.A. de C.V.',
                'name': 'TecnoGlobal',
                'country': 'Mexico',
                'currency': 'Mexican Peso',
                'text_id': 'TGM001234567',
                'state_province': 'Jalisco',
                'city': 'Guadalajara',
                'address': 'Av. Tecnologico 123, Col. Centro',
                'zip_code': '44100',
                'phone': '+52 33 1234 5678',
                'email': 'contacto@tecnoglobal.com',
                'contact_name': 'Juan Perez',
                'contact_role': 'Gerente de Ventas',
                'category': 'Tecnologia',
                'payments_terms': '30 días',
                'payment_method': 'Transferencia',
                'bank_account': '1234567890',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_suplier': 'PROV-002',
                'legal_name': 'Materiales de Construcción S.A.',
                'name': 'MaterialCon',
                'country': 'Mexico',
                'currency': 'Mexican Peso',
                'text_id': 'MCS7654321',
                'state_province': 'Nuevo Leon',
                'city': 'Monterrey',
                'address': 'Blvd. Industrial 456, Parque Industrial',
                'zip_code': '64000',
                'phone': '+52 81 9876 5432',
                'email': 'ventas@materialcon.com',
                'contact_name': 'Maria Lopez',
                'contact_role': 'Ejecutiva de Ventas',
                'category': 'Construccion',
                'payments_terms': '15 días',
                'payment_method': 'Cheque',
                'bank_account': '0987654321',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_suplier': 'PROV-003',
                'legal_name': 'Insumos Industriales del Norte',
                'name': 'Insunorte',
                'country': 'United States',
                'currency': 'US Dollar',
                'text_id': 'IINUS123456',
                'state_province': 'Texas',
                'city': 'Houston',
                'address': 'Industrial Ave 789',
                'zip_code': '77001',
                'phone': '+1 713 555 0123',
                'email': 'sales@insunorte.com',
                'contact_name': 'John Smith',
                'contact_role': 'Sales Manager',
                'category': 'Industrial',
                'payments_terms': 'Net 30',
                'payment_method': 'Wire Transfer',
                'bank_account': '1122334455',
                'status': True,
                'created_by': 'admin'
            }
        ]
        
        suppliers_created = 0
        for supplier_data in example_suppliers:
            supplier = Supplier.query.filter_by(id_suplier=supplier_data['id_suplier']).first()
            if not supplier:
                supplier = Supplier(**supplier_data)
                db.session.add(supplier)
                suppliers_created += 1
        
        db.session.commit()
        print(f"✓ Proveedores de ejemplo creados: {suppliers_created}")
        
        # Mostrar resumen final
        print("\n" + "="*50)
        print("✅ MÓDULO DE PROVEEDORES INICIALIZADO EXITOSAMENTE")
        print("="*50)
        print(f"🌎 Países: {Country.query.count()}")
        print(f"💰 Monedas: {Currency.query.count()}")
        print(f"🏢 Proveedores creados: {Supplier.query.count()}")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Accede al módulo de proveedores desde el dashboard")
        print("   2. Verifica que los proveedores de ejemplo estén cargados")
        print("   3. Prueba los filtros y la exportación CSV")
        print("   4. Usa la carga masiva para agregar más proveedores")

if __name__ == '__main__':
    init_suppliers_module()