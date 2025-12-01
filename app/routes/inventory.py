# app/routes/inventory.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify,send_file
from flask_login import login_required, current_user
from app import db
from app.models import Location, InventoryMovement, InventoryStock, Material, Unit
from app.utils.auth import permission_required
from datetime import datetime
import csv
import io

bp = Blueprint('inventory', __name__)

@bp.route('/inventory')
@login_required
@permission_required('inventory', 1)
def inventory_list():
    # Obtener parámetros de filtro
    location_filter = request.args.get('location', '')
    material_filter = request.args.get('material', '')
    
    # Construir consulta base
    query = InventoryStock.query
    
    # Aplicar filtros
    if location_filter:
        query = query.filter(InventoryStock.id_location == location_filter)
    if material_filter:
        # Cambiar de contains a igualdad exacta
        query = query.filter(InventoryStock.id_material == material_filter)
    
    stocks = query.order_by(InventoryStock.updated_at.desc()).all()
    
    locations = Location.query.filter_by(status=True).all()
    materials = Material.query.filter_by(status=True).order_by(Material.name).all()  # Ordenar por nombre
    
    return render_template('inventory/list.html', 
                         stocks=stocks,
                         locations=locations,
                         materials=materials,
                         filters=request.args)

@bp.route('/inventory/movements')
@login_required
@permission_required('inventory', 1)
def movement_list():
    # Obtener parámetros de filtro
    location_filter = request.args.get('location', '')
    material_filter = request.args.get('material', '')
    movement_type_filter = request.args.get('movement_type', '')
    
    # Construir consulta base
    query = InventoryMovement.query
    
    # Aplicar filtros
    if location_filter:
        query = query.filter(InventoryMovement.id_location == location_filter)
    if material_filter:
        query = query.filter(InventoryMovement.id_material.contains(material_filter))
    if movement_type_filter:
        query = query.filter(InventoryMovement.movement_type == movement_type_filter)
    
    movements = query.order_by(InventoryMovement.created_at.desc()).all()
    
    locations = Location.query.filter_by(status=True).all()
    materials = Material.query.filter_by(status=True).all()
    
    return render_template('inventory/movements.html', 
                         movements=movements,
                         locations=locations,
                         materials=materials,
                         filters=request.args)

