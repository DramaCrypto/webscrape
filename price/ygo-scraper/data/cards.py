from datetime import datetime

from sqlalchemy import Column, INTEGER, TEXT, FLOAT, VARCHAR, DateTime, func, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship

from data.modelbase import SqlAlchemyBase


class CardPriceHistory(SqlAlchemyBase):
    __tablename__ = 'cards_price_history'
    id = Column(INTEGER, primary_key=True, autoincrement=True, index=True)
    card_id = Column(INTEGER, ForeignKey('cards.id'))
    site = Column(VARCHAR(255))
    price_cad = Column(FLOAT)
    price_usd = Column(FLOAT)
    average_low_cad = Column(FLOAT)
    average_high_cad = Column(FLOAT)
    average_low_usd = Column(FLOAT)
    average_high_usd = Column(FLOAT)
    time = Column(DateTime(timezone=True), onupdate=func.now())
    parent_card = relationship("Card", back_populates='history')


class Card(SqlAlchemyBase):
    __tablename__ = 'cards'
    id = Column(INTEGER, primary_key=True, autoincrement=True, index=True)
    card_id = Column(INTEGER)
    name = Column(VARCHAR(200), index=True)
    type = Column(TEXT)
    description = Column(TEXT)
    attribute = Column(TEXT)
    archtype = Column(TEXT)
    race = Column(TEXT)
    ATK = Column(TEXT)
    DEF = Column(TEXT)
    level = Column(TEXT)
    images = Column(TEXT)
    set_name = Column(TEXT)
    set_code = Column(VARCHAR(200), index=True)
    set_rarity = Column(VARCHAR(200), index=True)
    BUY_CAD_PRICE_75 = Column(TEXT)
    BUY_USD_PRICE_75 = Column(TEXT)
    AVG_CAD_PRICE = Column(FLOAT)
    AVG_USD_PRICE = Column(FLOAT)
    EBAYCA_CAD_PRICE = Column(FLOAT)
    EBAYCA_USD_PRICE = Column(FLOAT)
    EBAYCOM_CAD_PRICE = Column(FLOAT)
    EBAYCOM_USD_PRICE = Column(FLOAT)
    TCGPLAYER_CAD_PRICE = Column(FLOAT)
    TCGPLAYER_USD_PRICE = Column(FLOAT)
    YGOLEGACY_INVENTORY = Column(INTEGER)
    edition = Column(VARCHAR(200), index=True)
    condition = Column(VARCHAR(200), index=True)
    edition_id = Column(VARCHAR(200), index=True)
    cond_edition_id = Column(VARCHAR(200), index=True)
    buylist = Column(INTEGER)
    ebayca_url = Column(VARCHAR(255), default=None)
    ebaycom_url = Column(VARCHAR(255), default=None)
    tcg_url = Column(VARCHAR(255), default=None)
    ebayca_results = Column(INTEGER, default=None)
    ebaycom_results = Column(INTEGER, default=None)
    tcg_results = Column(INTEGER, default=None)
    tcg_market_price = Column(FLOAT, default=None)
    last_updated = Column(DateTime, default=None, onupdate=datetime.now)
    ebayca_avg_cad_low = Column(FLOAT, default=None)
    ebayca_avg_cad_high = Column(FLOAT, default=None)
    ebayca_avg_usd_low = Column(FLOAT, default=None)
    ebayca_avg_usd_high = Column(FLOAT, default=None)
    ebaycom_avg_cad_low = Column(FLOAT, default=None)
    ebaycom_avg_cad_high = Column(FLOAT, default=None)
    ebaycom_avg_usd_low = Column(FLOAT, default=None)
    ebaycom_avg_usd_high = Column(FLOAT, default=None)
    tcg_avg_cad_low = Column(FLOAT, default=None)
    tcg_avg_cad_high = Column(FLOAT, default=None)
    tcg_avg_usd_low = Column(FLOAT, default=None)
    tcg_avg_usd_high = Column(FLOAT, default=None)

    tnt_cad_price = Column(FLOAT, default=None)
    tnt_usd_price = Column(FLOAT, default=None)
    tnt_results = Column(INTEGER, default=None)
    tnt_url = Column(VARCHAR(255), default=None)
    tnt_avg_cad_low = Column(FLOAT, default=None)
    tnt_avg_cad_high = Column(FLOAT, default=None)
    tnt_avg_usd_low = Column(FLOAT, default=None)
    tnt_avg_usd_high = Column(FLOAT, default=None)

    ftfg_cad_price = Column(FLOAT, default=None)
    ftfg_usd_price = Column(FLOAT, default=None)
    ftfg_results = Column(INTEGER, default=None)
    ftfg_url = Column(VARCHAR(255), default=None)
    ftfg_avg_cad_low = Column(FLOAT, default=None)
    ftfg_avg_cad_high = Column(FLOAT, default=None)
    ftfg_avg_usd_low = Column(FLOAT, default=None)
    ftfg_avg_usd_high = Column(FLOAT, default=None)

    tcg_market_price_cad = Column(FLOAT, default=None)
    history = relationship("CardPriceHistory", order_by=CardPriceHistory.id, back_populates="parent_card")
    buylist_price = Column(VARCHAR(255))
    ebay_ca_aff_urls = Column(LONGTEXT)
    ebay_com_aff_urls = Column(LONGTEXT)
