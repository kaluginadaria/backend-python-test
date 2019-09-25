from environs import Env
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

env = Env()
Env.read_env(env.str('ENV_PATH', '.env'))

DATABASE_PATH = env.str('DATABASE_PATH')
DATABASE_URI = env.str('DATABASE_URI')
DEBUG = env.bool('DEBUG', default=True)
SECRET_KEY = env.str('SECRET_KEY')

TODOS_PER_PAGE = env.int('TODOS_PER_PAGE', 10)

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)

import alayatodo.views
