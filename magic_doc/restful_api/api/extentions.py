from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask_migrate import Migrate
from contextlib import contextmanager
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            db.session.commit()
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            raise e


app = Flask(__name__)
CORS(app, supports_credentials=True)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()