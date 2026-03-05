from flask_login import current_user
from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from .extensions import admin, db
from .models import Producto, User
#importamos el menu de inicio de sesion
from flask_admin.menu import MenuLink

class SecurityModelView(ModelView):
    colum_exclude_list = ["password"]
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, ):
        return redirect(url_for("auth.login"))
    
    #agregamos una funcion para que se encripte el password al crearse
    def on_model_change(self, form, model, is_created):
        # Si se escribió una contraseña en el formulario, la encriptamos antes de guardar
        if form.password.data:
            model.set_password(form.password.data)
    
def configuracion_admin():
    admin.add_view(SecurityModelView(User, db.session))
    #mostramos la tabla creada en las pesatañas
    admin.add_view(SecurityModelView(Producto, db.session))
    
    #agregamos el boton de cerrar sesion
    admin.add_link(MenuLink(name='Cerrar Sesión', category='', url='/logout'))