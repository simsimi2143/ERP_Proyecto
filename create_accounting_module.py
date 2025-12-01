from app import create_app, db
from app.models import AccountType, AccountGroup, AccountNature, Currency, Country
from datetime import datetime

def init_accounting_module():
    """
    Script para inicializar las tablas del módulo de contabilidad
    """
    app = create_app()
    
    with app.app_context():
        print("Inicializando módulo de contabilidad...")
        
        # Crear tablas si no existen
        db.create_all()
        
        # Crear tipos de cuenta por defecto
        print("Creando tipos de cuenta...")
        default_account_types = [
            {'id_account_type': 'ACT-CIRCULANTE', 'name': 'Activo Circulante', 'description': 'Activos que se esperan convertir en efectivo dentro de un año'},
            {'id_account_type': 'ACT-FIJO', 'name': 'Activo Fijo', 'description': 'Activos de larga duración'},
            {'id_account_type': 'PAS-CIRCULANTE', 'name': 'Pasivo Circulante', 'description': 'Obligaciones a pagar dentro de un año'},
            {'id_account_type': 'PAS-LARGO-PLAZO', 'name': 'Pasivo a Largo Plazo', 'description': 'Obligaciones a pagar en más de un año'},
            {'id_account_type': 'CAPITAL', 'name': 'Capital', 'description': 'Patrimonio de los accionistas'},
            {'id_account_type': 'INGRESOS', 'name': 'Ingresos', 'description': 'Cuentas de ingresos'},
            {'id_account_type': 'GASTOS', 'name': 'Gastos', 'description': 'Cuentas de gastos'},
            {'id_account_type': 'RESULTADOS', 'name': 'Resultados', 'description': 'Cuentas de resultado'},
        ]
        
        for type_data in default_account_types:
            account_type = AccountType.query.filter_by(id_account_type=type_data['id_account_type']).first()
            if not account_type:
                account_type = AccountType(
                    id_account_type=type_data['id_account_type'],
                    name=type_data['name'],
                    description=type_data['description'],
                    created_by='admin'
                )
                db.session.add(account_type)
        
        db.session.commit()
        print("✓ Tipos de cuenta creados")
        
        # Crear grupos de cuenta por defecto
        print("Creando grupos de cuenta...")
        default_account_groups = [
            {'id_account_group': 'GRP-ACTIVO', 'name': 'Grupo Activo', 'code_prefix': '1', 'description': 'Grupo de cuentas de activo'},
            {'id_account_group': 'GRP-PASIVO', 'name': 'Grupo Pasivo', 'code_prefix': '2', 'description': 'Grupo de cuentas de pasivo'},
            {'id_account_group': 'GRP-CAPITAL', 'name': 'Grupo Capital', 'code_prefix': '3', 'description': 'Grupo de cuentas de capital'},
            {'id_account_group': 'GRP-INGRESOS', 'name': 'Grupo Ingresos', 'code_prefix': '4', 'description': 'Grupo de cuentas de ingresos'},
            {'id_account_group': 'GRP-GASTOS', 'name': 'Grupo Gastos', 'code_prefix': '5', 'description': 'Grupo de cuentas de gastos'},
        ]
        
        for group_data in default_account_groups:
            account_group = AccountGroup.query.filter_by(id_account_group=group_data['id_account_group']).first()
            if not account_group:
                account_group = AccountGroup(
                    id_account_group=group_data['id_account_group'],
                    name=group_data['name'],
                    code_prefix=group_data['code_prefix'],
                    description=group_data['description'],
                    created_by='admin'
                )
                db.session.add(account_group)
        
        db.session.commit()
        print("✓ Grupos de cuenta creados")
        
        # Crear naturalezas de cuenta por defecto
        print("Creando naturalezas de cuenta...")
        default_account_natures = [
            {'id_account_nature': 'DEUDORA', 'name': 'Deudora', 'symbol': 'D', 'effect_on_balance': 'Increase'},
            {'id_account_nature': 'ACREEDORA', 'name': 'Acreedora', 'symbol': 'A', 'effect_on_balance': 'Decrease'},
        ]
        
        for nature_data in default_account_natures:
            account_nature = AccountNature.query.filter_by(id_account_nature=nature_data['id_account_nature']).first()
            if not account_nature:
                account_nature = AccountNature(
                    id_account_nature=nature_data['id_account_nature'],
                    name=nature_data['name'],
                    symbol=nature_data['symbol'],
                    effect_on_balance=nature_data['effect_on_balance'],
                    created_by='admin'
                )
                db.session.add(account_nature)
        
        db.session.commit()
        print("✓ Naturalezas de cuenta creadas")
        
        print("\n" + "="*50)
        print("✅ MÓDULO DE CONTABILIDAD INICIALIZADO EXITOSAMENTE")
        print("="*50)
        print(f"📊 Tipos de cuenta: {AccountType.query.count()}")
        print(f"📋 Grupos de cuenta: {AccountGroup.query.count()}")
        print(f"⚖️ Naturalezas de cuenta: {AccountNature.query.count()}")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Accede al módulo de contabilidad desde el dashboard")
        print("   2. Revisa los tipos, grupos y naturalezas creadas")
        print("   3. Crea las cuentas contables principales")
        print("   4. Configura el plan de cuentas de tu empresa")

if __name__ == '__main__':
    init_accounting_module()