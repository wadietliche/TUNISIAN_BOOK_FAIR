from flask import Flask
from flask_smorest import Api


def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "Tunisian Book Fair API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.0"

    api = Api(app)
    app.config['SECRET_KEY'] = 'edo3'

    from webapp.routes.attendees import user_bp 

    
    api.register_blueprint(user_bp)
    
    return app