from app import create_app, db
from app.models import Location, InventoryStock, Material

app = create_app()

with app.app_context():
    print("--- INICIANDO REPARACIÓN DE BASE DE DATOS ---")
    
    # 1. Corregir la ubicación "Bodega de Reparto"
    # Buscamos por el ID primario que suele ser el 3 según lo que hemos hablado
    loc = Location.query.get(3) 
    if not loc:
        # Si el ID 3 no existe, buscamos por nombre
        loc = Location.query.filter(Location.name.like('%reparto%')).first()

    if loc:
        loc.id_location = '3'  # Forzamos el valor que el formulario necesita
        db.session.commit()
        print(f"✅ UBICACIÓN CORREGIDA: '{loc.name}' ahora tiene id_location='3'")
    else:
        print("❌ ERROR: No se encontró la ubicación 'Reparto' para corregirla.")

    # 2. Sincronizar el Stock de Prod-001
    # Borramos registros huérfanos o mal escritos
    InventoryStock.query.filter_by(id_material='Prod-001').delete()
    
    mat = Material.query.filter_by(id_material='Prod-001').first()
    if mat:
        nuevo_stock = InventoryStock(
            id_material='Prod-001',
            id_location='3', # Vinculado al código que acabamos de forzar
            quantity=500.0,
            unit_type=str(mat.unit),
            min_stock=0,
            max_stock=1000,
            created_by='admin'
        )
        db.session.add(nuevo_stock)
        db.session.commit()
        print("✅ STOCK REGENERADO: 500 unidades de Prod-001 en bodega '3'")
    else:
        print("❌ ERROR: No se encontró el material 'Prod-001' en el catálogo.")

    print("--- PROCESO FINALIZADO ---")