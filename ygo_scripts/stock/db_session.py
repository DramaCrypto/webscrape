import sqlalchemy
import sqlalchemy.orm

from data.cards import Card
from data.modelbase import SqlAlchemyBase
from config import DATABASE_URI


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
