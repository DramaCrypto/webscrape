from sqlalchemy import and_

from ygolegacy.data.cards import Card
from ygolegacy.data.db_session import DbSession


def __get_price(price):
    return "{:.2f}$".format(price) if price else '---'


def get_card(card_id, edition, condition, set_code):
    cond_edit_id = f"{set_code}_{card_id}_{edition.lower()}_{condition.lower()}".replace(" ", "_").lower()
    print(cond_edit_id)

    s = DbSession.factory()
    card = s.query(Card).filter(Card.cond_edition_id == cond_edit_id) \
        .first()

    s.close()
    if card:
        buy_cad = "{:.2f}$".format(float(card.BUY_CAD_PRICE_75)) if card.BUY_CAD_PRICE_75 else "-"
        buy_usd = "{:.2f}$".format(float(card.BUY_USD_PRICE_75)) if card.BUY_CAD_PRICE_75 else "-"

        return {
            'inventory': card.YGOLEGACY_INVENTORY if card.YGOLEGACY_INVENTORY else 0,
            'ebayca_cad': __get_price(card.EBAYCA_CAD_PRICE),
            'ebayca_usd': __get_price(card.EBAYCA_USD_PRICE),
            'ebaycom_cad': __get_price(card.EBAYCOM_CAD_PRICE),
            'ebaycom_usd': __get_price(card.EBAYCOM_USD_PRICE),
            'tcg_cad': __get_price(card.TCGPLAYER_CAD_PRICE),
            'tcg_usd': __get_price(card.TCGPLAYER_USD_PRICE),
            'buy_cad': buy_cad,
            'buy_usd': buy_usd,
            'id': card.id,
            'msg': 'ok',
            'card_id': card.card_id
        }
