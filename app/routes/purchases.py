from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models import PurchaseOrder, PurchaseOrderLine, Supplier, Material, Currency
from app.models import Location, InventoryStock, InventoryMovement
from app.utils.auth import permission_required
import csv
import io
from datetime import datetime

bp = Blueprint('purchases', __name__)

@bp.route('/purchases')
@login_required
@permission_required('purchases', 1)
def purchase_list():
    # Obtener parámetros de filtro
    id_purchase_order_filter = request.args.get('id_purchase_order', '')
    id_supplier_filter = request.args.get('id_supplier', '')
    status_filter = request.args.get('status', '')
    
    # Construir consulta base
    query = PurchaseOrder.query
    
    # Aplicar filtros
    if id_purchase_order_filter:
        query = query.filter(PurchaseOrder.id_purchase_order.contains(id_purchase_order_filter))
    if id_supplier_filter:
        query = query.filter(PurchaseOrder.id_supplier == id_supplier_filter)  # Cambiado a igualdad exacta
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)
    
    orders = query.order_by(PurchaseOrder.created_at.desc()).all()
    
    # Obtener información de proveedores para mostrar y para el filtro
    suppliers = Supplier.query.filter_by(status=True).all()
    supplier_dict = {s.id_suplier: s.name for s in suppliers}
    
    return render_template('purchases/list.html', 
                         orders=orders, 
                         supplier_dict=supplier_dict,
                         suppliers=suppliers,  # Agregar esta línea
                         filters=request.args)

