# This Python code sets up a Flask web application and configures several extensions to work with the app. 

# Import necessary modules
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_msearch import Search
from flask_login import LoginManager
from flask_migrate import Migrate

# Get the absolute path of the directory that contains the current Python file
basedir = os.path.abspath(os.path.dirname(__file__))

# Create a Flask application instance
app = Flask(__name__)

# Configure app settings, including the database URI, a secret key, and a path for uploaded photos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY']='hfouewhfoiwefoquw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')

# Create an UploadSet to handle uploaded photos and configure the app to use it
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

# Initialize a SQLAlchemy database instance and a Bcrypt password hashing instance
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Initialize a Flask-Search instance
search = Search()
search.init_app(app)

# Initialize a Flask-Migrate instance
migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == "sqlite":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

# Initialize a Flask-Login instance to handle user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = u"Please login first"

# Import necessary modules
from shop.products import routes
from shop.admin import routes
from shop.carts import carts
from shop.customers import routes
