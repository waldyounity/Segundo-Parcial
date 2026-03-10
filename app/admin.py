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

class CategoriaView(BaseAdminView):
    column_list = ['nombre', 'nivel_gravedad', 'tiempo_estimado_horas']
    column_searchable_list = ['nombre']
    column_filters = ['nivel_gravedad']
    column_sortable_list = ['nombre', 'nivel_gravedad', 'tiempo_estimado_horas']
    
    form_excluded_columns = ['tickets']
    
    column_labels = {
        'nombre': 'Nombre de la Categoría',
        'nivel_gravedad': 'Nivel de Gravedad',
        'tiempo_estimado_horas': 'Tiempo Estimado (horas)'
    }
    
    form_choices = {
        'nivel_gravedad': [
            ('Alta', 'Alta'),
            ('Media', 'Media'),
            ('Baja', 'Baja')
        ]
    }
    
    form_args = {
        'nombre': {
            'validators': [DataRequired(message="El nombre de la categoría es obligatorio.")]
        },
        'nivel_gravedad': {
            'validators': [DataRequired(message="Debes seleccionar un nivel de gravedad.")]
        },
        'tiempo_estimado_horas': {
            'validators': [DataRequired(message="El tiempo estimado es obligatorio.")]
        }
    }
    
    form_widget_args = {
        'nombre': {
            'placeholder': 'Falla de Hardware, Problema de Red, Capacitación...'
        },
        'tiempo_estimado_horas': {
            'min': 1,
            'max': 720,
            'style': 'width: 100px',
            'placeholder': 'Ej: 24, 48, 72...'
        }
    }

# --- Espacio de Jose (Inventario de Equipos) ---

<<<<<<< HEAD
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
=======
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
>>>>>>> 3de312f78af9b0228995cc25209007d69c51d132

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
<<<<<<< HEAD
=======
                if ticket.equipo:
                    ticket.equipo.estado = 'Activo'
>>>>>>> 3de312f78af9b0228995cc25209007d69c51d132
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
<<<<<<< HEAD
=======
                    if ticket.equipo:
                        ticket.equipo.estado = 'En Reparación'
>>>>>>> 3de312f78af9b0228995cc25209007d69c51d132
                    count += 1
            db.session.commit()
            flash(f"Se han reabierto {count} tickets exitosamente. Vuelven a la cola de trabajo.", "success")
        except Exception as ex:
            flash(f"Error al actualizar tickets: {str(ex)}", "error")
<<<<<<< HEAD
=======
    
>>>>>>> 3de312f78af9b0228995cc25209007d69c51d132

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
<<<<<<< HEAD
=======

    # 7 accion para cambiar el estado de un equipo        
    @action('reparar_equipo', 'Enviar Equipo a Reparación', '¿Cambiar el estado del equipo de este ticket a "En Reparación"?')
    def action_reparar_equipo(self, ids):
        # Seguridad: Solo técnicos y admin pueden tocar el hardware
        if current_user.role not in ['admin', 'tecnico']:
            flash("No tienes permiso para alterar el estado de los equipos.", "error")
            return
        
        try:
            tickets = Ticket.query.filter(Ticket.id.in_(ids)).all()
            count = 0
            for ticket in tickets:
                # Verificamos que el ticket tenga un equipo y no esté ya en reparación
                if ticket.equipo and ticket.equipo.estado != 'En Reparación':
                    ticket.equipo.estado = 'En Reparación'
                    count += 1
            
            db.session.commit()
            flash(f"Se ha cambiado el estado a 'En Reparación' de {count} equipos exitosamente.", "success")
        except Exception as ex:
            flash(f"Error al actualizar el estado del equipo: {str(ex)}", "error")
>>>>>>> 3de312f78af9b0228995cc25209007d69c51d132

# Registro global de vistas
def configuracion_admin():
    
    # Registro Samu
    
    admin.add_view(DepartamentoView(Departamento, db.session, name="Departamentos", category="Personal"))
    admin.add_view(UsuarioView(User, db.session, name="Usuarios", category="Personal"))
    
    # Registro Brayan

    admin.add_view(CategoriaView(Categoria, db.session, name="Categorías", category="Categorias"))
    
    # Registro Jose
    
<<<<<<< HEAD
    admin.add_view(EquipoAdminView(Equipo, db.session, name='Equipos', category='Inventario'))
=======
    admin.add_view(EquipoView(Equipo, db.session, name='Equipos', category='Inventario'))
>>>>>>> 3de312f78af9b0228995cc25209007d69c51d132
    
    # Registro Waldo
    
    admin.add_view(TicketView(Ticket, db.session, name="Gestión de Tickets", category="Soporte"))
    
    pass