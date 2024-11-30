from sqlalchemy import Column, INTEGER, FLOAT, VARCHAR, Boolean

from data.modelbase import SqlAlchemyBase


class EbayPost(SqlAlchemyBase):
    __tablename__ = 'ebay_cards'
    id = Column(INTEGER, primary_key=True)
    posted = Column(Boolean)
    ebay_id = Column(VARCHAR(255))
    price = Column(FLOAT)
    price_value = Column(FLOAT)
    price_type = Column(VARCHAR(255))  # Manual or Auto
    image = Column(VARCHAR(255))
