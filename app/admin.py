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

class EquipoView(ModelView): 
    # 1. SEGURIDAD: Solo admin y técnicos
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role in ['admin', 'tecnico']

    def inaccessible_callback(self, name, **kwargs):
        flash("No tienes permisos para acceder al inventario de equipos.", "error")
        return redirect(url_for('admin.index'))

    # 2. VISTAS DE TABLA Y FILTROS
    column_list = ['nombre', 'tipo', 'numero_serie', 'estado']
    column_searchable_list = ['nombre', 'numero_serie']
    column_filters = ['tipo', 'estado']

    # 3. ETIQUETAS AMIGABLES
    column_labels = {
        'nombre': 'Nombre del Equipo',
        'numero_serie': 'Número de Serie (S/N)',
        'tipo': 'Tipo de Equipo'
    }

    # 4. REGLAS DE FORMULARIO (Control exacto de qué se ve)
    form_create_rules = ('nombre', 'tipo', 'numero_serie')
    form_edit_rules = ('nombre', 'tipo', 'numero_serie', 'estado')

    # 5. PLACEHOLDERS
    form_widget_args = {
        'nombre': {
            'placeholder': 'Ej: Laptop Gerencia, Switch Piso 2'
        },
        'numero_serie': {
            'placeholder': 'Ej: LNV-8890-XYZ'
        }
    }

    # 6. COMBOBOX ESTRICTOS
    form_choices = {
        'estado': [
            ('Activo', 'Activo'), 
            ('En Reparación', 'En Reparación'), 
            ('Dado de Baja', 'Dado de Baja')
        ],
        'tipo': [
            ('Servidor', 'Servidor'), 
            ('Laptop', 'Laptop'), 
            ('Impresora', 'Impresora'), 
            ('Redes', 'Redes'),
            ('Periférico', 'Periférico')
        ]
    }

    # 7. AUTOMATIZACIÓN DEL ESTADO
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.estado = 'Activo'

# --- Espacio de Waldo (Tickets y PDF) ---



# Registro global de vistas
def configuracion_admin():
    
    # Registro Samu
    
    
    # Registro Brayan
    
    
    # Registro Jose
    
    admin.add_view(EquipoView(Equipo, db.session, name='Equipos', category='Inventario'))
    
    # Registro Waldo
    
    pass