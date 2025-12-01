from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# ------------- seccion de base de datos para la tabla roles------------------------------------- 
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    # Permisos por módulo
    materials_permission = db.Column(db.Integer, default=0)
    inventory_permission = db.Column(db.Integer, default=0)
    customers_permission = db.Column(db.Integer, default=0)
    accounting_permission = db.Column(db.Integer, default=0)
    suppliers_permission = db.Column(db.Integer, default=0)
    reporting_permission = db.Column(db.Integer, default=0)
    purchases_permission = db.Column(db.Integer, default=0)
    sales_permission = db.Column(db.Integer, default=0)
    users_permission = db.Column(db.Integer, default=0)
    
    users = db.relationship('User', backref='role', lazy='dynamic')

# ---------------------- seccion de usuarios -------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_superuser = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, module, required_level=1):
        """Verifica si el usuario tiene permiso para un módulo"""
        if self.is_superuser:
            return True
        
        if not self.role:
            return False
            
        permission_level = getattr(self.role, f"{module}_permission", 0)
        return permission_level >= required_level

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# ----- seccion de materiales usa la libreria de datetime ------------------------------------------
class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    symbol = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaterialType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_material = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Convierte el material a diccionario para CSV"""
        return {
            'id_material': self.id_material,
            'name': self.name,
            'description': self.description or '',
            'unit': self.unit,
            'type': self.type,
            'status': 'Activo' if self.status else 'Inactivo',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }
    
# --------------------------- seccion de proveedores -----------------------------------------------
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    symbol = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Currency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    symbol = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_suplier = db.Column(db.String(50), unique=True, nullable=False)
    legal_name = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    text_id = db.Column(db.String(100))
    state_province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    address = db.Column(db.Text)
    zip_code = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    contact_name = db.Column(db.String(100))
    contact_role = db.Column(db.String(100))
    category = db.Column(db.String(100))
    payments_terms = db.Column(db.String(200))
    payment_method = db.Column(db.String(100))
    bank_account = db.Column(db.String(100))
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Convierte el proveedor a diccionario para CSV"""
        return {
            'id_suplier': self.id_suplier,
            'legal_name': self.legal_name,
            'name': self.name,
            'country': self.country,
            'currency': self.currency,
            'text_id': self.text_id or '',
            'state_province': self.state_province or '',
            'city': self.city or '',
            'address': self.address or '',
            'zip_code': self.zip_code or '',
            'phone': self.phone or '',
            'email': self.email or '',
            'contact_name': self.contact_name or '',
            'contact_role': self.contact_role or '',
            'category': self.category or '',
            'payments_terms': self.payments_terms or '',
            'payment_method': self.payment_method or '',
            'bank_account': self.bank_account or '',
            'status': 'Activo' if self.status else 'Inactivo',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }        
        
# ------------------------------- clientes modelo base de datos ------------------------------------------
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_customer = db.Column(db.String(50), unique=True, nullable=False)
    legal_name = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    text_id = db.Column(db.String(100))
    state_province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    address = db.Column(db.Text)
    zip_code = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    contact_name = db.Column(db.String(100))
    contact_role = db.Column(db.String(100))
    category = db.Column(db.String(100))
    payments_terms = db.Column(db.String(200))
    payment_method = db.Column(db.String(100))
    bank_account = db.Column(db.String(100))
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        """Convierte el cliente a diccionario para CSV"""
        return {
            'id_customer': self.id_customer,
            'legal_name': self.legal_name,
            'name': self.name,
            'country': self.country,
            'currency': self.currency,
            'text_id': self.text_id or '',
            'state_province': self.state_province or '',
            'city': self.city or '',
            'address': self.address or '',
            'zip_code': self.zip_code or '',
            'phone': self.phone or '',
            'email': self.email or '',
            'contact_name': self.contact_name or '',
            'contact_role': self.contact_role or '',
            'category': self.category or '',
            'payments_terms': self.payments_terms or '',
            'payment_method': self.payment_method or '',
            'bank_account': self.bank_account or '',
            'status': 'Activo' if self.status else 'Inactivo',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }
    
# ------------------------------- seccion de Compras ------------------------------------------------
# Agregar al final de models.py

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_purchase_order = db.Column(db.String(50), unique=True, nullable=False)
    id_supplier = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estimated_delivery_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pendiente')  # Pendiente, Aprobada, Enviada, Recibida, Cancelada
    total_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id_purchase_order': self.id_purchase_order,
            'id_supplier': self.id_supplier,
            'issue_date': self.issue_date.strftime('%Y-%m-%d'),
            'estimated_delivery_date': self.estimated_delivery_date.strftime('%Y-%m-%d'),
            'status': self.status,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }

class PurchaseOrderLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_purchase_order_line = db.Column(db.String(50), unique=True, nullable=False)
    id_purchase_order = db.Column(db.String(50), nullable=False)
    id_material = db.Column(db.String(50), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_material = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency_suppliers = db.Column(db.String(10), nullable=False)
    resolved_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id_purchase_order_line': self.id_purchase_order_line,
            'id_purchase_order': self.id_purchase_order,
            'id_material': self.id_material,
            'position': self.position,
            'quantity': self.quantity,
            'unit_material': self.unit_material,
            'price': self.price,
            'currency_suppliers': self.currency_suppliers,
            'resolved_quantity': self.resolved_quantity,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }
        
# ----------------------- modulo de inventario ----------------------------------------------

class Location(db.Model):
    __tablename__ = 'locations_inventory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    main_location = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(500))  # Dirección física
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'main_location': self.main_location,
            'location': self.location,
            'status': 'Activo' if self.status else 'Inactivo',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }

class InventoryMovement(db.Model):
    __tablename__ = 'inventory_movements'
    id = db.Column(db.Integer, primary_key=True)
    id_location = db.Column(db.Integer, db.ForeignKey('locations_inventory.id'), nullable=False)
    id_material = db.Column(db.String(50), db.ForeignKey('material.id_material'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_type = db.Column(db.String(20), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # ENTRADA, SALIDA, AJUSTE
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)

    # Relaciones
    location = db.relationship('Location', backref='inventory_movements')
    material = db.relationship('Material', backref='inventory_movements')

    def to_dict(self):
        return {
            'id': self.id,
            'id_location': self.id_location,
            'id_material': self.id_material,
            'quantity': self.quantity,
            'unit_type': self.unit_type,
            'movement_type': self.movement_type,
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }

class InventoryStock(db.Model):
    __tablename__ = 'inventory_stock'
    id = db.Column(db.Integer, primary_key=True)
    id_location = db.Column(db.Integer, db.ForeignKey('locations_inventory.id'), nullable=False)
    id_material = db.Column(db.String(50), db.ForeignKey('material.id_material'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    unit_type = db.Column(db.String(20), nullable=False)
    min_stock = db.Column(db.Integer, default=0)
    max_stock = db.Column(db.Integer, default=0)
    last_movement = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=False)

    # Relaciones
    location = db.relationship('Location', backref='inventory_stocks')
    material = db.relationship('Material', backref='inventory_stocks')

    def to_dict(self):
        return {
            'id': self.id,
            'id_location': self.id_location,
            'id_material': self.id_material,
            'quantity': self.quantity,
            'unit_type': self.unit_type,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'last_movement': self.last_movement.strftime('%Y-%m-%d %H:%M:%S') if self.last_movement else '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by': self.created_by
        }        