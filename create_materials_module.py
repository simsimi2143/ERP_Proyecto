from app import create_app, db
from app.models import Unit, MaterialType, Material
from datetime import datetime

def init_materials_module():
    """
    Script para inicializar las tablas del módulo de materiales
    """
    app = create_app()
    
    with app.app_context():
        print("Inicializando módulo de materiales...")
        
        # Crear tablas si no existen
        db.create_all()
        
        # Crear unidades por defecto
        print("Creando unidades de medida...")
        default_units = [
            # Unidades de longitud
            {'name': 'Pulgada', 'symbol': 'in'},
            {'name': 'Pie', 'symbol': 'ft'},
            {'name': 'Yarda', 'symbol': 'yd'},
            {'name': 'Metro', 'symbol': 'm'},
            {'name': 'Centímetro', 'symbol': 'cm'},
            {'name': 'Milímetro', 'symbol': 'mm'},
            {'name': 'Kilómetro', 'symbol': 'km'},
            
            # Unidades de área
            {'name': 'Pulgada cuadrada', 'symbol': 'in²'},
            {'name': 'Pie cuadrado', 'symbol': 'ft²'},
            {'name': 'Metro cuadrado', 'symbol': 'm²'},
            {'name': 'Centímetro cuadrado', 'symbol': 'cm²'},
            {'name': 'Hectárea', 'symbol': 'ha'},
            
            # Unidades de volumen
            {'name': 'Pulgada cúbica', 'symbol': 'in³'},
            {'name': 'Pie cúbico', 'symbol': 'ft³'},
            {'name': 'Metro cúbico', 'symbol': 'm³'},
            {'name': 'Centímetro cúbico', 'symbol': 'cm³'},
            {'name': 'Litro', 'symbol': 'L'},
            {'name': 'Mililitro', 'symbol': 'mL'},
            {'name': 'Galón', 'symbol': 'gal'},
            
            # Unidades de peso/masa
            {'name': 'Gramo', 'symbol': 'g'},
            {'name': 'Kilogramo', 'symbol': 'kg'},
            {'name': 'Miligramo', 'symbol': 'mg'},
            {'name': 'Tonelada', 'symbol': 't'},
            {'name': 'Libra', 'symbol': 'lb'},
            {'name': 'Onza', 'symbol': 'oz'},
            
            # Unidades de tiempo
            {'name': 'Segundo', 'symbol': 's'},
            {'name': 'Minuto', 'symbol': 'min'},
            {'name': 'Hora', 'symbol': 'h'},
            {'name': 'Día', 'symbol': 'd'},
            
            # Unidades comerciales comunes
            {'name': 'Pieza', 'symbol': 'pza'},
            {'name': 'Par', 'symbol': 'par'},
            {'name': 'Juego', 'symbol': 'jgo'},
            {'name': 'Caja', 'symbol': 'cja'},
            {'name': 'Paquete', 'symbol': 'pqt'},
            {'name': 'Rollo', 'symbol': 'rll'},
            {'name': 'Lata', 'symbol': 'lta'},
            {'name': 'Botella', 'symbol': 'btl'},
            {'name': 'Saco', 'symbol': 'sco'},
            {'name': 'Bolsa', 'symbol': 'bsa'},
        ]
        
        units_created = 0
        for unit_data in default_units:
            unit = Unit.query.filter_by(symbol=unit_data['symbol']).first()
            if not unit:
                unit = Unit(
                    name=unit_data['name'],
                    symbol=unit_data['symbol']
                )
                db.session.add(unit)
                units_created += 1
        
        db.session.commit()
        print(f"✓ Unidades creadas: {units_created}")
        
        # Crear tipos de material por defecto
        print("Creando tipos de material...")
        default_material_types = [
            {'name': 'Materia Prima', 'description': 'Materiales básicos para la producción'},
            {'name': 'Insumo', 'description': 'Materiales auxiliares para el proceso productivo'},
            {'name': 'Producto en Proceso', 'description': 'Materiales en proceso de transformación'},
            {'name': 'Producto Terminado', 'description': 'Productos finales listos para la venta'},
            {'name': 'Subproducto', 'description': 'Productos secundarios del proceso productivo'},
            {'name': 'Material de Empaque', 'description': 'Materiales para empaque y embalaje'},
            {'name': 'Material de Oficina', 'description': 'Suministros para uso administrativo'},
            {'name': 'Herramienta', 'description': 'Herramientas y equipos de trabajo'},
            {'name': 'Repuesto', 'description': 'Repuestos y componentes de mantenimiento'},
            {'name': 'Activo Fijo', 'description': 'Bienes de capital y activos fijos'},
            {'name': 'Activo dinamico', 'description': 'Bienes volatiles y de consumo rápido'},
        ]
        
        types_created = 0
        for material_type_data in default_material_types:
            material_type = MaterialType.query.filter_by(name=material_type_data['name']).first()
            if not material_type:
                material_type = MaterialType(
                    name=material_type_data['name'],
                    description=material_type_data['description']
                )
                db.session.add(material_type)
                types_created += 1
        
        db.session.commit()
        print(f"✓ Tipos de material creados: {types_created}")
        
        # Crear algunos materiales de ejemplo
        print("Creando materiales de ejemplo...")
        example_materials = [
            {
                'id_material': 'MAT-001',
                'name': 'Tornillo hexagonal acero inoxidable',
                'description': 'Tornillo hexagonal de acero inoxidable 304, 1/4" x 2"',
                'unit': 'pza',
                'type': 'Insumo',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_material': 'MAT-002',
                'name': 'Madera de pino',
                'description': 'Tabla de madera de pino 2x4 pulgadas, grado estructural',
                'unit': 'm',
                'type': 'Materia Prima',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_material': 'MAT-003',
                'name': 'Pintura blanca mate',
                'description': 'Pintura blanca mate para interiores, base agua, 1 litro',
                'unit': 'L',
                'type': 'Insumo',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_material': 'MAT-004',
                'name': 'Lamina acero galvanizado',
                'description': 'Lámina de acero galvanizado calibre 22, 4x8 pies',
                'unit': 'pza',
                'type': 'Materia Prima',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_material': 'MAT-005',
                'name': 'Caja de clavos',
                'description': 'Caja de clavos de acero de 2-1/2", 5 kg',
                'unit': 'cja',
                'type': 'Insumo',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_material': 'MAT-006',
                'name': 'Taladro eléctrico',
                'description': 'Taladro eléctrico percutor 1/2", 650W, con maletín',
                'unit': 'pza',
                'type': 'Herramienta',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_material': 'MAT-007',
                'name': 'Resma de papel bond',
                'description': 'Resma de papel bond A4, 75 gr, 500 hojas',
                'unit': 'pza',
                'type': 'Material de Oficina',
                'status': True,
                'created_by': 'admin'
            },
            {
                'id_material': 'MAT-008',
                'name': 'Caja de tornillos autorroscantes',
                'description': 'Caja de tornillos autorroscantes para madera, #8 x 1-1/4", 100 pzas',
                'unit': 'cja',
                'type': 'Insumo',
                'status': False,
                'created_by': 'admin'
            }
        ]
        
        materials_created = 0
        for material_data in example_materials:
            material = Material.query.filter_by(id_material=material_data['id_material']).first()
            if not material:
                material = Material(**material_data)
                db.session.add(material)
                materials_created += 1
        
        db.session.commit()
        print(f"✓ Materiales de ejemplo creados: {materials_created}")
        
        # Mostrar resumen final
        print("\n" + "="*50)
        print("✅ MÓDULO DE MATERIALES INICIALIZADO EXITOSAMENTE")
        print("="*50)
        print(f"📦 Unidades de medida: {Unit.query.count()}")
        print(f"🏷️  Tipos de material: {MaterialType.query.count()}")
        print(f"📋 Materiales creados: {Material.query.count()}")
        print("\n📊 Materiales por tipo:")
        for material_type in MaterialType.query.all():
            count = Material.query.filter_by(type=material_type.name).count()
            print(f"   - {material_type.name}: {count} materiales")
        
        print("\n🎯 Próximos pasos:")
        print("   1. Accede al módulo de materiales desde el dashboard")
        print("   2. Verifica que los materiales de ejemplo estén cargados")
        print("   3. Prueba los filtros y la exportación CSV")
        print("   4. Usa la carga masiva para agregar más materiales")

if __name__ == '__main__':
    init_materials_module()