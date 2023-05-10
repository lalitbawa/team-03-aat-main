from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '<insert your secret key here>'

# suppress SQLAlchemy warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')

# EXAMPLE:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c123456:MySQLPassword@csmysql.cs.cf.ac.uk:3306/my_blog_db'
# WHERE:
# 'c123456' is your username (Student Number with leading 'c');
# 'MySQLPassword' is your MySQL password, NOT your University password! These two passwords SHOULD be different for security reasons. Use https://dbmanager.cs.cf.ac.uk/ to manage your passwords
# 'my_blog_db' is the name of your MySQL database

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from AATApp.models import User, Questions
from AATApp.views import AdminView

admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Questions, db.session))

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

from AATApp.routes import projectroutes, assessmentroutes, questionsroutes