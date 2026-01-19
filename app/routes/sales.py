from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import (
    SaleOrder, SaleOrderLine, Customer, Material, 
    Location, InventoryStock, InventoryMovement, 
    JournalEntry, JournalItem, AccountAccount
)
from app.utils.auth import permission_required
from datetime import datetime

bp = Blueprint('sales', __name__)

@bp.route('/sales')
@login_required
@permission_required('sales', 1)
def sale_list():
    orders = SaleOrder.query.order_by(SaleOrder.issue_date.desc()).all()
    return render_template('sales/list.html', orders=orders)

@bp.route('/sales/create', methods=['GET', 'POST'])
@login_required
@permission_required('sales', 2)
def sale_create():
    if request.method == 'POST':
        try:
            # 1. Recuperar ID de la bodega
            loc_id_raw = request.form.get('id_location')
            
            # Validación manual para depurar
            if not loc_id_raw or loc_id_raw == "":
                flash("❌ ERROR: La bodega seleccionada envió un valor vacío.", "error")
                return redirect(url_for('sales.sale_create'))
            
            loc_id = int(loc_id_raw) # Convertir a entero
            mat_code = request.form.get('id_material')
            qty = int(request.form.get('quantity', 0))
            price = float(request.form.get('price', 0))
            
            
            
            # Convertimos a entero para coincidir con el modelo de base de datos
            loc_id = int(loc_id)
            # --------------------------
            
            # 2. Buscar Material para obtener su unidad de medida
            material_obj = Material.query.filter_by(id_material=mat_code).first()
            if not material_obj:
                flash(f"Error: El material {mat_code} no existe.", "error")
                return redirect(url_for('sales.sale_create'))

            # 3. Buscar Stock usando el ID numérico de la bodega
            stock = InventoryStock.query.filter_by(
                id_material=mat_code, 
                id_location=loc_id
            ).first()

            if not stock:
                flash(f"❌ ERROR: No hay registro de stock para '{mat_code}' en la bodega seleccionada.", "error")
                return redirect(url_for('sales.sale_create'))

            if stock.quantity < qty:
                flash(f"❌ Stock insuficiente. Disponible: {stock.quantity}", "error")
                return redirect(url_for('sales.sale_create'))

            # 4. Registrar Venta e Inventario
            sale_id = f"VTA-{datetime.now().strftime('%y%m%d%H%M')}"
            
            # Cabecera de la Orden de Venta
            new_sale = SaleOrder(
                id_sale_order=sale_id,
                id_customer=request.form['id_customer'],
                total_amount=qty * price,
                currency='MXN',
                status='aprobado',
                created_by=current_user.username
            )
            db.session.add(new_sale)

            # Detalle de la línea de venta
            db.session.add(SaleOrderLine(
                id_sale_order=sale_id, 
                id_material=mat_code,
                quantity=qty, 
                unit_price=price, 
                subtotal=qty*price
            ))

            # Actualizar Stock (Descontar cantidad)
            stock.quantity -= qty
            
            # Registrar Movimiento de Inventario con el ID de bodega correcto
            db.session.add(InventoryMovement(
                id_location=loc_id, 
                id_material=mat_code,
                quantity=qty, 
                unit_type=str(material_obj.unit),
                movement_type='SALIDA', 
                notes=f"Venta {sale_id}",
                created_by=current_user.username
            ))

            # --- 5. REGISTRO CONTABLE (ASIENTO) ---
            # Calculamos el monto total de la venta
            total_sale = float(qty * price)

            # Crear cabecera del asiento
            # Asegúrate de que los nombres coincidan exactamente con tu models.py
            entry = JournalEntry(
                description=f"Venta {sale_id} - Cliente: {request.form.get('id_customer')}",
                reference=sale_id,
                created_by=current_user.username
                # Si tu modelo pide 'date', agrégalo aquí: date=datetime.utcnow()
            )
            db.session.add(entry)
            db.session.flush()  # <--- CRÍTICO: Genera el ID para que JournalItem pueda usarlo

            # Recuperar IDs de cuentas del formulario
            acc_debit_id = request.form.get('acc_debit')
            acc_credit_id = request.form.get('acc_credit')

            # Validación de seguridad: Si no hay cuentas, lanzamos error antes del commit
            if not acc_debit_id or not acc_credit_id:
                raise ValueError("Las cuentas contables (débito/crédito) no fueron seleccionadas correctamente.")

            # Línea de Débito (Entrada de dinero / CxC)
            item_debit = JournalItem(
                entry_id=entry.id,
                account_id=int(acc_debit_id),
                debit=total_sale,
                credit=0.0
            )
            db.session.add(item_debit)

            # Línea de Crédito (Venta / Ingreso)
            item_credit = JournalItem(
                entry_id=entry.id,
                account_id=int(acc_credit_id),
                debit=0.0,
                credit=total_sale
            )
            db.session.add(item_credit)

            # 6. Finalizar transacción
            db.session.commit()
            flash(f"✅ Venta {sale_id} exitosa", "success")
            return redirect(url_for('sales.sale_list'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error inesperado: {str(e)}", "error")
            return redirect(url_for('sales.sale_create'))

    # Carga de datos para los menús desplegables (GET)
    return render_template('sales/create.html', 
                           customers=Customer.query.filter_by(status=True).all(), 
                           materials=Material.query.all(),
                           locations=Location.query.all(), 
                           accounts=AccountAccount.query.all())