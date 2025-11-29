from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Role
from app.utils.auth import permission_required, superuser_required

bp = Blueprint('users', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('users.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('users/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('users.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    from app.models import User, Role
    total_users = User.query.count()
    total_roles = Role.query.count()
    
    # Calcular módulos activos para el usuario actual
    modules = ['materials', 'inventory', 'customers', 'accounting', 
              'suppliers', 'reporting', 'purchases', 'sales', 'users']
    
    active_modules = 0
    for module in modules:
        if current_user.has_permission(module, 1):  # Nivel 1 o superior
            active_modules += 1
    
    return render_template('users/dashboard.html', 
                         total_users=total_users, 
                         total_roles=total_roles,
                         active_modules=active_modules,
                         total_modules=len(modules))  # También pasamos el total para referencia

@bp.route('/users')
@login_required
@permission_required('users', 1)
def user_list():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@permission_required('users', 2)
def user_create():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form['role_id']
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('users.user_create'))
        
        user = User(
            username=username,
            email=email,
            role_id=role_id if role_id else None
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('users.user_list'))
    
    roles = Role.query.all()
    return render_template('users/create.html', roles=roles)

# Editar Usuario
@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('users', 2)
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role_id = request.form['role_id'] if request.form['role_id'] else None
        user.is_active = 'is_active' in request.form
        
        # Si se proporciona una nueva contraseña, actualizarla
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('Usuario actualizado exitosamente', 'success')
        return redirect(url_for('users.user_list'))
    
    roles = Role.query.all()
    return render_template('users/edit.html', user=user, roles=roles)

# Eliminar Usuario
@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@permission_required('users', 2)
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    
    # No permitir eliminar al superusuario admin
    if user.username == 'admin':
        flash('No se puede eliminar al superusuario admin', 'error')
        return redirect(url_for('users.user_list'))
    
    # No permitir que un usuario se elimine a sí mismo
    if user.id == current_user.id:
        flash('No puedes eliminar tu propio usuario', 'error')
        return redirect(url_for('users.user_list'))
    
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado exitosamente', 'success')
    return redirect(url_for('users.user_list'))

@bp.route('/roles')
@login_required
@permission_required('users', 1)
def role_list():
    roles = Role.query.all()
    return render_template('users/roles_list.html', roles=roles)

@bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
@permission_required('users', 2)
def role_create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        # Obtener permisos del formulario
        permissions = {}
        modules = ['materials', 'inventory', 'customers', 'accounting', 
                  'suppliers', 'reporting', 'purchases', 'sales', 'users']
        
        for module in modules:
            permission_value = int(request.form.get(f'{module}_permission', 0))
            permissions[f'{module}_permission'] = permission_value
        
        role = Role(name=name, description=description, **permissions)
        
        db.session.add(role)
        db.session.commit()
        flash('Rol creado exitosamente', 'success')
        return redirect(url_for('users.role_list'))
    
    return render_template('users/role_create.html')

# Editar Rol
@bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('users', 2)
def role_edit(role_id):
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        role.name = request.form['name']
        role.description = request.form['description']
        
        # Actualizar permisos
        modules = ['materials', 'inventory', 'customers', 'accounting', 
                  'suppliers', 'reporting', 'purchases', 'sales', 'users']
        
        for module in modules:
            setattr(role, f'{module}_permission', int(request.form.get(f'{module}_permission', 0)))
        
        db.session.commit()
        flash('Rol actualizado exitosamente', 'success')
        return redirect(url_for('users.role_list'))
    
    return render_template('users/role_edit.html', role=role)

# Eliminar Rol
@bp.route('/roles/<int:role_id>/delete', methods=['POST'])
@login_required
@permission_required('users', 2)
def role_delete(role_id):
    role = Role.query.get_or_404(role_id)
    
    # No permitir eliminar el rol Superadmin
    if role.name == 'Superadmin':
        flash('No se puede eliminar el rol Superadmin', 'error')
        return redirect(url_for('users.role_list'))
    
    # Verificar si hay usuarios con este rol
    if role.users.count() > 0:
        flash('No se puede eliminar el rol porque hay usuarios asignados a él', 'error')
        return redirect(url_for('users.role_list'))
    
    db.session.delete(role)
    db.session.commit()
    flash('Rol eliminado exitosamente', 'success')
    return redirect(url_for('users.role_list'))