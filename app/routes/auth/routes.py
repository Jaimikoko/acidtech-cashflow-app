from datetime import datetime
from flask import render_template, request, url_for, redirect, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user

from models.user import User
from database import db

from app.forms import LoginForm, RegistrationForm
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(form.password.data):
            # Persist session
            login_user(user, remember=form.remember_me.data)
            session.permanent = True

            # Update audit info
            try:
                user.last_login = datetime.utcnow()
                db.session.commit()
            except Exception as e:
                current_app.logger.warning(f'Login audit commit failed: {e}')

            # Safe redirect
            next_url = request.args.get('next')
            if not next_url or not next_url.startswith('/'):
                next_url = url_for('main.dashboard')
            current_app.logger.info(f'Login OK for {username}; redirecting to {next_url}')
            return redirect(next_url)

        current_app.logger.info('Login failed: bad credentials')
        flash('Invalid username or password', 'error')

    # If GET or validation failed, re-render with errors
    if form.errors:
        current_app.logger.info(f'Login form errors: {form.errors}')
    return render_template('auth/login.html', form=form), 200

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append('Username already exists')
        if User.query.filter_by(email=form.email.data.lower()).first():
            form.email.errors.append('Email already exists')

        if form.errors:
            return render_template('auth/register.html', form=form)

        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='user'  # Default role
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)
