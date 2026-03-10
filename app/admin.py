from flask_login import current_user
from flask import redirect, url_for, flash, request, render_template, make_response
from flask_admin.contrib.sqla import ModelView
from .extensions import admin, db
from .models import User, Departamento, Categoria, Equipo, Ticket
from wtforms.validators import DataRequired
from flask_admin.actions import action
from wtforms import PasswordField
from werkzeug.security import generate_password_hash
import pdfkit
from datetime import datetime

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

class TicketView(ModelView):
    
    # 0. SEGURIDAD: Todos los usuarios logueados pueden ver la pestaña
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("auth.login"))
    
    # 1. Columnas que se ven en la tabla principal
    column_list = ['id', 'titulo', 'estado', 'creador', 'equipo', 'categoria']
    
    # 2. Evitamos que el usuario edite el Estado o el Creador manualmente en el formulario
    # Al quitarlos de aquí, Flask-Admin no los muestra en 'Create' ni en 'Edit'
    form_excluded_columns = ['estado', 'creador']

    # 3. SEGURIDAD: Solo el empleado ve sus propios tickets
    def get_query(self):
        if current_user.role == 'empleado':
            return self.session.query(self.model).filter(self.model.usuario_id == current_user.id)
        return super(TicketView, self).get_query()

    # 4. PROCESO AUTOMÁTICO: Asignar usuario y estado inicial
    def on_model_change(self, form, model, is_created):
        if is_created:
            # Asignamos al usuario que está creando el ticket automáticamente
            model.usuario_id = current_user.id
            # Forzamos el estado inicial
            model.estado = 'Pendiente'

    # 5. ACCIÓN PARA EL TÉCNICO: Botón de "Finalizar Ticket"
    @action('completar_ticket', 'Marcar como Completado', '¿Está seguro de que desea finalizar los tickets seleccionados?')
    def action_completar_ticket(self, ids):
        if current_user.role not in ['admin', 'tecnico']:
            flash("No tienes permiso para cambiar el estado de los tickets.", "error")
            return
        
        try:
            # Buscamos los tickets por ID y los actualizamos
            query = Ticket.query.filter(Ticket.id.in_(ids))
            count = 0
            for ticket in query.all():
                ticket.estado = 'Completado'
                count += 1
            db.session.commit()
            flash(f"Se han finalizado {count} tickets exitosamente.", "success")
        except Exception as ex:
            flash(f"Error al actualizar tickets: {str(ex)}", "error")
            
    # ACCIÓN PARA REVERTIR ERRORES: Volver a estado Pendiente
    @action('reabrir_ticket', 'Reabrir Ticket (Deshacer)', '¿Está seguro de que desea volver a abrir los tickets seleccionados? Pasarán a estado Pendiente.')
    def action_reabrir_ticket(self, ids):
        if current_user.role not in ['admin', 'tecnico']:
            flash("No tienes permiso para cambiar el estado de los tickets.", "error")
            return
        
        try:
            query = Ticket.query.filter(Ticket.id.in_(ids))
            count = 0
            for ticket in query.all():
                # Evitamos "reabrir" algo que ya está pendiente
                if ticket.estado != 'Pendiente':
                    ticket.estado = 'Pendiente'
                    count += 1
            db.session.commit()
            flash(f"Se han reabierto {count} tickets exitosamente. Vuelven a la cola de trabajo.", "success")
        except Exception as ex:
            flash(f"Error al actualizar tickets: {str(ex)}", "error")

    # 6. ACCIÓN PARA EL PDF
    @action('generar_pdf', 'Exportar Informe (PDF)', '¿Desea generar el documento técnico de los tickets seleccionados?')
    def action_generar_pdf(self, ids):
        try:
            ruta_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            config = pdfkit.configuration(wkhtmltopdf=ruta_wkhtmltopdf)

            # Obtenemos TODOS los tickets seleccionados
            tickets = self.session.query(Ticket).filter(Ticket.id.in_(ids)).all()
            
            # 1. Renderizamos pasando la lista 'tickets' (en plural)
            html_renderizado = render_template(
                'reporte_ticket.html', 
                tickets=tickets, 
                fecha=datetime.now().strftime("%Y-%m-%d %H:%M")
            )

            # 2. Convertir a PDF maestro
            pdf_generado = pdfkit.from_string(html_renderizado, False, configuration=config)

            # 3. Forzar descarga del lote
            response = make_response(pdf_generado)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=Reporte_Tickets_Lote.pdf'
            
            return response

        except Exception as ex:
            flash(f"Error al generar PDF: {str(ex)}", "error")

# Registro global de vistas
def configuracion_admin():
    
    # Registro Samu
    
    admin.add_view(DepartamentoView(Departamento, db.session, name="Departamentos", category="Personal"))
    admin.add_view(UsuarioView(User, db.session, name="Usuarios", category="Personal"))
    
    # Registro Brayan
    
    
    # Registro Jose
    
    admin.add_view(EquipoAdminView(Equipo, db.session, name='Equipos', category='Inventario'))
    
    # Registro Waldo
    
    admin.add_view(TicketView(Ticket, db.session, name="Gestión de Tickets", category="Soporte"))
    
    pass