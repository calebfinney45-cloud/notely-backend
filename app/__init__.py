from flask import Flask
from app.config import Config
from app.extensions import db, migrate, ma, bcrypt, jwt, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})  # tighten this before deploying

    from app.routes.auth import auth_bp
    from app.routes.notes import notes_bp
    from app.routes.users import users_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(users_bp)

    return app