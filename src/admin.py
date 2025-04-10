import os
from flask_admin import Admin
from models import db, User, Planets, People, Favorites_people, Favorites_planets
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, validators


class FavoritePlanetView(ModelView):
    column_list = ('user_id', 'planets_id')
    form_columns = ('user_id', 'planets_id')

class FavoritePeopleView(ModelView):
    column_list = ('user_id', 'people_id')
    form_columns = ('user_id', 'people_id')

class UserForm(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    last_name = StringField('LastName', [validators.DataRequired()])
    email = StringField('Email', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class UserAdmin(ModelView):
    form = UserForm

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')


    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(ModelView(Planets, db.session))
    # admin.add_view(ModelView(Favorites_people, db.session))
    admin.add_view(FavoritePlanetView(Favorites_planets, db.session))
    admin.add_view(FavoritePeopleView(Favorites_people, db.session))
    # admin.add_view(FavoriteView(Favorites, db.session))
    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))