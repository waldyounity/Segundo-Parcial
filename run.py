from app._init_ import create_app
from app.extensions import db
from app.models import User

app=create_app()

if __name__ == '__main__':
    with app.app_context():
        #comentamos el creador para que no colisione con la migracion
        # db.create_all()
        if not User.query.filter_by(username='admin').first():
            usuario = User(username='admin', role='admin')
# Usamos tu método que contiene generate_password_hash:
            usuario.set_password('123456')
            
            db.session.add(usuario)
            
            db.session.commit()
    app.run(debug = True)