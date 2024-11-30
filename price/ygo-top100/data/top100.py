from sqlalchemy import Column, INTEGER, FLOAT, VARCHAR, DATETIME

from data.modelbase import SqlAlchemyBase


class SoldCard(SqlAlchemyBase):
    __tablename__ = 'ebay_sold_cards'
    id = Column(VARCHAR(255), primary_key=True)
    set_code = Column(VARCHAR(255), nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    sold_date = Column(DATETIME, nullable=False)
    price = Column(FLOAT, index=True)
    card_id = Column(INTEGER, default=None, nullable=False)
