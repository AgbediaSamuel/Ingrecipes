# Database code 
# I ended up using an external Database tool regardless but it maintains the definitions below
#I would not include it in the gitignore just for reference
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    recipes = db.relationship('saved_recipe', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash =  generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class saved_recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_title = db.Column(db.String(200), nullable=False)
    recipe_url = db.Column(db.String(300), nullable=False)

