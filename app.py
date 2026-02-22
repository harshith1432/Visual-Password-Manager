import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from models import db, User, PlatformPassword
from utils import generate_random_password, encrypt_password, decrypt_password, get_decoys
import random

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB

db.init_app(app)
migrate = Migrate(app, db)

# Ensure upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning \u2600\uFE0F"
    elif hour < 18:
        return "Good Afternoon \U0001F324\uFE0F"
    else:
        return "Good Evening \U0001F319"

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        pin = request.form.get('pin')
        
        if not pin.isdigit():
            flash('PIN must be numeric.', 'danger')
            return redirect(url_for('register'))
            
        user = User(name=name)
        user.set_pin(pin)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        pin = request.form.get('pin')
        
        # Find all users with this name
        users = User.query.filter_by(name=name).all()
        
        target_user = None
        for u in users:
            if u.check_pin(pin):
                target_user = u
                break
        
        if target_user:
            session['user_id'] = target_user.id
            session['decoy_mode'] = False 
            flash(f'Welcome back, {target_user.name}!', 'success')
        else:
            # Create a NEW user for this wrong PIN -> New Empty Vault
            new_shadow_user = User(name=name)
            new_shadow_user.set_pin(pin)
            db.session.add(new_shadow_user)
            db.session.commit()
            
            session['user_id'] = new_shadow_user.id
            session['decoy_mode'] = True 
            flash('Login successful!', 'success')
            
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('user_id') == -1:
        session.clear()
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    platforms = PlatformPassword.query.filter_by(user_id=user.id).all()
    user_name = user.name
        
    return render_template('dashboard.html', platforms=platforms, user_name=user_name, greeting=get_greeting())

@app.route('/add-platform', methods=['GET', 'POST'])
def add_platform():
    if 'user_id' not in session or session.get('user_id') == -1:
        session.clear()
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        platform_name = request.form.get('platform_name')
        password = request.form.get('password')
        category = request.form.get('category', 'other')
        image = request.files.get('secret_image')
        
        if not image:
            flash("Please upload a secret image.", "danger")
            return redirect(url_for('add_platform'))
            
        filename = secure_filename(f"{session['user_id']}_{platform_name}_{image.filename}")
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        
        new_pass = PlatformPassword(
            user_id=session['user_id'],
            platform=platform_name,
            encrypted_password=encrypt_password(password),
            image_path=filename,
            category=category
        )
        db.session.add(new_pass)
        db.session.commit()
        flash(f'Platform {platform_name} added successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    generated_pass = generate_random_password()
    return render_template('add_platform.html', generated_pass=generated_pass)

@app.route('/verify/<int:platform_id>', methods=['GET', 'POST'])
def verify(platform_id):
    if 'user_id' not in session:
        return redirect(url_for('dashboard'))
        
    platform = PlatformPassword.query.get_or_404(platform_id)
    
    # Check if locked
    if platform.is_locked():
        flash(f"This platform is locked until {platform.lock_until}. Try again later.", "danger")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        image_choice = request.form.get('image_choice')
        
        if image_choice == platform.image_path:
            # Success
            platform.failed_attempts = 0
            db.session.commit()
            decrypted = decrypt_password(platform.encrypted_password)
            return render_template('reveal.html', platform=platform, password=decrypted)
        else:
            # Failure
            platform.failed_attempts += 1
            if platform.failed_attempts == 1:
                flash(get_greeting(), "info")
            elif platform.failed_attempts == 2:
                flash("One more wrong attempt will lock access for 24 hours.", "warning")
            elif platform.failed_attempts >= 3:
                platform.lock_until = datetime.utcnow() + timedelta(hours=24)
                db.session.commit()
                # Trigger Notification via Flash or specialized response
                return render_template('locked.html', platform=platform)
            
            db.session.commit()
            return redirect(url_for('verify', platform_id=platform_id))
            
    # Prepare gallery: 19 decoys + 1 secret = 20 images
    decoys = get_decoys(platform.category, 19)
    
    # Store images as list of objects to track type
    image_list = []
    for d in decoys:
        image_list.append({'path': d, 'is_secret': False})
    image_list.append({'path': platform.image_path, 'is_secret': True})
    
    random.shuffle(image_list)
    
    return render_template('verify.html', platform=platform, images=image_list)

@app.route('/change-image/<int:platform_id>', methods=['GET', 'POST'])
def change_image(platform_id):
    if 'user_id' not in session:
        return redirect(url_for('dashboard'))
        
    platform = PlatformPassword.query.get_or_404(platform_id)
    
    if request.method == 'POST':
        password_attempt = request.form.get('current_password')
        new_password = request.form.get('new_password')
        new_image = request.files.get('new_image')
        
        if decrypt_password(platform.encrypted_password) == password_attempt:
            # RESET LOCK AND ATTEMPTS IF PASSWORD MATCHES
            platform.failed_attempts = 0
            platform.lock_until = None
            
            if new_password:
                platform.encrypted_password = encrypt_password(new_password)
            
            if new_image:
                filename = secure_filename(f"{session['user_id']}_{platform.platform}_{new_image.filename}")
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                new_image.save(image_path)
                platform.image_path = filename
            
            db.session.commit()
            flash("Security details updated successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect password. No changes made.", "danger")
            
    return render_template('change_image.html', platform=platform)

@app.route('/api/generate-password')
def api_generate_password():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"password": generate_random_password()})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
