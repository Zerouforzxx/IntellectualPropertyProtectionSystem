import uuid

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required

from app import db
from . import auth
from ..models import User, Wallet
from .forms import LoginForm, RegisterForm
from app.ethereum_service import new_account


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.args.get('next'):
        form.next.data = request.args.get('next')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(form.next.data or url_for('main.index'))
        form.password.errors.append('账号密码错误')
        # flash('账号密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    # flash('登出成功', 'success')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.args.get('next'):
        form.next.data = request.args.get('next')
    if form.validate_on_submit():
        role = 1 if User.query.first() is None else 0
        user = User(username=form.username.data, email=form.email.data, password=form.password.data, name=form.name.data, role=role)
        db.session.add(user)
        key_origin = uuid.uuid4().hex
        address = new_account(key_origin)
        wallet = Wallet(address=address, key_origin=key_origin, owner_user=user)
        db.session.add(wallet)
        flash('注册成功, 请登录', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)