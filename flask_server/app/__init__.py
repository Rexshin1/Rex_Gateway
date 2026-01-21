import os 
import config
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_jwt_extended import JWTManager


app = Flask(__name__,template_folder="./views",static_folder="./static")

bcrypt = Bcrypt(app)
app.config.from_object('config')
app.config['SECRET_KEY'] = config.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy()
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'app.login'
jwt = JWTManager(app)



migrate = Migrate(app, db)

# from flask_server.app import views, models
# from .routes import init_routes
# init_routes(app)

def create_app():

    db.init_app(app)
    Migrate(app, db)
    
   

    with app.app_context():
        from .blueprints.web_routes import web_app
        from .blueprints.api_routes import api_app
        app.register_blueprint(web_app)
        app.register_blueprint(api_app)
        # init_routes(app,csrf)
        
    return app