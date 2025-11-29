from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Customer, Country, Currency
from app.utils.auth import permission_required
import csv
import io
from datetime import datetime

bp = Blueprint('customers', __name__)

@bp.route('/customers')
@login_required
@permission_required('customers', 1)
def customer_list():
    # Obtener parámetros de filtro
    id_customer_filter = request.args.get('id_customer', '')
    name_filter = request.args.get('name', '')
    country_filter = request.args.get('country', '')
    status_filter = request.args.get('status', '')
    
    # Construir consulta base
    query = Customer.query
    
    # Aplicar filtros
    if id_customer_filter:
        query = query.filter(Customer.id_customer.contains(id_customer_filter))
    if name_filter:
        query = query.filter(Customer.name.contains(name_filter))
    if country_filter:
        query = query.filter(Customer.country == country_filter)
    if status_filter:
        status_bool = status_filter == 'true'
        query = query.filter(Customer.status == status_bool)
    
    customers = query.order_by(Customer.created_at.desc()).all()
    countries = Country.query.all()
    
    return render_template('customers/list.html', 
                         customers=customers, 
                         countries=countries,
                         filters=request.args)

@bp.route('/customers/create', methods=['GET', 'POST'])
@login_required
@permission_required('customers', 2)
def customer_create():
    if request.method == 'POST':
        try:
            customer = Customer(
                id_customer=request.form['id_customer'],
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
            
            db.session.add(customer)
            db.session.commit()
            flash('Cliente creado exitosamente', 'success')
            return redirect(url_for('customers.customer_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear cliente: {str(e)}', 'error')
    
    countries = Country.query.all()
    currencies = Currency.query.all()
    return render_template('customers/create.html', 
                         countries=countries, 
                         currencies=currencies)

@bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('customers', 2)
def customer_edit(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        try:
            customer.id_customer = request.form['id_customer']
            customer.legal_name = request.form['legal_name']
            customer.name = request.form['name']
            customer.country = request.form['country']
            customer.currency = request.form['currency']
            customer.text_id = request.form.get('text_id', '')
            customer.state_province = request.form.get('state_province', '')
            customer.city = request.form.get('city', '')
            customer.address = request.form.get('address', '')
            customer.zip_code = request.form.get('zip_code', '')
            customer.phone = request.form.get('phone', '')
            customer.email = request.form.get('email', '')
            customer.contact_name = request.form.get('contact_name', '')
            customer.contact_role = request.form.get('contact_role', '')
            customer.category = request.form.get('category', '')
            customer.payments_terms = request.form.get('payments_terms', '')
            customer.payment_method = request.form.get('payment_method', '')
            customer.bank_account = request.form.get('bank_account', '')
            customer.status = request.form.get('status') == 'on'
            customer.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Cliente actualizado exitosamente', 'success')
            return redirect(url_for('customers.customer_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar cliente: {str(e)}', 'error')
    
    countries = Country.query.all()
    currencies = Currency.query.all()
    return render_template('customers/edit.html', 
                         customer=customer, 
                         countries=countries, 
                         currencies=currencies)

@bp.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
@permission_required('customers', 2)
def customer_delete(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Cliente eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar cliente: {str(e)}', 'error')
    
    return redirect(url_for('customers.customer_list'))

@bp.route('/customers/export_csv')
@login_required
@permission_required('customers', 1)
def export_csv():
    # Obtener los mismos filtros de la lista
    id_customer_filter = request.args.get('id_customer', '')
    name_filter = request.args.get('name', '')
    country_filter = request.args.get('country', '')
    status_filter = request.args.get('status', '')
    
    # Construir consulta base
    query = Customer.query
    
    if id_customer_filter:
        query = query.filter(Customer.id_customer.contains(id_customer_filter))
    if name_filter:
        query = query.filter(Customer.name.contains(name_filter))
    if country_filter:
        query = query.filter(Customer.country == country_filter)
    if status_filter:
        status_bool = status_filter == 'true'
        query = query.filter(Customer.status == status_bool)
    
    customers = query.order_by(Customer.created_at.desc()).all()
    
    # Crear CSV en memoria con encoding para Excel
    output = io.StringIO()
    
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    # Encabezados
    headers = [
        'ID_Cliente',
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
    for customer in customers:
        writer.writerow([
            customer.id_customer,
            customer.legal_name,
            customer.name,
            customer.country,
            customer.currency,
            customer.text_id or '',
            customer.state_province or '',
            customer.city or '',
            customer.address or '',
            customer.zip_code or '',
            customer.phone or '',
            customer.email or '',
            customer.contact_name or '',
            customer.contact_role or '',
            customer.category or '',
            customer.payments_terms or '',
            customer.payment_method or '',
            customer.bank_account or '',
            'Activo' if customer.status else 'Inactivo',
            customer.created_by,
            customer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            customer.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    # Crear nombre de archivo con fecha
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'clientes_exportacion_{timestamp}.csv'
    
    csv_data = output.getvalue().encode('utf-8-sig')
    
    return send_file(
        io.BytesIO(csv_data),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/customers/bulk_upload')
@login_required
@permission_required('customers', 2)
def bulk_upload():
    return render_template('customers/bulk_upload.html')

@bp.route('/customers/download_template')
@login_required
@permission_required('customers', 2)
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
        'ID_Cliente', 'Nombre_Legal', 'Nombre', 'Pais', 'Moneda', 
        'Identificacion_Tributaria', 'Estado_Provincia', 'Ciudad', 'Direccion',
        'Codigo_Postal', 'Telefono', 'Email', 'Contacto_Nombre', 'Contacto_Rol',
        'Categoria', 'Terminos_Pago', 'Metodo_Pago', 'Cuenta_Bancaria', 'Estado'
    ])
    writer.writerow([
        'CLI-001', 'Empresa ABC S.A.', 'ABC Corp', 'Mexico', 'MXN',
        'ABC001234567', 'Jalisco', 'Guadalajara', 'Av. Principal 123',
        '44100', '+52 33 1234 5678', 'contacto@abccorp.com', 'Ana Garcia', 'Gerente',
        'Retail', '30 dias', 'Transferencia', '1234567890', '1'
    ])
    writer.writerow([
        'CLI-002', 'Comercializadora XYZ S.A.', 'XYZ Comercial', 'Mexico', 'MXN',
        'XYZ7654321', 'Nuevo Leon', 'Monterrey', 'Blvd. Comercial 456',
        '64000', '+52 81 9876 5432', 'ventas@xyz.com', 'Pedro Martinez', 'Compras',
        'Distribucion', '15 dias', 'Cheque', '0987654321', '1'
    ])
    writer.writerow([
        'CLI-003', 'Importadora Chile S.A.', 'ImportChile', 'Chile', 'CLP',
        'ICH123456789', 'Santiago', 'Santiago', 'Av. Principal 789',
        '8320000', '+56 2 2345 6789', 'contacto@importchile.cl', 'Carlos Ruiz', 'Director',
        'Importaciones', '60 dias', 'Transferencia', '1122334455', '1'
    ])
    writer.writerow([
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
    ])
    writer.writerow(['NOTAS:', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['- ID_Cliente: Debe ser unico', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['- Estado: 1=Activo, 0=Inactivo', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['- Pais: Usar paises existentes en el sistema', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    writer.writerow(['- Moneda: Usar simbolos de moneda existentes (MXN, USD, EUR, CLP, etc.)', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name='plantilla_carga_clientes.csv'
    )

@bp.route('/customers/process_bulk_upload', methods=['POST'])
@login_required
@permission_required('customers', 2)
def process_bulk_upload():
    if 'csv_file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('customers.bulk_upload'))
    
    file = request.files['csv_file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(url_for('customers.bulk_upload'))
    
    if not file.filename.endswith('.csv'):
        flash('El archivo debe ser un CSV', 'error')
        return redirect(url_for('customers.bulk_upload'))
    
    try:
        # Leer el archivo CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.reader(stream)
        
        # Saltar el encabezado
        header = next(csv_reader, None)
        
        customers_created = 0
        customers_updated = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            if len(row) < 19:
                errors.append(f"Fila {row_num}: No tiene suficientes columnas")
                continue
            
            try:
                # Mapear campos del CSV
                (id_customer, legal_name, name, country, currency, 
                 text_id, state_province, city, address, zip_code, 
                 phone, email, contact_name, contact_role, category, 
                 payments_terms, payment_method, bank_account, status_str) = row[:19]
                
                # Validar campos obligatorios
                if not id_customer or not legal_name or not name or not country or not currency:
                    errors.append(f"Fila {row_num}: Campos obligatorios faltantes")
                    continue
                
                # Validar que el país exista (por nombre)
                if not Country.query.filter_by(name=country).first():
                    errors.append(f"Fila {row_num}: País '{country}' no existe")
                    continue
                
                # Buscar moneda por símbolo
                currency_obj = Currency.query.filter_by(symbol=currency).first()
                if not currency_obj:
                    errors.append(f"Fila {row_num}: Moneda '{currency}' no existe. Use símbolos como MXN, USD, EUR")
                    continue
                
                # Validar estado
                status = status_str.strip() == '1' if status_str else True
                
                # Verificar si el cliente ya existe
                existing_customer = Customer.query.filter_by(id_customer=id_customer).first()
                
                if existing_customer:
                    # Actualizar cliente existente
                    existing_customer.legal_name = legal_name
                    existing_customer.name = name
                    existing_customer.country = country
                    existing_customer.currency = currency_obj.name  # Guardar nombre de la moneda
                    existing_customer.text_id = text_id
                    existing_customer.state_province = state_province
                    existing_customer.city = city
                    existing_customer.address = address
                    existing_customer.zip_code = zip_code
                    existing_customer.phone = phone
                    existing_customer.email = email
                    existing_customer.contact_name = contact_name
                    existing_customer.contact_role = contact_role
                    existing_customer.category = category
                    existing_customer.payments_terms = payments_terms
                    existing_customer.payment_method = payment_method
                    existing_customer.bank_account = bank_account
                    existing_customer.status = status
                    existing_customer.updated_at = datetime.utcnow()
                    customers_updated += 1
                else:
                    # Crear nuevo cliente
                    customer = Customer(
                        id_customer=id_customer,
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
                    db.session.add(customer)
                    customers_created += 1
                    
            except Exception as e:
                errors.append(f"Fila {row_num}: Error procesando - {str(e)}")
                continue
        
        # Confirmar cambios en la base de datos
        db.session.commit()
        
        # Mostrar resultados
        if customers_created > 0 or customers_updated > 0:
            flash(f'Carga masiva completada: {customers_created} clientes creados, {customers_updated} actualizados', 'success')
        
        if errors:
            error_msg = f'Se encontraron {len(errors)} errores durante la carga:'
            for error in errors[:10]:
                error_msg += f'<br>- {error}'
            if len(errors) > 10:
                error_msg += f'<br>... y {len(errors) - 10} errores más'
            flash(error_msg, 'warning')
        
        if not customers_created and not customers_updated and not errors:
            flash('No se procesó ningún cliente. Verifique el formato del archivo.', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error procesando el archivo: {str(e)}', 'error')
    
    return redirect(url_for('customers.customer_list'))