from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .user import User
from functools import wraps


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name') 
        password = request.form.get('password') 
        
        if user_name and password:
            user = User.login_user(user_name, password)
            if user:
                session["user_id"] = user.id
                session["user_name"] = user.user_name
                session["user_full_name"] = user.user_full_name
                session["user_role"] = user.user_role
                return redirect(url_for('views.home'))
        else:
            flash("Introduce el nombre de usuario y la contraseña en los campos que aparecen por pantalla", category='error')

    return render_template("login.html")


#Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_name' in session:
            return f(*args, **kwargs)
        else:
            flash('Acceso no autorizado. Por favor, inicia sesión', category='error')
            return redirect(url_for('auth.login'))
    return wrap

#Check if user is admin
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('user_name' in session) and User.isAdmin(session["user_name"]):
            return f(*args, **kwargs)
        else:
            flash('Acceso no autorizado. Por favor, inicia sesión como administrador', category='error')
            return redirect(url_for('auth.login'))
    return wrap

@auth.route('/logout')
@is_logged_in
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_full_name", None)
    session.pop("user_role", None)
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form.get('user_name') 
        user_full_name = request.form.get('user_full_name') 
        password = request.form.get('password') 
        password2 = request.form.get('password2') 
        user_role = request.form.get('user_role')

        valid_data = True
        if not user_name or not user_full_name or not password or not password2 or not user_role:
            flash('Tienes que rellenar todos los campos que aparecen por pantalla.', category='error')
            valid_data = False
        if password and len(password) < 9:
            flash('La contraseña tiene que tener más de 8 caracteres.', category='error')
            valid_data = False
        if password != password2:
            flash('Las contraseñas introducidas no coinciden.', category='error')
            valid_data = False
        if User.search_user(user_name):
            flash('El nombre de usuario ya existe.', category='error')
            valid_data = False
     
        if valid_data:
            user = User.create_user(user_name, user_full_name, password, user_role)
            if user:
                session["user_id"] = user.id
                session["user_name"] = user.user_name
                session["user_full_name"] = user.user_full_name
                session["user_role"] = user.user_role
                return redirect(url_for('views.home'))
            else:
                flash('No se ha podido introducir el usuario en la base de datos.', category='error')
                
    return render_template("sign_up.html")

@auth.route('/search-user', methods=['GET', 'POST'])
def search_user():
    if request.method == 'POST':
        user_name = request.form.get('user_name') 
        list_users = User.search_users(user_name)
        if list_users:
            return render_template("listusers.html", list_users=list_users)

    return render_template("search_user.html")


@auth.route('/delete-user', methods=['GET', 'POST'])
#@admin_required
def delete_user():
    if request.method == 'POST':
        user_name = request.form.get('user_name') 
        user = User.search_user(user_name)
        if user:
            user_id = user.id
            user_deleted = User.delete(user)
            if user_deleted and user_id == session["user_id"]:
                return redirect(url_for('auth.logout'))
            elif user_deleted:
                return redirect(url_for('views.home'))

    return redirect(url_for('views.home'))

@auth.route('/user', methods=['GET'])
def user():
    user_id = request.args.get('id')
    if user_id:
        user = User.get_user_by_id(user_id)
        if user:
            return render_template("user.html", user=user)

    return redirect(url_for('views.home'))


@auth.route('/modify-user', methods=['GET', 'POST'])
#@admin_required
def modify_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id') 
        if user_id:
            user = User.get_user_by_id(user_id)
            if "user_name" in request.form:
                user.user_name = request.form.get('user_name')
            elif "user_full_name" in request.form:
                user.user_full_name = request.form.get('user_full_name')
            elif "password" in request.form:
                print("Hola")
                password = request.form.get('password')
                password2 = request.form.get('password2')
                if password != password2:
                    flash('Las contraseñas introducidas no coinciden.', category='error')
                else:
                    user.set_password(password)

            user = User.save_user(user)

            if user:
                return redirect(url_for('auth.user', id = user.id))

    return redirect(url_for('views.home'))


@auth.route('/list-all-users', methods=['GET'])
@admin_required
def list_all_users():
    return render_template("listusers.html", list_users=User.get_all_users())


