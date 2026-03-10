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


# --- Espacio de Brayan (Categorías de Fallas) ---


# --- Espacio de Jose (Inventario de Equipos) ---


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

# Registro global de vistas
def configuracion_admin():
    
    # Registro Samu
    
    
    # Registro Brayan
    
    
    # Registro Jose
    
    
    # Registro Waldo
    
    admin.add_view(TicketView(Ticket, db.session, name="Gestión de Tickets", category="Soporte"))
    
    pass