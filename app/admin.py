from flask_login import current_user
from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from .extensions import admin, db
from .models import User, Departamento, Categoria, Equipo, Ticket
from wtforms.validators import DataRequired
# Clase base de seguridad para el panel
class BaseAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))


# --- Espacio de Samu (Personal y Departamentos) ---


# --- Espacio de Brayan (Categorías de Fallas) ---

class CategoriaAdmin(BaseAdminView):
    column_list = ['nombre', 'nivel_gravedad', 'tiempo_estimado_horas']
    column_searchable_list = ['nombre']
    column_filters = ['nivel_gravedad']
    column_editable_list = ['nivel_gravedad', 'tiempo_estimado_horas']
    column_labels = {
        'nombre': 'Categoría',
        'nivel_gravedad': 'Gravedad',
        'tiempo_estimado_horas': 'Tiempo (horas)'
    }
    form_columns = ['nombre', 'nivel_gravedad', 'tiempo_estimado_horas']
    
# --- Espacio de Jose (Inventario de Equipos) ---


# --- Espacio de Waldo (Tickets y PDF) ---



# Registro global de vistas
def configuracion_admin():
    
    # Registro Samu
    
    
    # Registro Brayan
    
        admin.add_view(CategoriaAdmin(Categoria, db.session, name="Categorías", endpoint="admin_categorias"))
    
    # Registro Jose
    
    
    # Registro Waldo
    
pass