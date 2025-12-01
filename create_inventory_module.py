from app import create_app, db
from app.models import Location, Unit, MaterialType
from datetime import datetime

def init_inventory_module():
    """
    Script para inicializar las tablas del módulo de inventario
    """
    app = create_app()
    
    with app.app_context():
        print("Inicializando módulo de inventario...")
        
        # Crear tablas si no existen
        db.create_all()
        
        # Crear ubicación principal por defecto
        print("Creando ubicaciones por defecto...")
        main_location = Location.query.filter_by(main_location=True).first()
        if not main_location:
            location = Location(
                name='Bodega Principal',
                code='BOD-PRINCIPAL',
                main_location=True,
                location='Ubicación principal de almacenamiento',
                created_by='admin'
            )
            db.session.add(location)
            print("✓ Ubicación principal creada")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("✅ MÓDULO DE INVENTARIO INICIALIZADO EXITOSAMENTE")
        print("="*50)
        print(f"🏢 Ubicaciones: {Location.query.count()}")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Accede al módulo de inventario desde el dashboard")
        print("   2. Configura las ubicaciones necesarias")
        print("   3. Registra los movimientos iniciales de inventario")
        print("   4. Configura los niveles mínimo y máximo de stock")

if __name__ == '__main__':
    init_inventory_module()