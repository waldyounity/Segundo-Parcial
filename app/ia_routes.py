import os
from groq import Groq
from flask import Blueprint, request, jsonify
from flask_login import current_user # Para saber el nivel de acceso
from dotenv import load_dotenv
from .models import Categoria, db, Ticket, Equipo, User 

# --- APORTE DE WALDO ---
load_dotenv()
ia_bp = Blueprint('ia_bp', __name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@ia_bp.route('/api/chat', methods=['POST'])
def chat_bot():
    data = request.json
    mensaje_usuario = data.get('mensaje')
    if not mensaje_usuario:
        return jsonify({'respuesta': 'Por favor, ingresa una consulta.'}), 400

    try:
        # 1. OBTENER DATOS REALES DE LA BD
        tickets_all = Ticket.query.all()
        
        # Estructuramos una lista técnica para la IA
        detalle_tickets = ""
        for t in tickets_all:
            detalle_tickets += f"- Ticket #{t.id}: [{t.estado}] {t.titulo} | Usuario: {t.creador.username} | Equipo: {t.equipo.nombre}\n  Desc: {t.descripcion[:100]}...\n"

        # 2. DEFINIR LA PERSONALIDAD SEGÚN EL ROL
        rol_usuario = current_user.role if current_user.is_authenticated else "Invitado"
        
        system_prompt = f"""
        Eres el Ingeniero de Soporte IA del sistema Helpdesk IT. 
        USUARIO ACTUAL: {current_user.username if current_user.is_authenticated else 'Desconocido'} (Rol: {rol_usuario}).
        
        BASE DE DATOS EN TIEMPO REAL:
        {detalle_tickets}

        REGLAS DE RESPUESTA:
        - Si el usuario es 'admin' o 'tecnico', DA DETALLES COMPLETOS (IDs, nombres de equipos, problemas específicos).
        - Si el usuario es 'empleado', sé amable y solo dale un resumen general de sus solicitudes.
        - Usa **negritas** para resaltar estados y nombres.
        - Usa listas y saltos de línea para que la información sea fácil de leer.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje_usuario}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5
        )
        return jsonify({'respuesta': chat_completion.choices[0].message.content})
    except Exception as e:
        print(f"ERROR IA WALDO: {e}")
        return jsonify({'respuesta': "Error: El sistema de datos no está disponible."}), 500

# --- APORTE DE JOSE ---

@ia_bp.route('/api/analizar_dashboard', methods=['GET'])
def analizar_dashboard():
    try:
    # Obtenemos solo los tickets pendientes para el análisis de riesgos
        pendientes = Ticket.query.filter_by(estado='Pendiente').all()
        lista_pendientes = "\n".join([f"- {p.titulo}: {p.descripcion[:50]}" for p in pendientes])
        prompt = f"""
        Actúa como un Auditor IT Senior. Analiza estos tickets PENDIENTES:
        {lista_pendientes}
        Genera un informe con:
        1. **Resumen de Crisis**: (¿Hay problemas críticos acumulados?)
        2. **Impacto en el Negocio**: (¿Qué se está deteniendo?)
        3. **Plan de Priorización**: (Dime qué ticket ID debo atender PRIMERO y por qué).
        """
        completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        )
        return jsonify({'analisis': completion.choices[0].message.content})
    except Exception as e:
        return jsonify({'analisis': "No se pudo realizar el análisis técnico."}), 500
# La ruta de estadísticas se mantiene igual
@ia_bp.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    try:
        # 1. Datos de Tickets (Waldo)
        pendientes = Ticket.query.filter_by(estado='Pendiente').count()
        cerrados = Ticket.query.filter(Ticket.estado != 'Pendiente').count()
        # 2. Datos de Categorías (Brayan)
        categorias = Categoria.query.all()
        cat_labels = [c.nombre for c in categorias]
        cat_data = [Ticket.query.filter_by(categoria_id=c.id).count() for c in categorias]
        # 3. Datos de Equipos (Jose)
        activos = Equipo.query.filter_by(estado='Activo').count()
        mantenimiento = Equipo.query.filter_by(estado='En Reparación').count()
        return jsonify({
        'abiertos': pendientes,
        'cerrados': cerrados,
        'cat_labels': cat_labels,
        'cat_data': cat_data,
        'equipos_stats': [activos, mantenimiento]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
