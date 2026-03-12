import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from config import config
from .extensions import db, login_manager, admin, migrate
from app.admin import configuracion_admin

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    admin.init_app(app)
    
    configuracion_admin()
    
    # Registramos el blueprint una sola vez
    from .auth import auth_bp    
    app.register_blueprint(auth_bp)
    
    # Registramos el nuevo blueprint de Inteligencia Artificial
    from .ia_routes import ia_bp
    app.register_blueprint(ia_bp)
    
    return app