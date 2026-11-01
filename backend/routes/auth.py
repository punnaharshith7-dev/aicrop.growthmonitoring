import os
import re
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlparse

from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, session, current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func

from backend.models import db, User

auth_bp = Blueprint('auth', __name__)

# ── URL Safety Helper ─────────────────────────────────────────────────────────
def is_safe_url(target):
    """Ensure redirect URL is strictly local to avoid open-redirect vulnerabilities."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('', 'http', 'https') and (not test_url.netloc or test_url.netloc == ref_url.netloc)


# ── Registration Input Validation ─────────────────────────────────────────────
def validate_registration(data):
    """Thoroughly validate registration form inputs, returning an error dictionary."""
    errors = {}
    
    username  = (data.get('username') or '').strip()
    email     = (data.get('email') or '').strip().lower()
    full_name = (data.get('full_name') or '').strip()
    phone     = (data.get('phone') or '').strip()
    farm_size = (data.get('farm_size') or '').strip()
    password  = data.get('password') or ''
    confirm   = data.get('confirm_password') or ''

    # Username validation
    if not username:
        errors['username'] = 'Username is required.'
    elif len(username) < 3 or len(username) > 30:
        errors['username'] = 'Username must be between 3 and 30 characters long.'
    elif not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        errors['username'] = 'Username may only contain letters, numbers, underscores, hyphens, and periods.'
    else:
        existing_user = User.query.filter(func.lower(User.username) == username.lower()).first()
        if existing_user:
            errors['username'] = 'This username is already taken. Please choose another.'

    # Email validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not email:
        errors['email'] = 'Email address is required.'
    elif len(email) > 120 or not re.match(email_regex, email):
        errors['email'] = 'Please provide a valid email address (e.g., farmer@example.com).'
    else:
        existing_email = User.query.filter(func.lower(User.email) == email.lower()).first()
        if existing_email:
            errors['email'] = 'An account with this email address is already registered.'

    # Password validation
    if not password:
        errors['password'] = 'Password is required.'
    elif len(password) < 6:
        errors['password'] = 'Password must be at least 6 characters long.'
    elif password.isspace():
        errors['password'] = 'Password cannot consist solely of whitespace.'

    # Confirm password
    if not confirm:
        errors['confirm_password'] = 'Please confirm your password.'
    elif password != confirm:
        errors['confirm_password'] = 'Passwords do not match.'

    # Optional fields validation
    if full_name and len(full_name) > 120:
        errors['full_name'] = 'Full name must be under 120 characters.'

    if phone:
        phone_regex = r'^[+]?[\d\s\-()]{7,20}$'
        if not re.match(phone_regex, phone):
            errors['phone'] = 'Please enter a valid phone number (e.g., +1 234 567 8900).'

    if farm_size:
        try:
            val = float(farm_size)
            if val < 0:
                errors['farm_size'] = 'Farm acreage cannot be negative.'
            elif val > 1000000:
                errors['farm_size'] = 'Please enter a realistic farm size.'
        except (ValueError, TypeError):
            errors['farm_size'] = 'Farm size must be a numeric value in hectares.'

    return errors


# ── Registration Route ────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        errors = validate_registration(request.form)

        if errors:
            for field, err_msg in errors.items():
                flash(err_msg, 'danger')
            return render_template('auth/register.html', errors=errors, form_data=request.form)

        username  = request.form.get('username', '').strip()
        email     = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        phone     = request.form.get('phone', '').strip()
        location  = request.form.get('location', '').strip()
        farm_size_val = request.form.get('farm_size', '').strip()

        try:
            farm_size = float(farm_size_val) if farm_size_val else None
        except (ValueError, TypeError):
            farm_size = None

        new_user = User(
            username  = username,
            email     = email,
            full_name = full_name or None,
            phone     = phone or None,
            location  = location or None,
            farm_size = farm_size,
        )
        new_user.set_password(request.form.get('password', ''))

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please sign in with your credentials.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {e}")
            flash('An unexpected error occurred while saving your account. Please try again.', 'danger')
            return render_template('auth/register.html', errors={'general': str(e)}, form_data=request.form)

    return render_template('auth/register.html', errors={}, form_data={})


# ── Login Route ───────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password', '')
        remember   = request.form.get('remember') == 'on'

        if not identifier or not password:
            flash('Please enter both your username/email and password.', 'danger')
            return render_template('auth/login.html', identifier=identifier)

        # Case-insensitive search on username or email
        user = User.query.filter(
            (func.lower(User.username) == identifier.lower()) |
            (func.lower(User.email) == identifier.lower())
        ).first()

        if user and user.check_password(password):
            # Configure session persistence
            session.permanent = remember
            login_user(user, remember=remember)

            next_page = request.args.get('next')
            if not next_page or not is_safe_url(next_page):
                next_page = url_for('dashboard.index')

            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username/email or password. Please verify your credentials and try again.', 'danger')
            return render_template('auth/login.html', identifier=identifier)

    return render_template('auth/login.html', identifier='')


# ── Logout Route ──────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    farmer_name = current_user.full_name or current_user.username
    logout_user()
    flash(f'Goodbye, {farmer_name}. You have been logged out securely.', 'info')
    response = redirect(url_for('auth.login'))
    remember_cookie = current_app.config.get('REMEMBER_COOKIE_NAME', 'remember_token')
    response.delete_cookie(remember_cookie)
    return response


# ── Password Recovery ─────────────────────────────────────────────────────────
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your account email address.', 'danger')
            return render_template('auth/forgot_password.html')

        user = User.query.filter(func.lower(User.email) == email).first()

        if user:
            token  = secrets.token_urlsafe(32)
            expiry = datetime.utcnow() + timedelta(hours=1)
            user.reset_token  = token
            user.reset_expiry = expiry
            db.session.commit()

            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f'Password reset token generated. (Demo) <a href="{reset_url}">Click here to reset your password</a>', 'info')
        else:
            # Ambiguous message to prevent account enumeration
            flash('If an account exists with that email address, a password reset link has been dispatched.', 'info')

    return render_template('auth/forgot_password.html')


# ── Reset Password ────────────────────────────────────────────────────────────
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or (user.reset_expiry and user.reset_expiry < datetime.utcnow()):
        flash('The password reset link is invalid or has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            user.set_password(password)
            user.reset_token  = None
            user.reset_expiry = None
            db.session.commit()
            flash('Password updated successfully! Please sign in with your new password.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


# ── Farmer Profile ────────────────────────────────────────────────────────────
@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone     = request.form.get('phone', '').strip()
        location  = request.form.get('location', '').strip()
        farm_size = request.form.get('farm_size', '').strip()

        current_user.full_name = full_name or None
        current_user.location  = location or None

        if phone:
            phone_regex = r'^[+]?[\d\s\-()]{7,20}$'
            if re.match(phone_regex, phone):
                current_user.phone = phone
            else:
                flash('Invalid phone format. Kept previous phone number.', 'warning')
        else:
            current_user.phone = None

        if farm_size:
            try:
                val = float(farm_size)
                if val >= 0:
                    current_user.farm_size = val
            except (ValueError, TypeError):
                flash('Farm size must be a valid number.', 'warning')

        # Profile image upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename:
                ext = file.filename.rsplit('.', 1)[-1].lower()
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
                    os.makedirs(upload_dir, exist_ok=True)
                    fname = f"profile_{current_user.id}_{secrets.token_hex(4)}.{ext}"
                    file.save(os.path.join(upload_dir, fname))
                    current_user.profile_image = f'uploads/profiles/{fname}'
                else:
                    flash('Invalid image format. Allowed: JPG, PNG, GIF, BMP.', 'danger')

        try:
            db.session.commit()
            flash('Profile details updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Profile update error: {e}")
            flash('Error saving profile changes.', 'danger')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
