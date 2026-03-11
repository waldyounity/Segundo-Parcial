from flask import redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_admin import Admin, AdminIndexView
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# 1. Creamos el guardia para la ruta principal del panel
class PanelSeguroView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        flash("Debes iniciar sesión para acceder al panel administrativo.", "warning")
        return redirect(url_for("auth.login"))

# 2. Le inyectamos el guardia al Admin en el parámetro index_view
admin = Admin(name="Soporte Técnico - IT", index_view=PanelSeguroView())

login_manager.login_view = "auth.login"