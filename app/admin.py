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

class DepartamentoView(BaseAdminView):

    # Campos que se verán en la tabla

    column_list = ['nombre', 'edificio_piso']

    # Habilitar búsqueda por nombre

    column_searchable_list = ['nombre']

    # Nombre que aparecerá en el menú

    name = "Departamentos"

class UsuarioView(BaseAdminView):
    # 1. Vista de tabla limpia
    column_list = ['username', 'role', 'departamento']
    column_filters = ['role']
    
    # 2. Quitar "tickets" del formulario de creación/edición
    form_excluded_columns = ['tickets']
    
    # 3. Combobox estricto para roles
    form_choices = {
        'role': [
            ('empleado', 'Empleado'),
            ('tecnico', 'Técnico'),
            ('admin', 'Administrador')
        ]
    }
    
    # 4. Forzar que el Departamento sea obligatorio
    form_args = {
        'departamento': {
            'validators': [DataRequired(message="El departamento es obligatorio.")]
        }
    }
    
    # 5. Convertir el campo de texto de password en campo de contraseña (puntos)
    form_extra_fields = {
        'password': PasswordField('Contraseña')
    }

    # 6. Encriptar la contraseña correctamente al guardar
    def on_model_change(self, form, model, is_created):
        # Solo encriptamos si el usuario escribió algo en el campo
        if form.password.data:
            model.password = generate_password_hash(form.password.data)

# --- Espacio de Brayan (Categorías de Fallas) ---


# --- Espacio de Jose (Inventario de Equipos) ---


# --- Espacio de Waldo (Tickets y PDF) ---



# Registro global de vistas
def configuracion_admin():
    
    # Registro Samu
    
    admin.add_view(DepartamentoView(Departamento, db.session, name="Departamentos", category="Personal"))
    admin.add_view(UsuarioView(User, db.session, name="Usuarios", category="Personal"))
    
    # Registro Brayan
    
    
    # Registro Jose
    
    
    # Registro Waldo
    
    pass