@bp.route('/inventory/movement/create', methods=['GET', 'POST'])
@login_required
@permission_required('inventory', 2)
def movement_create():
    if request.method == 'POST':
        try:
            movement = InventoryMovement(
                id_location=request.form['id_location'],
                id_material=request.form['id_material'],
                quantity=int(request.form['quantity']),
                unit_type=request.form['unit_type'],
                movement_type=request.form['movement_type'],
                notes=request.form.get('notes', ''),
                created_by=current_user.username
            )
            
            db.session.add(movement)
            
            # Actualizar stock
            stock = InventoryStock.query.filter_by(
                id_location=movement.id_location,
                id_material=movement.id_material
            ).first()
            
            if not stock:
                stock = InventoryStock(
                    id_location=movement.id_location,
                    id_material=movement.id_material,
                    quantity=0,
                    unit_type=movement.unit_type,
                    created_by=current_user.username
                )
                db.session.add(stock)
            
            # Ajustar stock según el tipo de movimiento
            if movement.movement_type == 'ENTRADA':
                stock.quantity += movement.quantity
            elif movement.movement_type == 'SALIDA':
                stock.quantity -= movement.quantity
            elif movement.movement_type == 'AJUSTE':
                stock.quantity = movement.quantity
            
            stock.last_movement = datetime.utcnow()
            stock.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Movimiento de inventario registrado exitosamente', 'success')
            return redirect(url_for('inventory.movement_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar movimiento: {str(e)}', 'error')
    
    locations = Location.query.filter_by(status=True).all()
    materials = Material.query.filter_by(status=True).all()
    
    return render_template('inventory/movement_create.html', 
                         locations=locations,
                         materials=materials)

@bp.route('/inventory/locations')
@login_required
@permission_required('inventory', 1)
def location_list():
    locations = Location.query.order_by(Location.name).all()
    return render_template('inventory/locations.html', locations=locations)

@bp.route('/inventory/location/create', methods=['GET', 'POST'])
@login_required
@permission_required('inventory', 2)
def location_create():
    if request.method == 'POST':
        try:
            location = Location(
                name=request.form['name'],
                code=request.form['code'],
                main_location=bool(request.form.get('main_location')),
                location=request.form.get('location', ''),
                created_by=current_user.username
            )
            
            db.session.add(location)
            db.session.commit()
            flash('Ubicación creada exitosamente', 'success')
            return redirect(url_for('inventory.location_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear ubicación: {str(e)}', 'error')
    
    return render_template('inventory/location_create.html')

@bp.route('/inventory/location/<int:location_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('inventory', 2)
def location_edit(location_id):
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'POST':
        try:
            location.name = request.form['name']
            location.code = request.form['code']
            location.main_location = bool(request.form.get('main_location'))
            location.location = request.form.get('location', '')
            location.status = bool(request.form.get('status'))
            
            db.session.commit()
            flash('Ubicación actualizada exitosamente', 'success')
            return redirect(url_for('inventory.location_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar ubicación: {str(e)}', 'error')
    
    return render_template('inventory/location_edit.html', location=location)

@bp.route('/inventory/stock/<int:stock_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('inventory', 2)
def stock_edit(stock_id):
    stock = InventoryStock.query.get_or_404(stock_id)
    
    if request.method == 'POST':
        try:
            stock.min_stock = int(request.form['min_stock'])
            stock.max_stock = int(request.form['max_stock'])
            
            db.session.commit()
            flash('Stock actualizado exitosamente', 'success')
            return redirect(url_for('inventory.inventory_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar stock: {str(e)}', 'error')
    
    return render_template('inventory/stock_edit.html', stock=stock)

@bp.route('/api/inventory/stock')
@login_required
def get_stock_info():
    location_id = request.args.get('location_id')
    material_id = request.args.get('material_id')
    
    stock = InventoryStock.query.filter_by(
        id_location=location_id,
        id_material=material_id
    ).first()
    
    if stock:
        return jsonify({
            'current_stock': stock.quantity,
            'unit_type': stock.unit_type
        })
    return jsonify({'current_stock': 0, 'unit_type': ''})

@bp.route('/inventory/export_stock')
@login_required
@permission_required('inventory', 1)
def export_stock():
    import csv
    import io
    from datetime import datetime
    
    stocks = InventoryStock.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    headers = [
        'Ubicación', 'Material', 'Stock Actual', 'Unidad',
        'Stock Mínimo', 'Stock Máximo', 'Último Movimiento'
    ]
    writer.writerow(headers)
    
    for stock in stocks:
        writer.writerow([
            stock.location.name,
            f"{stock.material.id_material} - {stock.material.name}",
            stock.quantity,
            stock.unit_type,
            stock.min_stock,
            stock.max_stock,
            stock.last_movement.strftime('%Y-%m-%d %H:%M') if stock.last_movement else ''
        ])
    
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'inventario_stock_{timestamp}.csv'
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name=filename
    )
    
@bp.route('/inventory/stock/<int:stock_id>/delete', methods=['POST'])
@login_required
@permission_required('inventory', 2)
def stock_delete(stock_id):
    stock = InventoryStock.query.get_or_404(stock_id)
    
    try:
        # Verificar si hay movimientos asociados a este stock
        movements = InventoryMovement.query.filter_by(
            id_location=stock.id_location,
            id_material=stock.id_material
        ).first()
        
        if movements:
            flash('No se puede eliminar el stock porque tiene movimientos asociados. Elimine primero los movimientos.', 'error')
        else:
            db.session.delete(stock)
            db.session.commit()
            flash('Stock eliminado exitosamente', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar stock: {str(e)}', 'error')
    
    return redirect(url_for('inventory.inventory_list'))  

@bp.route('/inventory/bulk_upload')
@login_required
@permission_required('inventory', 2)
def bulk_upload():
    """Mostrar página de carga masiva"""
    return render_template('inventory/bulk_upload.html')

@bp.route('/inventory/download_movement_template')
@login_required
@permission_required('inventory', 2)
def download_movement_template():
    """Descargar plantilla CSV para carga masiva de movimientos"""
    output = io.StringIO()
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    # Encabezados de la plantilla
    headers = [
        'ID_Ubicacion',
        'ID_Material',
        'Cantidad',
        'Tipo_Movimiento',
        'Unidad',
        'Notas'
    ]
    writer.writerow(headers)
    
    # Ejemplo de datos
    writer.writerow([
        '1',
        'MAT-001',
        '100',
        'ENTRADA',
        'pzas',
        'Carga inicial de inventario'
    ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name='plantilla_movimientos_inventario.csv'
    )

@bp.route('/inventory/process_bulk_upload', methods=['POST'])
@login_required
@permission_required('inventory', 2)
def process_bulk_upload():
    """Procesar archivo CSV de carga masiva de movimientos"""
    try:
        if 'csv_file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('inventory.bulk_upload'))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('inventory.bulk_upload'))
        
        if file and file.filename.endswith('.csv'):
            # Leer el archivo CSV
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream, delimiter=',')
            
            movements_created = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, 2):  # row_num empieza en 2 (fila 1 es encabezado)
                try:
                    # Validar campos obligatorios
                    required_fields = ['ID_Ubicacion', 'ID_Material', 'Cantidad', 'Tipo_Movimiento', 'Unidad']
                    for field in required_fields:
                        if not row.get(field):
                            errors.append(f"Fila {row_num}: Campo '{field}' es obligatorio")
                            continue

                    # Validar que la ubicación exista
                    location = Location.query.get(row['ID_Ubicacion'])
                    if not location:
                        errors.append(f"Fila {row_num}: La ubicación {row['ID_Ubicacion']} no existe")
                        continue

                    # Validar que el material exista
                    material = Material.query.filter_by(id_material=row['ID_Material']).first()
                    if not material:
                        errors.append(f"Fila {row_num}: El material {row['ID_Material']} no existe")
                        continue

                    # Validar cantidad
                    try:
                        quantity = int(row['Cantidad'])
                        if quantity <= 0:
                            errors.append(f"Fila {row_num}: La cantidad debe ser un entero positivo")
                            continue
                    except ValueError:
                        errors.append(f"Fila {row_num}: La cantidad debe ser un número entero")
                        continue

                    # Validar tipo de movimiento
                    movement_type = row['Tipo_Movimiento']
                    if movement_type not in ['ENTRADA', 'SALIDA', 'AJUSTE']:
                        errors.append(f"Fila {row_num}: Tipo de movimiento debe ser ENTRADA, SALIDA o AJUSTE")
                        continue

                    # Crear el movimiento
                    movement = InventoryMovement(
                        id_location=row['ID_Ubicacion'],
                        id_material=row['ID_Material'],
                        quantity=quantity,
                        unit_type=row['Unidad'],
                        movement_type=movement_type,
                        notes=row.get('Notas', ''),
                        created_by=current_user.username
                    )
                    
                    db.session.add(movement)
                    
                    # Actualizar stock
                    stock = InventoryStock.query.filter_by(
                        id_location=movement.id_location,
                        id_material=movement.id_material
                    ).first()
                    
                    if not stock:
                        stock = InventoryStock(
                            id_location=movement.id_location,
                            id_material=movement.id_material,
                            quantity=0,
                            unit_type=movement.unit_type,
                            created_by=current_user.username
                        )
                        db.session.add(stock)
                    
                    # Ajustar stock según el tipo de movimiento
                    if movement.movement_type == 'ENTRADA':
                        stock.quantity += movement.quantity
                    elif movement.movement_type == 'SALIDA':
                        # Verificar que haya suficiente stock
                        if stock.quantity < movement.quantity:
                            errors.append(f"Fila {row_num}: No hay suficiente stock para realizar la salida. Stock actual: {stock.quantity}, Se intenta retirar: {movement.quantity}")
                            db.session.rollback()
                            continue
                        stock.quantity -= movement.quantity
                    elif movement.movement_type == 'AJUSTE':
                        stock.quantity = movement.quantity
                    
                    stock.last_movement = datetime.utcnow()
                    stock.updated_at = datetime.utcnow()
                    
                    movements_created += 1
                    
                except Exception as e:
                    errors.append(f"Fila {row_num}: Error - {str(e)}")
                    continue

            if errors:
                db.session.rollback()
                # Mostrar solo los primeros 10 errores para no saturar
                flash(f'Se crearon {movements_created} movimientos. Errores: {" | ".join(errors[:10])}', 'error')
            else:
                db.session.commit()
                flash(f'Carga masiva completada: {movements_created} movimientos creados exitosamente', 'success')
            
            return redirect(url_for('inventory.movement_list'))
        
        else:
            flash('Formato de archivo no válido. Solo se permiten archivos CSV.', 'error')
            return redirect(url_for('inventory.bulk_upload'))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el archivo: {str(e)}', 'error')
        return redirect(url_for('inventory.bulk_upload')) 


@bp.route('/inventory/movement/<int:movement_id>/delete', methods=['POST'])
@login_required
@permission_required('inventory', 2)
def movement_delete(movement_id):
    movement = InventoryMovement.query.get_or_404(movement_id)
    
    try:
        # Obtener el stock asociado a este movimiento
        stock = InventoryStock.query.filter_by(
            id_location=movement.id_location,
            id_material=movement.id_material
        ).first()
        
        if stock:
            # Revertir el efecto del movimiento en el stock
            if movement.movement_type == 'ENTRADA':
                # Si era una entrada, restar la cantidad
                stock.quantity -= movement.quantity
                if stock.quantity < 0:
                    stock.quantity = 0  # Evitar valores negativos
            elif movement.movement_type == 'SALIDA':
                # Si era una salida, sumar la cantidad (devolver al stock)
                stock.quantity += movement.quantity
            elif movement.movement_type == 'AJUSTE':
                # Para ajustes, no podemos revertir automáticamente sin saber el valor anterior
                # En este caso, mantenemos el stock actual y mostramos advertencia
                flash('Advertencia: Al eliminar un ajuste, el stock actual no se modifica automáticamente. Verifique manualmente el stock.', 'warning')
            
            # Actualizar la fecha del último movimiento
            last_movement = InventoryMovement.query.filter(
                InventoryMovement.id_location == movement.id_location,
                InventoryMovement.id_material == movement.id_material,
                InventoryMovement.id != movement_id
            ).order_by(InventoryMovement.created_at.desc()).first()
            
            if last_movement:
                stock.last_movement = last_movement.created_at
            else:
                stock.last_movement = None
            
            stock.updated_at = datetime.utcnow()
        
        # Eliminar el movimiento
        db.session.delete(movement)
        db.session.commit()
        flash('Movimiento eliminado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar movimiento: {str(e)}', 'error')
    
    return redirect(url_for('inventory.movement_list'))     