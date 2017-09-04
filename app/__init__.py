from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from config import config
import sharedmodels

# db = SQLAlchemy()
db = sharedmodels.db


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .detect import detect as detect_blueprint
    app.register_blueprint(detect_blueprint)

    from .face import face as face_blueprint
    app.register_blueprint(face_blueprint, url_prefix='/face')

    from .faceset import faceset as faceset_blueprint
    app.register_blueprint(faceset_blueprint, url_prefix='/faceset')

    from .search import search as search_blueprint
    app.register_blueprint(search_blueprint)

    from .compare import compare as compare_blueprint
    app.register_blueprint(compare_blueprint)

    return app
