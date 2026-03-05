from flask import Blueprint, redirect, request, url_for, render_template
from flask_login import login_user, logout_user, current_user

from app.models import User
from .extensions import login_manager
# from flask_login import 

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@auth_bp.route('/')

def inicio():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods = ['GET', 'POST'])
def login():
    
    #verificamos si hay un usuario que ya inicio sesion
    if current_user.is_authenticated:
        return redirect("/admin")
    
    usuario = User.query.filter_by(
        username = request.form.get("nombre_usuario")
    ).first()
    
    if usuario and usuario.check_password(request.form.get("contrasenia")):
        login_user(usuario)
        return redirect("/admin")
    
    return render_template("login.html")

#creamos la ruta para cerrar sesion
@auth_bp.route('/logout')
def logout():
    logout_user() # Esto destruye la sesión actual
    return redirect(url_for('auth.login')) # Te devuelve a la pantalla de login