from flask import Flask
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
from flask_swagger_ui import get_swaggerui_blueprint


db = SQLAlchemy()
jwt=JWTManager()

def create_app():
    app = Flask(__name__)

    app.config["API_TITLE"] = "Tunisian Book Fair API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.0" 
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TUNISIAN_BOOK_FAIR.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'edo3'
    app.config['FLASK_JWT_SECRET_KEY'] = '5f9605d45bbe9c1fd4e5eca5'
    
    app.config.from_object(Config) 
    db.init_app(app)
    jwt.init_app(app)
    api = Api(app)
    


    
    from webapp.routes.admin import admin_bp
    from webapp.routes.attendees import attendee_bp
    from webapp.routes.author import author_bp

    api.register_blueprint(admin_bp)
    api.register_blueprint(attendee_bp)
    api.register_blueprint(author_bp)

    return app