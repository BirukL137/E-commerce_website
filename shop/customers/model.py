# Import necessary modules
from shop import db, login_manager
from datetime import datetime
from flask_login import UserMixin
import json

# This function is used by Flask-Login to load a user by ID.
@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)


# This is the Register model that represents the user table in the database.
class Register(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(50), unique= False)
    username = db.Column(db.String(50), unique= True)
    email = db.Column(db.String(50), unique= True)
    password = db.Column(db.String(200), unique= False)
    country = db.Column(db.String(50), unique= False)
    city = db.Column(db.String(50), unique= False)
    contact = db.Column(db.String(50), unique= False)
    address = db.Column(db.String(50), unique= False)
    zipcode = db.Column(db.String(50), unique= False)
    profile = db.Column(db.String(200), unique= False, default='profile.jpg')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Define a representation of the model as a string.
    def __repr__(self):
        return '<Register %r>' % self.name


# This is a custom type decorator for JSON-encoded dictionaries.
class JsonEcodedDict(db.TypeDecorator):
    # This decorator uses a Text column type in the database.
    impl = db.Text

    # This method is called when a value is bound to the column.
    def process_bind_param(self, value, dialect):
        # If the value is None, return an empty dictionary as a string.
        if value is None:
            return '{}'
        # Otherwise, JSON-encode the value and return it as a string.
        else:
            return json.dumps(value)

    # This method is called when a value is fetched from the column.
    def process_result_value(self, value, dialect):
        # If the value is None, return an empty dictionary.
        if value is None:
            return {}
        # Otherwise, parse the JSON-encoded string and return the resulting dictionary.
        else:
            return json.loads(value)

# This is the CustomerOrder model that represents the order table in the database.
class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    customer_id = db.Column(db.Integer, unique=False, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Use the custom JSON-encoded dictionary type for the orders column.
    orders = db.Column(JsonEcodedDict)

    # Define a representation of the model as a string.
    def __repr__(self):
        return'<CustomerOrder %r>' % self.invoice


# Create the database tables for all defined models.
db.create_all()
