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


# --- Espacio de Jose (Inventario de Equipos) ---

class EquipoAdminView(BaseAdminView):
    column_list = ['id', 'nombre', 'tipo', 'numero_serie', 'estado']
    column_searchable_list = ['nombre', 'numero_serie', 'tipo']
    column_filters = ['estado', 'tipo']
    column_sortable_list = ['nombre', 'tipo', 'estado', 'id']
    
    form_columns = ['nombre', 'tipo', 'numero_serie', 'estado']
    form_args = {
        'nombre': {'validators': [DataRequired()]},
        'numero_serie': {'validators': [DataRequired()]},
        'tipo': {'validators': [DataRequired()]},
        'estado': {'validators': [DataRequired()]},
    }
    
    def is_accessible(self):
        """Permitir acceso a admin, técnico y empleado"""
        return current_user.is_authenticated and current_user.role in ['admin', 'tecnico', 'empleado']
    
    def on_model_change(self, form, model, is_created):
        """Registra el usuario que ingresa el equipo"""
        if is_created:
            model.usuario_ingreso = current_user.username
        super().on_model_change(form, model, is_created)

# --- Espacio de Waldo (Tickets y PDF) ---



# Registro global de vistas
def configuracion_admin():
    
    # Registro Samu
    
    
    # Registro Brayan
    
    
    # Registro Jose
    
    admin.add_view(EquipoAdminView(Equipo, db.session, name='Equipos', category='Inventario'))
    
    # Registro Waldo
    
    pass