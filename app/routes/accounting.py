# app/routes/accounting.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models import AccountType, AccountGroup, AccountNature, AccountAccount, Currency, Country, JournalEntry, JournalItem
from app.utils.auth import permission_required
import csv
import io
from datetime import datetime

bp = Blueprint('accounting', __name__)

# ================================
# Rutas para Tipos de Cuenta
# ================================

@bp.route('/accounting/types')
@login_required
@permission_required('accounting', 1)
def account_type_list():
    types = AccountType.query.order_by(AccountType.name).all()
    return render_template('accounting/types/list.html', types=types)

@bp.route('/accounting/types/create', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def account_type_create():
    if request.method == 'POST':
        try:
            account_type = AccountType(
                id_account_type=request.form['id_account_type'],
                name=request.form['name'],
                description=request.form.get('description', ''),
                created_by=current_user.username
            )
            db.session.add(account_type)
            db.session.commit()
            flash('Tipo de cuenta creado exitosamente', 'success')
            return redirect(url_for('accounting.account_type_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear tipo de cuenta: {str(e)}', 'error')
    
    return render_template('accounting/types/create.html')

@bp.route('/accounting/types/<string:type_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def account_type_edit(type_id):
    account_type = AccountType.query.filter_by(id_account_type=type_id).first_or_404()
    
    if request.method == 'POST':
        try:
            account_type.name = request.form['name']
            account_type.description = request.form.get('description', '')
            db.session.commit()
            flash('Tipo de cuenta actualizado exitosamente', 'success')
            return redirect(url_for('accounting.account_type_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar tipo de cuenta: {str(e)}', 'error')
    
    return render_template('accounting/types/edit.html', account_type=account_type)

@bp.route('/accounting/types/<string:type_id>/delete', methods=['POST'])
@login_required
@permission_required('accounting', 2)
def account_type_delete(type_id):
    account_type = AccountType.query.filter_by(id_account_type=type_id).first_or_404()
    
    try:
        # Verificar si hay cuentas usando este tipo
        accounts = AccountAccount.query.filter_by(account_type=type_id).first()
        if accounts:
            flash('No se puede eliminar el tipo de cuenta porque está siendo usado en una o más cuentas.', 'error')
        else:
            db.session.delete(account_type)
            db.session.commit()
            flash('Tipo de cuenta eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar tipo de cuenta: {str(e)}', 'error')
    
    return redirect(url_for('accounting.account_type_list'))

# ================================
# Rutas para Grupos de Cuenta
# ================================

@bp.route('/accounting/groups')
@login_required
@permission_required('accounting', 1)
def account_group_list():
    groups = AccountGroup.query.order_by(AccountGroup.name).all()
    return render_template('accounting/groups/list.html', groups=groups)

@bp.route('/accounting/groups/create', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def account_group_create():
    if request.method == 'POST':
        try:
            account_group = AccountGroup(
                id_account_group=request.form['id_account_group'],
                name=request.form['name'],
                code_prefix=request.form.get('code_prefix', ''),
                description=request.form.get('description', ''),
                created_by=current_user.username
            )
            db.session.add(account_group)
            db.session.commit()
            flash('Grupo de cuenta creado exitosamente', 'success')
            return redirect(url_for('accounting.account_group_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear grupo de cuenta: {str(e)}', 'error')
    
    return render_template('accounting/groups/create.html')

@bp.route('/accounting/groups/<string:group_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def account_group_edit(group_id):
    account_group = AccountGroup.query.filter_by(id_account_group=group_id).first_or_404()
    
    if request.method == 'POST':
        try:
            account_group.name = request.form['name']
            account_group.code_prefix = request.form.get('code_prefix', '')
            account_group.description = request.form.get('description', '')
            db.session.commit()
            flash('Grupo de cuenta actualizado exitosamente', 'success')
            return redirect(url_for('accounting.account_group_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar grupo de cuenta: {str(e)}', 'error')
    
    return render_template('accounting/groups/edit.html', account_group=account_group)

@bp.route('/accounting/groups/<string:group_id>/delete', methods=['POST'])
@login_required
@permission_required('accounting', 2)
def account_group_delete(group_id):
    account_group = AccountGroup.query.filter_by(id_account_group=group_id).first_or_404()
    
    try:
        # Verificar si hay cuentas usando este grupo
        accounts = AccountAccount.query.filter_by(account_group=group_id).first()
        if accounts:
            flash('No se puede eliminar el grupo de cuenta porque está siendo usado en una o más cuentas.', 'error')
        else:
            db.session.delete(account_group)
            db.session.commit()
            flash('Grupo de cuenta eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar grupo de cuenta: {str(e)}', 'error')
    
    return redirect(url_for('accounting.account_group_list'))

# ================================
# Rutas para Naturalezas de Cuenta
# ================================

@bp.route('/accounting/natures')
@login_required
@permission_required('accounting', 1)
def account_nature_list():
    natures = AccountNature.query.order_by(AccountNature.name).all()
    return render_template('accounting/natures/list.html', natures=natures)

@bp.route('/accounting/natures/create', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def account_nature_create():
    if request.method == 'POST':
        try:
            account_nature = AccountNature(
                id_account_nature=request.form['id_account_nature'],
                name=request.form['name'],
                symbol=request.form.get('symbol', ''),
                effect_on_balance=request.form.get('effect_on_balance', ''),
                created_by=current_user.username
            )
            db.session.add(account_nature)
            db.session.commit()
            flash('Naturaleza de cuenta creada exitosamente', 'success')
            return redirect(url_for('accounting.account_nature_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear naturaleza de cuenta: {str(e)}', 'error')
    
    return render_template('accounting/natures/create.html')

@bp.route('/accounting/natures/<string:nature_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def account_nature_edit(nature_id):
    account_nature = AccountNature.query.filter_by(id_account_nature=nature_id).first_or_404()
    
    if request.method == 'POST':
        try:
            account_nature.name = request.form['name']
            account_nature.symbol = request.form.get('symbol', '')
            account_nature.effect_on_balance = request.form.get('effect_on_balance', '')
            db.session.commit()
            flash('Naturaleza de cuenta actualizada exitosamente', 'success')
            return redirect(url_for('accounting.account_nature_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar naturaleza de cuenta: {str(e)}', 'error')
    
    return render_template('accounting/natures/edit.html', account_nature=account_nature)

@bp.route('/accounting/natures/<string:nature_id>/delete', methods=['POST'])
@login_required
@permission_required('accounting', 2)
def account_nature_delete(nature_id):
    account_nature = AccountNature.query.filter_by(id_account_nature=nature_id).first_or_404()
    
    try:
        # Verificar si hay cuentas usando esta naturaleza
        accounts = AccountAccount.query.filter_by(nature=nature_id).first()
        if accounts:
            flash('No se puede eliminar la naturaleza de cuenta porque está siendo usada en una o más cuentas.', 'error')
        else:
            db.session.delete(account_nature)
            db.session.commit()
            flash('Naturaleza de cuenta eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar naturaleza de cuenta: {str(e)}', 'error')
    
    return redirect(url_for('accounting.account_nature_list'))

# ================================
# Rutas para Cuentas Contables
# ================================

@bp.route('/accounting/accounts')
@login_required
@permission_required('accounting', 1)
def account_list():
    # Obtener parámetros de filtro
    code_filter = request.args.get('code', '')
    name_filter = request.args.get('name', '')
    status_filter = request.args.get('status', '')
    
    query = AccountAccount.query
    
    if code_filter:
        query = query.filter(AccountAccount.code.contains(code_filter))
    if name_filter:
        query = query.filter(AccountAccount.name.contains(name_filter))
    if status_filter:
        if status_filter == 'Activo':
            query = query.filter(AccountAccount.status == True)
        elif status_filter == 'Inactivo':
            query = query.filter(AccountAccount.status == False)
    
    accounts = query.order_by(AccountAccount.code).all()
    
    # Obtener datos para mostrar nombres en lugar de IDs
    account_types = AccountType.query.all()
    account_groups = AccountGroup.query.all()
    account_natures = AccountNature.query.all()
    currencies = Currency.query.all()
    countries = Country.query.all()
    
    # Crear diccionarios para mapear IDs a nombres
    type_dict = {t.id_account_type: t.name for t in account_types}
    group_dict = {g.id_account_group: g.name for g in account_groups}
    nature_dict = {n.id_account_nature: n.name for n in account_natures}
    currency_dict = {c.symbol: f"{c.name} ({c.symbol})" for c in currencies}
    country_dict = {c.symbol: c.name for c in countries}
    
    return render_template('accounting/accounts/list.html', 
                         accounts=accounts,
                         type_dict=type_dict,
                         group_dict=group_dict,
                         nature_dict=nature_dict,
                         currency_dict=currency_dict,
                         country_dict=country_dict,
                         filters=request.args)

@bp.route('/accounting/accounts/create', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def account_create():
    if request.method == 'POST':
        try:
            account = AccountAccount(
                id_account=request.form['id_account'],
                name=request.form['name'],
                code=request.form['code'],
                description=request.form.get('description', ''),
                account_type=request.form['account_type'],
                account_group=request.form['account_group'],
                nature=request.form['nature'],
                currency_id=request.form['currency_id'],
                country_id=request.form['country_id'],
                parent_account=request.form.get('parent_account', ''),
                status=bool(request.form.get('status', False)),
                created_by=current_user.username
            )
            db.session.add(account)
            db.session.commit()
            flash('Cuenta contable creada exitosamente', 'success')
            return redirect(url_for('accounting.account_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear cuenta contable: {str(e)}', 'error')
    
    # Obtener datos para los selects
    account_types = AccountType.query.all()
    account_groups = AccountGroup.query.all()
    account_natures = AccountNature.query.all()
    currencies = Currency.query.all()
    countries = Country.query.all()
    parent_accounts = AccountAccount.query.filter_by(status=True).all()
    
    return render_template('accounting/accounts/create.html',
                         account_types=account_types,
                         account_groups=account_groups,
                         account_natures=account_natures,
                         currencies=currencies,
                         countries=countries,
                         parent_accounts=parent_accounts)

@bp.route('/accounting/accounts/<string:account_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def account_edit(account_id):
    account = AccountAccount.query.filter_by(id_account=account_id).first_or_404()
    
    if request.method == 'POST':
        try:
            account.name = request.form['name']
            account.code = request.form['code']
            account.description = request.form.get('description', '')
            account.account_type = request.form['account_type']
            account.account_group = request.form['account_group']
            account.nature = request.form['nature']
            account.currency_id = request.form['currency_id']
            account.country_id = request.form['country_id']
            account.parent_account = request.form.get('parent_account', '')
            account.status = bool(request.form.get('status', False))
            
            db.session.commit()
            flash('Cuenta contable actualizada exitosamente', 'success')
            return redirect(url_for('accounting.account_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar cuenta contable: {str(e)}', 'error')
    
    # Obtener datos para los selects
    account_types = AccountType.query.all()
    account_groups = AccountGroup.query.all()
    account_natures = AccountNature.query.all()
    currencies = Currency.query.all()
    countries = Country.query.all()
    parent_accounts = AccountAccount.query.filter(AccountAccount.id_account != account_id).filter_by(status=True).all()
    
    return render_template('accounting/accounts/edit.html',
                         account=account,
                         account_types=account_types,
                         account_groups=account_groups,
                         account_natures=account_natures,
                         currencies=currencies,
                         countries=countries,
                         parent_accounts=parent_accounts)

@bp.route('/accounting/accounts/<string:account_id>/delete', methods=['POST'])
@login_required
@permission_required('accounting', 2)
def account_delete(account_id):
    account = AccountAccount.query.filter_by(id_account=account_id).first_or_404()
    
    try:
        # Verificar si hay cuentas hijas
        child_accounts = AccountAccount.query.filter_by(parent_account=account_id).first()
        if child_accounts:
            flash('No se puede eliminar la cuenta porque tiene cuentas hijas asignadas.', 'error')
        else:
            # En un sistema real, también deberíamos verificar si hay transacciones asociadas
            db.session.delete(account)
            db.session.commit()
            flash('Cuenta contable eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar cuenta contable: {str(e)}', 'error')
    
    return redirect(url_for('accounting.account_list'))

@bp.route('/accounting/accounts/export_csv')
@login_required
@permission_required('accounting', 1)
def export_accounts_csv():
    accounts = AccountAccount.query.order_by(AccountAccount.code).all()
    
    output = io.StringIO()
    writer = csv.writer(output, 
                       delimiter=',',
                       quotechar='"', 
                       quoting=csv.QUOTE_ALL,
                       lineterminator='\n')
    
    headers = [
        'ID_Cuenta', 'Nombre', 'Código', 'Descripción', 'Tipo', 'Grupo',
        'Naturaleza', 'Moneda', 'País', 'Cuenta_Padre', 'Estado',
        'Fecha_Creación', 'Última_Actualización', 'Creado_Por'
    ]
    writer.writerow(headers)
    
    for account in accounts:
        writer.writerow([
            account.id_account,
            account.name,
            account.code,
            account.description or '',
            account.account_type,
            account.account_group,
            account.nature,
            account.currency_id,
            account.country_id,
            account.parent_account or '',
            'Activo' if account.status else 'Inactivo',
            account.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            account.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            account.created_by
        ])
    
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'cuentas_contables_{timestamp}.csv'
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv; charset=utf-8-sig',
        as_attachment=True,
        download_name=filename
    )

# API para obtener cuentas en formato JSON (útil para select2 o similar)
@bp.route('/api/accounting/accounts')
@login_required
def get_accounts_json():
    accounts = AccountAccount.query.filter_by(status=True).order_by(AccountAccount.code).all()
    account_list = [{'id': acc.id_account, 'text': f"{acc.code} - {acc.name}"} for acc in accounts]
    return jsonify(account_list)

@bp.route('/accounting/journal/create', methods=['GET', 'POST'])
@login_required
@permission_required('accounting', 2)
def journal_entry_create():
    accounts = AccountAccount.query.filter_by(status=True).order_by(AccountAccount.code).all()
    
    if request.method == 'POST':
        try:
            # 1. Obtener datos del formulario
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            description = request.form['description']
            
            # Listas de datos de las líneas (vienen del formulario dinámico)
            acc_ids = request.form.getlist('account_id[]')
            debits = request.form.getlist('debit[]')
            credits = request.form.getlist('credit[]')
            
            # 2. Validación de Partida Doble (Cuadre)
            total_debit = sum(float(d) for d in debits if d)
            total_credit = sum(float(c) for c in credits if c)
            
            if abs(total_debit - total_credit) > 0.001:
                flash('Error: El asiento no está cuadrado (Debe != Haber).', 'error')
                return redirect(url_for('accounting.journal_entry_create'))

            # 3. Guardar el asiento
            entry = JournalEntry(
                date=date,
                description=description,
                created_by=current_user.username
            )
            db.session.add(entry)
            db.session.flush() # Para obtener el ID de entry antes del commit

            for i in range(len(acc_ids)):
                val_debit = float(debits[i] or 0)
                val_credit = float(credits[i] or 0)
                
                if val_debit > 0 or val_credit > 0:
                    item = JournalItem(
                        entry_id=entry.id,
                        account_id=acc_ids[i],
                        debit=val_debit,
                        credit=val_credit
                    )
                    db.session.add(item)
            
            db.session.commit()
            flash('Asiento contable registrado exitosamente', 'success')
            return redirect(url_for('accounting.account_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar asiento: {str(e)}', 'error')

    return render_template('accounting/journal/create.html', accounts=accounts)