from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. TABLA DEPARTAMENTOS (Samu) ---
class Departamento(db.Model):
    __tablename__ = 'departamentos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    edificio_piso = db.Column(db.String(100))
    
    usuarios = db.relationship('User', backref='departamento', lazy=True)
    
    def __str__(self):
        return self.nombre

# --- 2. TABLA USUARIOS (Samu) ---
class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), default="empleado")
    
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=True) 
    tickets = db.relationship('Ticket', backref='creador', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __str__(self):
        return self.username

# --- 3. TABLA CATEGORÍAS (Brayan) ---
class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    nivel_gravedad = db.Column(db.String(20), default="Media") 
    tiempo_estimado_horas = db.Column(db.Integer, default=24) 
    
    tickets = db.relationship('Ticket', backref='categoria', lazy=True)
    
    def __str__(self):
        return self.nombre

# --- 4. TABLA EQUIPOS (Jose) ---
class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    numero_serie = db.Column(db.String(50), unique=True, nullable=False)
    estado = db.Column(db.String(20), default='Activo')
    
    tickets = db.relationship('Ticket', backref='equipo', lazy=True)

    def __str__(self):
        return f"{self.nombre} ({self.numero_serie})"

# --- 5. TABLA TICKETS (Waldo) ---
class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(50), default='Pendiente')
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)