@bp.route('/purchases/create', methods=['GET', 'POST'])
@login_required
@permission_required('purchases', 2)
def purchase_create():
    if request.method == 'POST':
        try:
            # Crear la orden de compra
            order = PurchaseOrder(
                id_purchase_order=request.form['id_purchase_order'],
                id_supplier=request.form['id_supplier'],
                issue_date=datetime.strptime(request.form['issue_date'], '%Y-%m-%d'),
                estimated_delivery_date=datetime.strptime(request.form['estimated_delivery_date'], '%Y-%m-%d'),
                status=request.form['status'],
                currency=request.form['currency'],
                notes=request.form.get('notes', ''),
                created_by=current_user.username
            )
            
            db.session.add(order)
            
            # Procesar líneas de la orden
            line_count = int(request.form.get('line_count', 0))
            total_amount = 0
            
            for i in range(1, line_count + 1):
                if request.form.get(f'id_material_{i}'):
                    line = PurchaseOrderLine(
                        id_purchase_order_line=f"{order.id_purchase_order}-{i}",
                        id_purchase_order=order.id_purchase_order,
                        id_material=request.form[f'id_material_{i}'],
                        position=i,
                        quantity=int(request.form[f'quantity_{i}']),
                        unit_material=request.form[f'unit_material_{i}'],
                        price=float(request.form[f'price_{i}']),
                        currency_suppliers=request.form[f'currency_suppliers_{i}'],
                        created_by=current_user.username
                    )
                    db.session.add(line)
                    total_amount += line.quantity * line.price
            
            # Actualizar monto total
            order.total_amount = total_amount
            
            db.session.commit()
            flash('Orden de compra creada exitosamente', 'success')
            return redirect(url_for('purchases.purchase_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear orden de compra: {str(e)}', 'error')
    
    suppliers = Supplier.query.filter_by(status=True).all()
    materials = Material.query.filter_by(status=True).all()
    currencies = Currency.query.all()
    
    return render_template('purchases/create.html', 
                         suppliers=suppliers, 
                         materials=materials,
                         currencies=currencies)

@bp.route('/purchases/<string:order_id>')
@login_required
@permission_required('purchases', 1)
def purchase_detail(order_id):
    order = PurchaseOrder.query.filter_by(id_purchase_order=order_id).first_or_404()
    lines = PurchaseOrderLine.query.filter_by(id_purchase_order=order_id).order_by(PurchaseOrderLine.position).all()
    supplier = Supplier.query.filter_by(id_suplier=order.id_supplier).first()
    
    # Obtener información de materiales
    materials = Material.query.all()
    material_dict = {m.id_material: m for m in materials}
    
    # Obtener ubicaciones para recepción
    locations = Location.query.filter_by(status=True).all()
    
    return render_template('purchases/detail.html', 
                         order=order, 
                         lines=lines,
                         supplier=supplier,
                         material_dict=material_dict,
                         locations=locations)  # Agregar esta línea

@bp.route('/purchases/<string:order_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('purchases', 2)
def purchase_edit(order_id):
    order = PurchaseOrder.query.filter_by(id_purchase_order=order_id).first_or_404()
    lines = PurchaseOrderLine.query.filter_by(id_purchase_order=order_id).order_by(PurchaseOrderLine.position).all()
    
    if request.method == 'POST':
        try:
            order.id_supplier = request.form['id_supplier']
            order.issue_date = datetime.strptime(request.form['issue_date'], '%Y-%m-%d')
            order.estimated_delivery_date = datetime.strptime(request.form['estimated_delivery_date'], '%Y-%m-%d')
            order.status = request.form['status']
            order.currency = request.form['currency']
            order.notes = request.form.get('notes', '')
            order.updated_at = datetime.utcnow()
            
            # Eliminar líneas existentes
            PurchaseOrderLine.query.filter_by(id_purchase_order=order_id).delete()
            
            # Procesar nuevas líneas
            line_count = int(request.form.get('line_count', 0))
            total_amount = 0
            
            for i in range(1, line_count + 1):
                if request.form.get(f'id_material_{i}'):
                    line = PurchaseOrderLine(
                        id_purchase_order_line=f"{order.id_purchase_order}-{i}",
                        id_purchase_order=order.id_purchase_order,
                        id_material=request.form[f'id_material_{i}'],
                        position=i,
                        quantity=int(request.form[f'quantity_{i}']),
                        unit_material=request.form[f'unit_material_{i}'],
                        price=float(request.form[f'price_{i}']),
                        currency_suppliers=request.form[f'currency_suppliers_{i}'],
                        created_by=current_user.username
                    )
                    db.session.add(line)
                    total_amount += line.quantity * line.price
            
            # Actualizar monto total
            order.total_amount = total_amount
            
            db.session.commit()
            flash('Orden de compra actualizada exitosamente', 'success')
            return redirect(url_for('purchases.purchase_detail', order_id=order.id_purchase_order))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar orden de compra: {str(e)}', 'error')
    
    suppliers = Supplier.query.filter_by(status=True).all()
    materials = Material.query.filter_by(status=True).all()
    currencies = Currency.query.all()
    
    return render_template('purchases/edit.html', 
                         order=order, 
                         lines=lines,
                         suppliers=suppliers, 
                         materials=materials,
                         currencies=currencies)

@bp.route('/purchases/<string:order_id>/delete', methods=['POST'])
@login_required
@permission_required('purchases', 2)
def purchase_delete(order_id):
    order = PurchaseOrder.query.filter_by(id_purchase_order=order_id).first_or_404()
    
    try:
        # Eliminar líneas primero
        PurchaseOrderLine.query.filter_by(id_purchase_order=order_id).delete()
        # Eliminar orden
        db.session.delete(order)
        db.session.commit()
        flash('Orden de compra eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar orden de compra: {str(e)}', 'error')
    
    return redirect(url_for('purchases.purchase_list'))

@bp.route('/purchases/export_csv')
@login_required
@permission_required('purchases', 1)
def export_csv():
    # Obtener los mismos filtros de la lista
    id_purchase_order_filter = request.args.get('id_purchase_order', '')
    id_supplier_filter = request.args.get('id_supplier', '')
    status_filter = request.args.get('status', '')
    
    # Construir consulta base
    query = PurchaseOrder.query
    
    if id_purchase_order_filter:
        query = query.filter(PurchaseOrder.id_purchase_order.contains(id_purchase_order_filter))
    if id_supplier_filter:
        query = query.filter(PurchaseOrder.id_supplier.contains(id_supplier_filter))
    if status_filter:
        query = query.filter(PurchaseOrder.status == status_filter)
    
    orders = query.order_by(PurchaseOrder.created_at.desc()).all()
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    # Encabezados
    headers = [
        'ID_Orden_Compra',
        'ID_Proveedor',
        'Fecha_Emision',
        'Fecha_Estimada_Entrega',
        'Estado',
        'Monto_Total',
        'Moneda',
        'Notas',
        'Creado_Por',
        'Fecha_Creacion',
        'Fecha_Actualizacion'
    ]
    writer.writerow(headers)
    
    # Datos
    for order in orders:
        writer.writerow([
            order.id_purchase_order,
            order.id_supplier,
            order.issue_date.strftime('%Y-%m-%d'),
            order.estimated_delivery_date.strftime('%Y-%m-%d'),
            order.status,
            order.total_amount,
            order.currency,
            order.notes or '',
            order.created_by,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            order.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    # Crear nombre de archivo con fecha
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'ordenes_compra_exportacion_{timestamp}.csv'
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/api/materials/<string:material_id>')
@login_required
def get_material_info(material_id):
    material = Material.query.filter_by(id_material=material_id).first()
    if material:
        return jsonify({
            'name': material.name,
            'unit': material.unit,
            'description': material.description
        })
    return jsonify({'error': 'Material no encontrado'}), 404

@bp.route('/purchases/bulk_upload')
@login_required
@permission_required('purchases', 2)
def bulk_upload():
    """Mostrar página de carga masiva"""
    return render_template('purchases/bulk_upload.html')

@bp.route('/purchases/download_template')
@login_required
@permission_required('purchases', 2)
def download_template():
    """Descargar plantilla CSV para carga masiva"""
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    # Encabezados de la plantilla
    headers = [
        'ID_Orden_Compra',
        'ID_Proveedor',
        'Fecha_Emision',
        'Fecha_Estimada_Entrega',
        'Estado',
        'Moneda',
        'Notas'
    ]
    writer.writerow(headers)
    
    # Ejemplo de datos
    writer.writerow([
        'OC-2024-001',
        'PROV-001',
        '2024-01-15',
        '2024-02-01',
        'Pendiente',
        'MXN',
        'Notas de ejemplo'
    ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name='plantilla_ordenes_compra.csv'
    )

@bp.route('/purchases/process_bulk_upload', methods=['POST'])
@login_required
@permission_required('purchases', 2)
def process_bulk_upload():
    """Procesar archivo CSV de carga masiva"""
    try:
        if 'csv_file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('purchases.bulk_upload'))
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('purchases.bulk_upload'))
        
        if file and file.filename.endswith('.csv'):
            # Leer el archivo CSV
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream, delimiter=',')
            
            orders_created = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, 2):  # row_num empieza en 2 (fila 1 es encabezado)
                try:
                    # Validar campos obligatorios
                    required_fields = ['ID_Orden_Compra', 'ID_Proveedor', 'Fecha_Emision', 
                                     'Fecha_Estimada_Entrega', 'Estado', 'Moneda']
                    for field in required_fields:
                        if not row.get(field):
                            errors.append(f"Fila {row_num}: Campo '{field}' es obligatorio")
                            continue
                    
                    # Verificar si la orden ya existe
                    existing_order = PurchaseOrder.query.filter_by(
                        id_purchase_order=row['ID_Orden_Compra']
                    ).first()
                    
                    if existing_order:
                        errors.append(f"Fila {row_num}: La orden {row['ID_Orden_Compra']} ya existe")
                        continue
                    
                    # Verificar que el proveedor exista
                    supplier = Supplier.query.filter_by(id_suplier=row['ID_Proveedor']).first()
                    if not supplier:
                        errors.append(f"Fila {row_num}: El proveedor {row['ID_Proveedor']} no existe")
                        continue
                    
                    # Crear la orden
                    order = PurchaseOrder(
                        id_purchase_order=row['ID_Orden_Compra'],
                        id_supplier=row['ID_Proveedor'],
                        issue_date=datetime.strptime(row['Fecha_Emision'], '%Y-%m-%d'),
                        estimated_delivery_date=datetime.strptime(row['Fecha_Estimada_Entrega'], '%Y-%m-%d'),
                        status=row['Estado'],
                        currency=row['Moneda'],
                        notes=row.get('Notas', ''),
                        total_amount=0.0,  # Se puede calcular si hay líneas en el CSV
                        created_by=current_user.username
                    )
                    
                    db.session.add(order)
                    orders_created += 1
                    
                except Exception as e:
                    errors.append(f"Fila {row_num}: Error - {str(e)}")
                    continue
            
            if errors:
                db.session.rollback()
                flash(f'Se crearon {orders_created} órdenes. Errores: {" | ".join(errors[:5])}', 'error')  # Mostrar solo primeros 5 errores
            else:
                db.session.commit()
                flash(f'Carga masiva completada: {orders_created} órdenes creadas exitosamente', 'success')
            
            return redirect(url_for('purchases.purchase_list'))
        
        else:
            flash('Formato de archivo no válido. Solo se permiten archivos CSV.', 'error')
            return redirect(url_for('purchases.bulk_upload'))
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar el archivo: {str(e)}', 'error')
        return redirect(url_for('purchases.bulk_upload'))
    
# estado de la orden registra en inventario
@bp.route('/purchases/<string:order_id>/receive', methods=['POST'])
@login_required
@permission_required('purchases', 2)
def purchase_receive(order_id):
    """Procesar recepción de orden de compra y registrar en inventario"""
    order = PurchaseOrder.query.filter_by(id_purchase_order=order_id).first_or_404()
    
    if order.status != 'Recibida':
        flash('La orden debe estar en estado "Recibida" para procesar la recepción', 'error')
        return redirect(url_for('purchases.purchase_detail', order_id=order_id))
    
    try:
        # Obtener ubicación principal
        main_location = Location.query.filter_by(main_location=True).first()
        if not main_location:
            flash('No hay ubicación principal configurada', 'error')
            return redirect(url_for('purchases.purchase_detail', order_id=order_id))
        
        lines = PurchaseOrderLine.query.filter_by(id_purchase_order=order_id).all()
        movements_created = 0
        
        for line in lines:
            # Solo procesar si no ha sido recibido completamente
            if line.resolved_quantity < line.quantity:
                # Calcular cantidad pendiente
                pending_quantity = line.quantity - line.resolved_quantity
                
                # Crear movimiento de entrada
                movement = InventoryMovement(
                    id_location=main_location.id,
                    id_material=line.id_material,
                    quantity=pending_quantity,
                    unit_type=line.unit_material,
                    movement_type='ENTRADA',
                    notes=f'Recepcion orden {order.id_purchase_order}',
                    created_by=current_user.username
                )
                db.session.add(movement)
                
                # Actualizar stock
                stock = InventoryStock.query.filter_by(
                    id_location=main_location.id,
                    id_material=line.id_material
                ).first()
                
                if not stock:
                    stock = InventoryStock(
                        id_location=main_location.id,
                        id_material=line.id_material,
                        quantity=0,
                        unit_type=line.unit_material,
                        created_by=current_user.username
                    )
                    db.session.add(stock)
                
                stock.quantity += pending_quantity
                stock.last_movement = datetime.utcnow()
                
                # Actualizar cantidad recibida en la línea
                line.resolved_quantity += pending_quantity
                movements_created += 1
        
        db.session.commit()
        
        if movements_created > 0:
            flash(f'Recepción procesada: {movements_created} movimientos creados', 'success')
        else:
            flash('No hay cantidades pendientes por recibir', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('purchases.purchase_detail', order_id=order_id))

@bp.route('/purchases/<string:order_id>/receive_partial', methods=['POST'])
@login_required
@permission_required('purchases', 2)
def purchase_receive_partial(order_id):
    """Recepcion parcial de una orden de compra"""
    order = PurchaseOrder.query.filter_by(id_purchase_order=order_id).first_or_404()
    
    try:
        location_id = request.form.get('location_id')
        if not location_id:
            flash('Debe seleccionar una ubicación', 'error')
            return redirect(url_for('purchases.purchase_detail', order_id=order_id))
        
        location = Location.query.get(location_id)
        if not location:
            flash('Ubicación no válida', 'error')
            return redirect(url_for('purchases.purchase_detail', order_id=order_id))
        
        # Procesar cada línea con cantidades parciales
        movements_created = 0
        
        for line in PurchaseOrderLine.query.filter_by(id_purchase_order=order_id).all():
            received_qty = request.form.get(f'received_qty_{line.id}')
            
            if received_qty and float(received_qty) > 0:
                received_qty = int(received_qty)
                pending_quantity = line.quantity - line.resolved_quantity
                
                if received_qty > pending_quantity:
                    flash(f'La cantidad recibida para {line.id_material} excede la pendiente', 'warning')
                    continue
                
                # Crear movimiento de entrada
                movement = InventoryMovement(
                    id_location=location_id,
                    id_material=line.id_material,
                    quantity=received_qty,
                    unit_type=line.unit_material,
                    movement_type='ENTRADA',
                    notes=f'Recepcion parcial orden {order.id_purchase_order} - Proveedor: {order.id_supplier}',
                    created_by=current_user.username
                )
                db.session.add(movement)
                
                # Actualizar stock
                stock = InventoryStock.query.filter_by(
                    id_location=location_id,
                    id_material=line.id_material
                ).first()
                
                if not stock:
                    stock = InventoryStock(
                        id_location=location_id,
                        id_material=line.id_material,
                        quantity=0,
                        unit_type=line.unit_material,
                        created_by=current_user.username
                    )
                    db.session.add(stock)
                
                stock.quantity += received_qty
                stock.last_movement = datetime.utcnow()
                stock.updated_at = datetime.utcnow()
                
                # Actualizar cantidad recibida
                line.resolved_quantity += received_qty
                line.updated_at = datetime.utcnow()
                
                movements_created += 1
        
        order.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Recepcion parcial completada: {movements_created} movimientos registrados', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error en recepcion parcial: {str(e)}', 'error')
    
    return redirect(url_for('purchases.purchase_detail', order_id=order_id)) 


@bp.route('/debug/order/<string:order_id>')
@login_required
def debug_order(order_id):
    """Depurar datos de una orden"""
    order = PurchaseOrder.query.filter_by(id_purchase_order=order_id).first_or_404()
    lines = PurchaseOrderLine.query.filter_by(id_purchase_order=order_id).all()
    
    debug_info = {
        'order': {
            'id': order.id_purchase_order,
            'status': order.status,
            'supplier': order.id_supplier
        },
        'lines': []
    }
    
    for line in lines:
        debug_info['lines'].append({
            'material': line.id_material,
            'quantity': line.quantity,
            'resolved_quantity': line.resolved_quantity,
            'pending': line.quantity - line.resolved_quantity
        })
    
    # Verificar movimientos de inventario
    movements = []
    for line in lines:
        movement = InventoryMovement.query.filter_by(
            id_material=line.id_material
        ).filter(
            InventoryMovement.notes.contains(order_id)
        ).first()
        
        if movement:
            movements.append({
                'material': movement.id_material,
                'quantity': movement.quantity,
                'type': movement.movement_type,
                'notes': movement.notes
            })
    
    debug_info['inventory_movements'] = movements
    
    return jsonify(debug_info)