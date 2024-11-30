import pytest
from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_restframework.serializer.sa_model_serializer import SqlAlchemyModelSerializer


@pytest.fixture(scope="session")
def app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"

    return app

@pytest.fixture(scope="session")
def sa(app):

    db = SQLAlchemy(app)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True)

    db.drop_all()
    db.create_all()

    class Output:
        UserModel = None
        db = None

    Output.UserModel = User
    Output.db = db

    return Output


@pytest.fixture()
def user(sa):
    user = sa.UserModel()

    user.username = "test@test.ru"
    sa.db.session.add(user)
    sa.db.session.commit()

    return user

def test_sqlalchemy_serializer(sa, user):

    class S(SqlAlchemyModelSerializer):
        class Meta:
            model = sa.UserModel

    assert S(sa.UserModel.query.all()).serialize() == [
        {"id": user.id, "username": "test@test.ru"}
    ]


