from flask import Blueprint, render_template, redirect, jsonify, url_for, flash, request
from flask_server.app import db, bcrypt
from flask_server.app.model.user_model import User
from flask_login import login_user, current_user, logout_user, login_required
from flask_server.app.request_form.LoginForm import LoginForm
from flask_server.app.request_form.RegisterForm import RegistrationForm
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

class AuthController:
    
    @staticmethod
    def login():
        # Cek kalau user sudah login, langsung lempar ke dashboard
        if current_user.is_authenticated:
            return redirect(url_for('app.index'))

        form = LoginForm()
        
        if request.method == 'POST':
            # 1. AMBIL INPUT
            # Pastikan di HTML name="username"
            login_input = request.form.get('username') 
            password = request.form.get('password')

            # Debugging (Opsional, akan muncul di terminal)
            print(f"[LOGIN DEBUG] Input: {login_input}")

            # 2. QUERY DATABASE (Logika OR: Email atau Username)
            user = User.query.filter(
                (User.email == login_input) | (User.username == login_input)
            ).first()

            # 3. CEK PASSWORD
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash('Login successful!', 'success')
                # Arahkan ke dashboard (pastikan nama fungsinya benar, biasanya app.index atau web.index)
                return redirect(url_for('app.index')) 
            else:
                flash('Login failed. Check username/email and password.', 'danger')
        
        return render_template('login.html', form=form)

    @staticmethod
    def logout():
        logout_user()
        # Redirect ke halaman login setelah logout
        return redirect(url_for("app.login"))
    
    @staticmethod
    def register():
        form = RegistrationForm()
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # Hash password sebelum simpan
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Cek apakah email/username sudah ada (opsional tapi disarankan)
            existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
            if existing_user:
                flash('Email or Username already exists.', 'warning')
                return render_template('register.html', form=form)

            user = User(username=username, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('app.login'))
            
        return render_template('register.html', form=form)
    
    @staticmethod
    def api_login():
        """Login endpoint to generate JWT token"""
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        email = data.get("email")
        password = data.get("password")

        # Validate credentials
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            # Generate a JWT token if credentials are valid
            access_token = create_access_token(identity=email)
            return jsonify(access_token=access_token), 200
        return jsonify({"message": "Invalid credentials"}), 401

    @staticmethod
    def api_register():
        try:
            # Ambil data JSON
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "No input data provided"}), 400

            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            # Validasi input sederhana
            if not username or not email or not password:
                return jsonify({"status": "error", "message": "Username, email, and password are required"}), 400

            # Cek user duplikat
            existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
            if existing_user:
                return jsonify({"status": "error", "message": "Email or Username already exists"}), 409

            # Hash password dan simpan
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, email=email, password=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()

            return jsonify({"status": "success", "message": "User registered successfully"}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500