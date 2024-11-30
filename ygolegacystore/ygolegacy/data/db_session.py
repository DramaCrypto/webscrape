import json

import sqlalchemy
import sqlalchemy.orm

from ygolegacy.data.cards import Card
from ygolegacy.data.modelbase import SqlAlchemyBase
# noinspection PyUnresolvedReferences
import ygolegacy.data.__all_models
from ygolegacy.db_config import DATABASE_URI


class DbSession:
    factory = None
    engine = None
    card_data = None

    @staticmethod
    def global_init():
        if DbSession.factory:
            return

        conn_str = DATABASE_URI
        print("Connecting to DB at: {}".format(conn_str))

        engine = sqlalchemy.create_engine(conn_str, echo=False)
        DbSession.engine = engine
        DbSession.factory = sqlalchemy.orm.sessionmaker(bind=engine)

        SqlAlchemyBase.metadata.create_all(engine)
