from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from project import db
from project.models import User

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'error')

        # if the user doesn't exist or password is wrong, reload the page
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.dashboard'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    is_admin = True if request.form.get('profile') == 'admin' else False

    # if this returns a user, then the username already exists in database
    user = User.query.filter_by(username=username).first()

    is_error = False
    if user:
        flash('This username already exists', 'error')
        is_error = True

    if len(username) < 5:
        flash('Your username should be at least 6 characters', 'error')
        is_error = True

    if len(password) < 7:
        flash('Your password should be at least 8 characters', 'error')
        is_error = True

    if password != password2:
        flash('Password not matching!', 'error')
        is_error = True

    if is_error:
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(
        username=username,
        password=generate_password_hash(password, method='sha256'),
        is_admin=is_admin,
    )

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    flash('You are registered and can login!', 'success')

    return redirect(url_for('auth.login'))

