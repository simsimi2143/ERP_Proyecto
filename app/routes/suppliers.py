from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Supplier, Country, Currency
from app.utils.auth import permission_required
import csv
import io
from datetime import datetime

bp = Blueprint('suppliers', __name__)

@bp.route('/suppliers')
@login_required
@permission_required('suppliers', 1)
def supplier_list():
    # Obtener parámetros de filtro
    id_suplier_filter = request.args.get('id_suplier', '')
    name_filter = request.args.get('name', '')
    country_filter = request.args.get('country', '')
    status_filter = request.args.get('status', '')
    
    # Construir consulta base
    query = Supplier.query
    
    # Aplicar filtros
    if id_suplier_filter:
        query = query.filter(Supplier.id_suplier.contains(id_suplier_filter))
    if name_filter:
        query = query.filter(Supplier.name.contains(name_filter))
    if country_filter:
        query = query.filter(Supplier.country == country_filter)
    if status_filter:
        status_bool = status_filter == 'true'
        query = query.filter(Supplier.status == status_bool)
    
    suppliers = query.order_by(Supplier.created_at.desc()).all()
    countries = Country.query.all()
    
    return render_template('suppliers/list.html', 
                         suppliers=suppliers, 
                         countries=countries,
                         filters=request.args)

@bp.route('/suppliers/create', methods=['GET', 'POST'])
@login_required
@permission_required('suppliers', 2)
def supplier_create():
    if request.method == 'POST':
        try:
            supplier = Supplier(
                id_suplier=request.form['id_suplier'],
                legal_name=request.form['legal_name'],
                name=request.form['name'],
                country=request.form['country'],
                currency=request.form['currency'],
                text_id=request.form.get('text_id', ''),
                state_province=request.form.get('state_province', ''),
                city=request.form.get('city', ''),
                address=request.form.get('address', ''),
                zip_code=request.form.get('zip_code', ''),
                phone=request.form.get('phone', ''),
                email=request.form.get('email', ''),
                contact_name=request.form.get('contact_name', ''),
                contact_role=request.form.get('contact_role', ''),
                category=request.form.get('category', ''),
                payments_terms=request.form.get('payments_terms', ''),
                payment_method=request.form.get('payment_method', ''),
                bank_account=request.form.get('bank_account', ''),
                status=request.form.get('status') == 'on',
                created_by=current_user.username
            )
            
            db.session.add(supplier)
            db.session.commit()
            flash('Proveedor creado exitosamente', 'success')
            return redirect(url_for('suppliers.supplier_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear proveedor: {str(e)}', 'error')
    
    countries = Country.query.all()
    currencies = Currency.query.all()
    return render_template('suppliers/create.html', 
                         countries=countries, 
                         currencies=currencies)

@bp.route('/suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('suppliers', 2)
def supplier_edit(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if request.method == 'POST':
        try:
            supplier.id_suplier = request.form['id_suplier']
            supplier.legal_name = request.form['legal_name']
            supplier.name = request.form['name']
            supplier.country = request.form['country']
            supplier.currency = request.form['currency']
            supplier.text_id = request.form.get('text_id', '')
            supplier.state_province = request.form.get('state_province', '')
            supplier.city = request.form.get('city', '')
            supplier.address = request.form.get('address', '')
            supplier.zip_code = request.form.get('zip_code', '')
            supplier.phone = request.form.get('phone', '')
            supplier.email = request.form.get('email', '')
            supplier.contact_name = request.form.get('contact_name', '')
            supplier.contact_role = request.form.get('contact_role', '')
            supplier.category = request.form.get('category', '')
            supplier.payments_terms = request.form.get('payments_terms', '')
            supplier.payment_method = request.form.get('payment_method', '')
            supplier.bank_account = request.form.get('bank_account', '')
            supplier.status = request.form.get('status') == 'on'
            supplier.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Proveedor actualizado exitosamente', 'success')
            return redirect(url_for('suppliers.supplier_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor: {str(e)}', 'error')
    
    countries = Country.query.all()
    currencies = Currency.query.all()
    return render_template('suppliers/edit.html', 
                         supplier=supplier, 
                         countries=countries, 
                         currencies=currencies)

@bp.route('/suppliers/<int:supplier_id>/delete', methods=['POST'])
@login_required
@permission_required('suppliers', 2)
def supplier_delete(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    
    try:
        db.session.delete(supplier)
        db.session.commit()
        flash('Proveedor eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar proveedor: {str(e)}', 'error')
    
    return redirect(url_for('suppliers.supplier_list'))

@bp.route('/suppliers/export_csv')
@login_required
@permission_required('suppliers', 1)
def export_csv():
    # Obtener los mismos filtros de la lista
    id_suplier_filter = request.args.get('id_suplier', '')
    name_filter = request.args.get('name', '')
    country_filter = request.args.get('country', '')
    status_filter = request.args.get('status', '')
    
    # Construir consulta base
    query = Supplier.query
    
    if id_suplier_filter:
        query = query.filter(Supplier.id_suplier.contains(id_suplier_filter))
    if name_filter:
        query = query.filter(Supplier.name.contains(name_filter))
    if country_filter:
        query = query.filter(Supplier.country == country_filter)
    if status_filter:
        status_bool = status_filter == 'true'
        query = query.filter(Supplier.status == status_bool)
    
    suppliers = query.order_by(Supplier.created_at.desc()).all()
    
    # Crear CSV en memoria con encoding para Excel
    output = io.StringIO()
    
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    # Encabezados
    headers = [
        'ID_Proveedor',
        'Nombre_Legal',
        'Nombre',
        'Pais',
        'Moneda',
        'Identificacion_Tributaria',
        'Estado_Provincia',
        'Ciudad',
        'Direccion',
        'Codigo_Postal',
        'Telefono',
        'Email',
        'Contacto_Nombre',
        'Contacto_Rol',
        'Categoria',
        'Terminos_Pago',
        'Metodo_Pago',
        'Cuenta_Bancaria',
        'Estado',
        'Creado_Por',
        'Fecha_Creacion',
        'Fecha_Actualizacion'
    ]
    writer.writerow(headers)
    
    # Datos
    for supplier in suppliers:
        writer.writerow([
            supplier.id_suplier,
            supplier.legal_name,
            supplier.name,
            supplier.country,
            supplier.currency,
            supplier.text_id or '',
            supplier.state_province or '',
            supplier.city or '',
            supplier.address or '',
            supplier.zip_code or '',
            supplier.phone or '',
            supplier.email or '',
            supplier.contact_name or '',
            supplier.contact_role or '',
            supplier.category or '',
            supplier.payments_terms or '',
            supplier.payment_method or '',
            supplier.bank_account or '',
            'Activo' if supplier.status else 'Inactivo',
            supplier.created_by,
            supplier.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            supplier.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    # Crear nombre de archivo con fecha
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'proveedores_exportacion_{timestamp}.csv'
    
    csv_data = output.getvalue().encode('utf-8-sig')
    
    return send_file(
        io.BytesIO(csv_data),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/suppliers/bulk_upload')
@login_required
@permission_required('suppliers', 2)
def bulk_upload():
    return render_template('suppliers/bulk_upload.html')

@bp.route('/suppliers/download_template')
@login_required
@permission_required('suppliers', 2)
def download_template():
    # Crear CSV template en memoria optimizado para Excel
    output = io.StringIO()
    
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    # Encabezados con ejemplos - USAR SÍMBOLOS
    writer.writerow([
        'ID_Proveedor', 'Nombre_Legal', 'Nombre', 'Pais', 'Moneda', 
        'Identificacion_Tributaria', 'Estado_Provincia', 'Ciudad', 'Direccion',
        'Codigo_Postal', 'Telefono', 'Email', 'Contacto_Nombre', 'Contacto_Rol',
        'Categoria', 'Terminos_Pago', 'Metodo_Pago', 'Cuenta_Bancaria', 'Estado'
    ])
    writer.writerow([
        'PROV-001', 'Tecnologia Global S.A.', 'TecnoGlobal', 'Mexico', 'MXN',  # Cambiado a MXN
        'TGM001234567', 'Jalisco', 'Guadalajara', 'Av. Tecnologico 123',
        '44100', '+52 33 1234 5678', 'contacto@tecnoglobal.com', 'Juan Perez', 'Gerente',
        'Tecnologia', '30 dias', 'Transferencia', '1234567890', '1'
    ])
    writer.writerow([
        'PROV-002', 'Materiales Construccion S.A.', 'MaterialCon', 'Mexico', 'MXN',  # Cambiado a MXN
        'MCS7654321', 'Nuevo Leon', 'Monterrey', 'Blvd. Industrial 456',
        '64000', '+52 81 9876 5432', 'ventas@materialcon.com', 'Maria Lopez', 'Ventas',
        'Construccion', '15 dias', 'Cheque', '0987654321', '1'
    ])
    writer.writerow([
        'PROV-003', 'Importadora Chile S.A.', 'ImportChile', 'Chile', 'CLP',  # Ejemplo con CLP
        'ICH123456789', 'Santiago', 'Santiago', 'Av. Principal 789',
        '8320000', '+56 2 2345 6789', 'contacto@importchile.cl', 'Carlos Ruiz', 'Director',
        'Importaciones', '60 dias', 'Transferencia', '1122334455', '1'
    ])
    writer.writerow([
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
    ])
    writer.writerow(['NOTAS:', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['- ID_Proveedor: Debe ser unico', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['- Estado: 1=Activo, 0=Inactivo', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['- Pais: Usar paises existentes en el sistema', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['- Moneda: Usar simbolos de moneda existentes (MXN, USD, EUR, CLP, etc.)', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name='plantilla_carga_proveedores.csv'
    )

@bp.route('/suppliers/process_bulk_upload', methods=['POST'])
@login_required
@permission_required('suppliers', 2)
def process_bulk_upload():
    if 'csv_file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('suppliers.bulk_upload'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('suppliers.bulk_upload'))
    
    if not file.filename.endswith('.csv'):
        flash('El archivo debe ser un CSV', 'error')
        return redirect(url_for('suppliers.bulk_upload'))
    
    try:
        # Leer el archivo CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.reader(stream)
        
        # Saltar el encabezado
        header = next(csv_reader, None)
        
        suppliers_created = 0
        suppliers_updated = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            if len(row) < 19:
                errors.append(f"Fila {row_num}: No tiene suficientes columnas")
                continue
            
            try:
                # Mapear campos del CSV
                (id_suplier, legal_name, name, country, currency, 
                 text_id, state_province, city, address, zip_code, 
                 phone, email, contact_name, contact_role, category, 
                 payments_terms, payment_method, bank_account, status_str) = row[:19]
                
                # Validar campos obligatorios
                if not id_suplier or not legal_name or not name or not country or not currency:
                    errors.append(f"Fila {row_num}: Campos obligatorios faltantes")
                    continue
                
                # Validar que el país exista (por nombre)
                if not Country.query.filter_by(name=country).first():
                    errors.append(f"Fila {row_num}: País '{country}' no existe")
                    continue
                
                # **CORRECCIÓN: Buscar moneda por símbolo en lugar de nombre**
                currency_obj = Currency.query.filter_by(symbol=currency).first()
                if not currency_obj:
                    errors.append(f"Fila {row_num}: Moneda '{currency}' no existe. Use símbolos como MXN, USD, EUR")
                    continue
                
                # Validar estado
                status = status_str.strip() == '1' if status_str else True
                
                # Verificar si el proveedor ya existe
                existing_supplier = Supplier.query.filter_by(id_suplier=id_suplier).first()
                
                if existing_supplier:
                    # Actualizar proveedor existente
                    existing_supplier.legal_name = legal_name
                    existing_supplier.name = name
                    existing_supplier.country = country
                    existing_supplier.currency = currency_obj.name  # Guardar nombre de la moneda
                    existing_supplier.text_id = text_id
                    existing_supplier.state_province = state_province
                    existing_supplier.city = city
                    existing_supplier.address = address
                    existing_supplier.zip_code = zip_code
                    existing_supplier.phone = phone
                    existing_supplier.email = email
                    existing_supplier.contact_name = contact_name
                    existing_supplier.contact_role = contact_role
                    existing_supplier.category = category
                    existing_supplier.payments_terms = payments_terms
                    existing_supplier.payment_method = payment_method
                    existing_supplier.bank_account = bank_account
                    existing_supplier.status = status
                    existing_supplier.updated_at = datetime.utcnow()
                    suppliers_updated += 1
                else:
                    # Crear nuevo proveedor
                    supplier = Supplier(
                        id_suplier=id_suplier,
                        legal_name=legal_name,
                        name=name,
                        country=country,
                        currency=currency_obj.name,  # Guardar nombre de la moneda
                        text_id=text_id,
                        state_province=state_province,
                        city=city,
                        address=address,
                        zip_code=zip_code,
                        phone=phone,
                        email=email,
                        contact_name=contact_name,
                        contact_role=contact_role,
                        category=category,
                        payments_terms=payments_terms,
                        payment_method=payment_method,
                        bank_account=bank_account,
                        status=status,
                        created_by=current_user.username
                    )
                    db.session.add(supplier)
                    suppliers_created += 1
                    
            except Exception as e:
                errors.append(f"Fila {row_num}: Error procesando - {str(e)}")
                continue
        
        # Confirmar cambios en la base de datos
        db.session.commit()
        
        # Mostrar resultados
        if suppliers_created > 0 or suppliers_updated > 0:
            flash(f'Carga masiva completada: {suppliers_created} proveedores creados, {suppliers_updated} actualizados', 'success')
        
        if errors:
            error_msg = f'Se encontraron {len(errors)} errores durante la carga:'
            for error in errors[:10]:
                error_msg += f'<br>- {error}'
            if len(errors) > 10:
                error_msg += f'<br>... y {len(errors) - 10} errores más'
            flash(error_msg, 'warning')
        
        if not suppliers_created and not suppliers_updated and not errors:
            flash('No se procesó ningún proveedor. Verifique el formato del archivo.', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error procesando el archivo: {str(e)}', 'error')
    
    return redirect(url_for('suppliers.supplier_list'))