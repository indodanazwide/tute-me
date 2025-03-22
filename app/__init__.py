from flask import Flask 
from config import DevelopmentConfig
from .models import db

def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)

    app.config.from_object(config_object)

    db.init_app(app)

    from .routes import router
    app.register_blueprint(router)

    with app.app_context():
        db.create_all()

    return app