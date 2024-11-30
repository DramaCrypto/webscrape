from sqlalchemy import Column, INTEGER, FLOAT, VARCHAR, Boolean

from ygolegacy.data.modelbase import SqlAlchemyBase


class EbayPost(SqlAlchemyBase):
    __tablename__ = 'ebay_cards'
    id = Column(INTEGER, primary_key=True, index=True)
    posted = Column(Boolean, index=True)
    ebay_id = Column(VARCHAR(255), index=True)
    price = Column(FLOAT, index=True)
    price_value = Column(FLOAT, index=True)
    price_type = Column(VARCHAR(255), index=True)  # Manual or Auto
    image = Column(VARCHAR(255))
