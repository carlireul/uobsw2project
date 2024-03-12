import os 
from flask import Flask
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tO$&!|0wkamvVia0?n$NqIRVWOG'
csrf = CSRFProtect(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views
from app.models import *


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, Student=Student, Loan=Loan)