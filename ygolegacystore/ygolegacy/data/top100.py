from sqlalchemy import Column, INTEGER, FLOAT, VARCHAR, DATETIME

from ygolegacy.data.modelbase import SqlAlchemyBase


class SoldCard(SqlAlchemyBase):
    __tablename__ = 'ebay_sold_cards'
    id = Column(VARCHAR(255), primary_key=True, index=True)
    set_code = Column(VARCHAR(255), nullable=False, index=True)
    name = Column(VARCHAR(255), nullable=False, index=True)
    sold_date = Column(DATETIME, nullable=False, index=True)
    price = Column(FLOAT, index=True)