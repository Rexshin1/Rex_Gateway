from flask import render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from flask_server.app import db, bcrypt
from flask_server.app.model.user_model import User
from functools import wraps
import os
import secrets

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    # Ensure directory exists
    pics_dir = os.path.join(current_app.root_path, 'static', 'profile_pics')
    if not os.path.exists(pics_dir):
        os.makedirs(pics_dir)

    picture_path = os.path.join(pics_dir, picture_fn)
    form_picture.save(picture_path)
    return picture_fn

# Decorator for Admin Access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('app.index'))
        return f(*args, **kwargs)
    return decorated_function

class UserController:
    
    @staticmethod
    @login_required
    @admin_required
    def index():
        # List all users
        users = User.query.all()
        page = {"title": "User Management"}
        return render_template('users.html', page=page, users=users, user=current_user)

    @staticmethod
    @login_required
    @admin_required
    def add_user():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            role = request.form.get('role', 'user')

            # Basic Validation
            if not username or not email or not password:
                flash("All fields are required!", "danger")
                return redirect(url_for('app.users'))
            
            if ' ' in username:
                flash("Username cannot contain spaces.", "warning")
                return redirect(url_for('app.users'))

            
            # Check exist
            existing = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing:
                flash("Username or Email already taken.", "warning")
                return redirect(url_for('app.users'))
            
            # Create
            hashed = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, email=email, password=hashed, role=role)
            db.session.add(new_user)
            db.session.commit()
            
            flash(f"User {username} created successfully!", "success")
            
        return redirect(url_for('app.users'))

    @staticmethod
    @login_required
    def edit_user(user_id):
        # Allow if Admin OR if editing self
        if str(user_id) != str(current_user.id) and current_user.role != 'admin':
             flash("Unauthorized action.", "danger")
             return redirect(url_for('app.index'))

        user = User.query.get(user_id)
        if not user:
            flash("User not found.", "warning")
            return redirect(url_for('app.users'))

        if request.method == 'POST':
            # Role Update: Only Admin can change roles
            if current_user.role == 'admin':
                role = request.form.get('role')
                if role:
                    user.role = role
            
            # Update Username
            new_username = request.form.get('username')
            if new_username and new_username != user.username:
                if ' ' in new_username:
                     flash("Username cannot contain spaces.", "warning")
                     return redirect(url_for('app.users')) if current_user.role == 'admin' else redirect(url_for('app.profile'))
                
                existing_u = User.query.filter_by(username=new_username).first()
                if existing_u:
                    flash(f"Username {new_username} is already taken.", "warning")
                    return redirect(url_for('app.users')) if current_user.role == 'admin' else redirect(url_for('app.profile'))
                user.username = new_username
            
            # Update Email - Check uniqueness if changed
            new_email = request.form.get('email')
            if new_email and new_email != user.email:
                existing = User.query.filter_by(email=new_email).first()
                if existing:
                    flash(f"Email {new_email} is already taken.", "warning")
                    return redirect(url_for('app.users')) if current_user.role == 'admin' else redirect(url_for('app.profile'))
                user.email = new_email

            # Update Picture
            if 'picture' in request.files:
                file = request.files['picture']
                if file and file.filename != '':
                    try:
                        picture_file = save_picture(file)
                        user.image_file = picture_file
                    except Exception as e:
                        print(e)
                        flash("Error saving image.", "danger")

            # Update Password (Optional)
            password = request.form.get('password')
            if password:
                if len(password) < 6:
                     flash("Password must be at least 6 characters.", "warning")
                     return redirect(url_for('app.users')) if current_user.role == 'admin' else redirect(url_for('app.profile'))
                hashed = bcrypt.generate_password_hash(password).decode('utf-8')
                user.password = hashed
                flash(f"Password updated.", "info")

            db.session.commit()
            flash(f"User {user.username} updated.", "success")
        
        # Redirect back to appropriate page
        if current_user.role == 'admin' and "users" in request.referrer:
             return redirect(url_for('app.users'))
        return redirect(url_for('app.profile'))

    @staticmethod
    @login_required
    @admin_required
    def delete_user(user_id):
        # Prevent Deleting Self
        if str(user_id) == str(current_user.id):
            flash("You cannot delete yourself!", "danger")
            return redirect(url_for('app.users'))
            
        user = User.query.get(user_id)
        if user:
            # Prevent deleting the KEY Admin (e.g. ID 1) or Last Admin
            if user.role == 'admin':
                admin_count = User.query.filter_by(role='admin').count()
                if admin_count <= 1:
                    flash("Cannot delete the last Administrator account!", "danger")
                    return redirect(url_for('app.users'))

            db.session.delete(user)
            db.session.commit()
            flash("User deleted.", "success")
        else:
            flash("User not found.", "warning")
            
        return redirect(url_for('app.users'))

    @staticmethod
    @login_required
    def profile():
        page = {"title": "My Profile"}
        return render_template('profile.html', page=page, user=current_user)

    @staticmethod
    @login_required
    def change_password():
        if request.method == 'POST':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not current_password or not new_password or not confirm_password:
                flash("All password fields are required.", "danger")
                return redirect(url_for('app.profile'))

            # 1. Cek Password Lama Benar
            if not bcrypt.check_password_hash(current_user.password, current_password):
                flash("Incorrect Current Password.", "danger")
                return redirect(url_for('app.profile'))

            # 2. Cek Password Baru Sama dengan Konfirmasi
            if new_password != confirm_password:
                flash("New Password and Confirm Password do not match.", "warning")
                return redirect(url_for('app.profile'))
            
            # 3. Validasi Panjang Password
            if len(new_password) < 6:
                flash("Password must be at least 6 characters.", "warning")
                return redirect(url_for('app.profile'))

            # 4. Ganti Password
            hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.password = hashed
            db.session.commit()

            flash("Password changed successfully!", "success")
            return redirect(url_for('app.profile'))
        
        return redirect(url_for('app.profile'))
