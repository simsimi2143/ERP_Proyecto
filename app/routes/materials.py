from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Material, Unit, MaterialType
from app.utils.auth import permission_required
import csv
import io
from datetime import datetime

bp = Blueprint('materials', __name__)

@bp.route('/materials')
@login_required
@permission_required('materials', 1)
def material_list():
    # Obtener parámetros de filtro
    id_material_filter = request.args.get('id_material', '')
    name_filter = request.args.get('name', '')
    type_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '')
    
    # Construir consulta base
    query = Material.query
    
    # Aplicar filtros
    if id_material_filter:
        query = query.filter(Material.id_material.contains(id_material_filter))
    if name_filter:
        query = query.filter(Material.name.contains(name_filter))
    if type_filter:
        query = query.filter(Material.type == type_filter)
    if status_filter:
        status_bool = status_filter == 'true'
        query = query.filter(Material.status == status_bool)
    
    materials = query.order_by(Material.created_at.desc()).all()
    material_types = MaterialType.query.all()
    
    return render_template('materials/list.html', 
                         materials=materials, 
                         material_types=material_types,
                         filters=request.args)

@bp.route('/materials/create', methods=['GET', 'POST'])
@login_required
@permission_required('materials', 2)
def material_create():
    if request.method == 'POST':
        try:
            material = Material(
                id_material=request.form['id_material'],
                name=request.form['name'],
                description=request.form['description'],
                unit=request.form['unit'],
                type=request.form['type'],
                status=request.form.get('status') == 'on',
                created_by=current_user.username
            )
            
            db.session.add(material)
            db.session.commit()
            flash('Material creado exitosamente', 'success')
            return redirect(url_for('materials.material_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear material: {str(e)}', 'error')
    
    units = Unit.query.all()
    material_types = MaterialType.query.all()
    return render_template('materials/create.html', units=units, material_types=material_types)

@bp.route('/materials/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('materials', 2)
def material_edit(material_id):
    material = Material.query.get_or_404(material_id)
    
    if request.method == 'POST':
        try:
            material.id_material = request.form['id_material']
            material.name = request.form['name']
            material.description = request.form['description']
            material.unit = request.form['unit']
            material.type = request.form['type']
            material.status = request.form.get('status') == 'on'
            material.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Material actualizado exitosamente', 'success')
            return redirect(url_for('materials.material_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar material: {str(e)}', 'error')
    
    units = Unit.query.all()
    material_types = MaterialType.query.all()
    return render_template('materials/edit.html', 
                         material=material, 
                         units=units, 
                         material_types=material_types)

@bp.route('/materials/<int:material_id>/delete', methods=['POST'])
@login_required
@permission_required('materials', 2)
def material_delete(material_id):
    material = Material.query.get_or_404(material_id)
    
    try:
        db.session.delete(material)
        db.session.commit()
        flash('Material eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar material: {str(e)}', 'error')
    
    return redirect(url_for('materials.material_list'))

@bp.route('/materials/export_csv')
@login_required
@permission_required('materials', 1)
def export_csv():
    # Obtener los mismos filtros de la lista
    id_material_filter = request.args.get('id_material', '')
    name_filter = request.args.get('name', '')
    type_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '')
    
    # Construir consulta base (igual que en material_list)
    query = Material.query
    
    if id_material_filter:
        query = query.filter(Material.id_material.contains(id_material_filter))
    if name_filter:
        query = query.filter(Material.name.contains(name_filter))
    if type_filter:
        query = query.filter(Material.type == type_filter)
    if status_filter:
        status_bool = status_filter == 'true'
        query = query.filter(Material.status == status_bool)
    
    
    materials = query.order_by(Material.created_at.desc()).all()
    
    # Crear CSV en memoria con encoding para Excel
    output = io.StringIO()
    
    # Crear writer con delimitador de coma y quoting para Excel
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,  # Esto fuerza comillas en todos los campos
                       lineterminator='\n')
    
    # Encabezados en español (asegurarse de que no haya caracteres especiales problemáticos)
    headers = [
        'ID_Material',
        'Nombre', 
        'Descripcion',
        'Unidad',
        'Tipo',
        'Estado',
        'Creado_Por',
        'Fecha_Creacion',
        'Fecha_Actualizacion'
    ]
    writer.writerow(headers)
    
    # Datos
    for material in materials:
        writer.writerow([
            material.id_material,
            material.name,
            material.description or '',
            material.unit,
            material.type,
            'Activo' if material.status else 'Inactivo',
            material.created_by,
            material.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            material.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    # Crear nombre de archivo con fecha
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'materiales_exportacion_{timestamp}.csv'
    
    # Para Excel es importante usar utf-8-sig (BOM) para que detecte correctamente
    csv_data = output.getvalue().encode('utf-8-sig')
    
    return send_file(
        io.BytesIO(csv_data),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/materials/bulk_upload')
@login_required
@permission_required('materials', 2)
def bulk_upload():
    return render_template('materials/bulk_upload.html')

@bp.route('/materials/download_template')
@login_required
@permission_required('materials', 2)
def download_template():
    # Crear CSV template en memoria optimizado para Excel
    output = io.StringIO()
    
    # Usar el mismo formato que en export_csv
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    # Encabezados con ejemplos
    writer.writerow(['ID_Material', 'Nombre', 'Descripcion', 'Unidad', 'Tipo', 'Estado'])
    writer.writerow(['MAT-001', 'Tornillo hexagonal', 'Tornillo hexagonal acero inoxidable', 'pza', 'Insumo', '1'])
    writer.writerow(['MAT-002', 'Madera pino', 'Tabla de madera de pino 2x4', 'm', 'Materia Prima', '1'])
    writer.writerow(['MAT-003', 'Pintura blanca', 'Pintura blanca mate 1L', 'L', 'Insumo', '0'])
    writer.writerow(['', '', '', '', '', ''])
    writer.writerow(['NOTAS:', '', '', '', '', ''])
    writer.writerow(['- ID_Material: Debe ser único', '', '', '', '', ''])
    writer.writerow(['- Estado: 1=Activo, 0=Inactivo', '', '', '', '', ''])
    writer.writerow(['- Unidad: Usar símbolos como pza, kg, m, L, etc.', '', '', '', '', ''])
    writer.writerow(['- Tipo: Usar tipos existentes en el sistema', '', '', '', '', ''])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name='plantilla_carga_materiales.csv'
    )

@bp.route('/materials/process_bulk_upload', methods=['POST'])
@login_required
@permission_required('materials', 2)
def process_bulk_upload():
    if 'csv_file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('materials.bulk_upload'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('materials.bulk_upload'))
    
    if not file.filename.endswith('.csv'):
        flash('El archivo debe ser un CSV', 'error')
        return redirect(url_for('materials.bulk_upload'))
    
    try:
        # Leer el archivo CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.reader(stream)
        
        # Saltar el encabezado
        header = next(csv_reader, None)
        
        materials_created = 0
        materials_updated = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # start=2 porque la primera fila es encabezado
            if len(row) < 6:
                errors.append(f"Fila {row_num}: No tiene suficientes columnas")
                continue
            
            try:
                id_material, name, description, unit, material_type, status_str = row[:6]
                
                # Validar campos obligatorios
                if not id_material or not name or not unit or not material_type:
                    errors.append(f"Fila {row_num}: Campos obligatorios faltantes")
                    continue
                
                # Validar que el tipo de material exista
                if not MaterialType.query.filter_by(name=material_type).first():
                    errors.append(f"Fila {row_num}: Tipo de material '{material_type}' no existe")
                    continue
                
                # Validar estado
                status = status_str.strip() == '1' if status_str else True
                
                # Verificar si el material ya existe
                existing_material = Material.query.filter_by(id_material=id_material).first()
                
                if existing_material:
                    # Actualizar material existente
                    existing_material.name = name
                    existing_material.description = description
                    existing_material.unit = unit
                    existing_material.type = material_type
                    existing_material.status = status
                    existing_material.updated_at = datetime.utcnow()
                    materials_updated += 1
                else:
                    # Crear nuevo material
                    material = Material(
                        id_material=id_material,
                        name=name,
                        description=description,
                        unit=unit,
                        type=material_type,
                        status=status,
                        created_by=current_user.username
                    )
                    db.session.add(material)
                    materials_created += 1
                    
            except Exception as e:
                errors.append(f"Fila {row_num}: Error procesando - {str(e)}")
                continue
        
        # Confirmar cambios en la base de datos
        db.session.commit()
        
        # Mostrar resultados
        if materials_created > 0 or materials_updated > 0:
            flash(f'Carga masiva completada: {materials_created} materiales creados, {materials_updated} actualizados', 'success')
        
        if errors:
            error_msg = f'Se encontraron {len(errors)} errores durante la carga:'
            for error in errors[:10]:  # Mostrar solo los primeros 10 errores
                error_msg += f'<br>- {error}'
            if len(errors) > 10:
                error_msg += f'<br>... y {len(errors) - 10} errores más'
            flash(error_msg, 'warning')
        
        if not materials_created and not materials_updated and not errors:
            flash('No se procesó ningún material. Verifique el formato del archivo.', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error procesando el archivo: {str(e)}', 'error')
    
    return redirect(url_for('materials.material_list'))