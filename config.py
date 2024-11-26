# import os, pymysql

# BASE_DIR = os.path.dirname(__file__)

# SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'todo.db'))
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
    'root', 'root', 'localhost', '3306', 'todo'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "dev"
