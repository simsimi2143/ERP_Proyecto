from app import create_app, db
# Asegúrate de importar tus nuevos modelos aquí
from app.models import (
    AccountType, AccountGroup, AccountNature, AccountAccount, 
    Currency, Country, JournalEntry, JournalItem
)
from datetime import datetime

def init_accounting_module(reset_data=False):
    """
    Script para inicializar las tablas del módulo de contabilidad
    """
    app = create_app()
    
    with app.app_context():
        print("Iniciando actualización del módulo de contabilidad...")
        
        if reset_data:
            print("⚠️ CUIDADO: Eliminando tablas existentes para reinicio total...")
            # Esto eliminará los datos. Úsalo solo si quieres empezar de cero.
            db.drop_all()
            print("✓ Tablas eliminadas")

        # Este comando crea todas las tablas definidas en models.py que no existan
        # Esto solucionará el error 'no such table: journal_item'
        db.create_all()
        print("✓ Estructura de tablas verificada/creada")
        
        # 1. Crear tipos de cuenta por defecto
        print("Sincronizando tipos de cuenta...")
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
        
        # 2. Crear grupos de cuenta por defecto
        print("Sincronizando grupos de cuenta...")
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
        
        # 3. Crear naturalezas de cuenta por defecto
        print("Sincronizando naturalezas de cuenta...")
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
        
        print("\n" + "="*50)
        print("✅ MÓDULO DE CONTABILIDAD ACTUALIZADO")
        print("="*50)
        print(f"📊 Tipos: {AccountType.query.count()} | Grupos: {AccountGroup.query.count()} | Naturalezas: {AccountNature.query.count()}")
        print("🚀 Las tablas de Asientos y Apuntes ya están listas.")

if __name__ == '__main__':
    # Cambia a True si quieres borrar todo y empezar de cero
    init_accounting_module(reset_data=False)