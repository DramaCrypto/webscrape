from sqlalchemy import Column, VARCHAR, Integer

from data.modelbase import SqlAlchemyBase


class CardSet(SqlAlchemyBase):
    __tablename__ = 'card_sets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255))
    type_of_set = Column(VARCHAR(255))
    edition = Column(VARCHAR(255))
    set_code = Column(VARCHAR(255))
    picture_name = Column(VARCHAR(255))