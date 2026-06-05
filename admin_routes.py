from flask import render_template, redirect, url_for, session, flash, request, jsonify
from functools import wraps
from flask_login import login_required, current_user
from models import User
from extensions import db

ADMIN_EMAIL = 'artemidos17@gmail.com'

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in first.', 'error')
            return redirect(url_for('signup'))
        if current_user.email != ADMIN_EMAIL or current_user.role != 'admin':
            flash('Admin access only!', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def init_admin_routes(app):
    """Initialize admin routes"""
    
    @app.route('/admin')
    ##@login_required
    @admin_required
    def admin_dashboard():
        users = User.query.all()
        return render_template('admin.html', users=users)
    
    @app.route('/admin/users')
    ##@login_required
    @admin_required
    def admin_users_list():
        users = User.query.all()
        return jsonify([{
            'id': u.id,
            'email': u.email,
            'role': u.role,
            'is_verified': u.is_verified,
            'created_at': u.id
        } for u in users])
    
    @app.route('/admin/user/<int:user_id>/promote', methods=['POST'])
    ##@login_required
    @admin_required
    def promote_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.email == ADMIN_EMAIL:
            return jsonify({'error': 'Cannot modify primary admin'}), 403
        user.role = 'admin'
        db.session.commit()
        flash(f'{user.email} promoted to admin!', 'success')
        return jsonify({'success': True, 'message': f'{user.email} is now admin'})
    
    @app.route('/admin/user/<int:user_id>/demote', methods=['POST'])
    ##@login_required
    @admin_required
    def demote_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.email == ADMIN_EMAIL:
            return jsonify({'error': 'Cannot modify primary admin'}), 403
        user.role = 'user'
        db.session.commit()
        flash(f'{user.email} demoted to user.', 'success')
        return jsonify({'success': True, 'message': f'{user.email} is now user'})
    
    @app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
    ##@login_required
    @admin_required
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user.email == ADMIN_EMAIL:
            return jsonify({'error': 'Cannot delete primary admin'}), 403
        email = user.email
        db.session.delete(user)
        db.session.commit()
        flash(f'{email} deleted.', 'success')
        return jsonify({'success': True, 'message': f'{email} has been deleted'})
    
    @app.route('/admin/user/<int:user_id>/verify', methods=['POST'])
    ##@login_required
    @admin_required
    def verify_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.is_verified = True
        db.session.commit()
        flash(f'{user.email} verified!', 'success')
        return jsonify({'success': True, 'message': f'{user.email} verified'})
