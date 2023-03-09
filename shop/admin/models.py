# Import necessary modules
from shop import db
from datetime import datetime

# Define User model class that inherits from db.Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(180), unique=False, nullable=False)
    profile = db.Column(db.String(180), unique=False, nullable=False, default='profile.jpg')

    # Define a representation function for the user model
    def __repr__(self):
        return '<User %r>' % self.username

# Create database tables
db.create_all()
