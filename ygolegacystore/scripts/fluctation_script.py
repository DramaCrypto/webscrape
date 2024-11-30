from tqdm import tqdm
import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from ygolegacy import DbSession
from ygolegacy.data.cards import Card, CardPriceHistory

SENDGRID_API = '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'


def get_ids():
    session = DbSession.factory()
    cards = session.query(Card).filter(Card.condition == 'Near Mint', Card.YGOLEGACY_INVENTORY >= 0).all()
    session.close()
    return cards


def check_price(_id, site):
    session = DbSession.factory()
    prices = session.query(CardPriceHistory).filter(CardPriceHistory.card_id == _id,
                                                    CardPriceHistory.site == site,
                                                    CardPriceHistory.price_cad.isnot(None)). \
        order_by(CardPriceHistory.id.desc()).limit(2).all()
    prices = [x.price_cad for x in prices]
    if len(prices) < 2:
        return False
    price_series = pd.Series(prices)
    prct = price_series.pct_change()
    print(_id, 'price change by {}'.format(prct[1]))
    session.close()
    if prct[1] >= 40:
        return True
    return False


def msg_send(card):
    message = Mail(
        from_email='store@ygolegacy.com',
        to_emails='store@ygolegacy.com',
        subject=f"{card.name} - {card.set_code} - {card.edition} - {card.set_rarity} INCREASE BY 40%+",
        html_content="<div>Press <a href='https://www.ygolegacystore.com/live/ebay/item/{}'>HERE</a> to go to the card !</div>".format(card.id))

    try:
        sg = SendGridAPIClient(SENDGRID_API)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(e.message)
        return False



def main():
    DbSession.global_init()
    cards = get_ids()
    for card in tqdm(cards):
        if check_price(card.id, "Ebay Canada"):
            print('Sending for id: {}'.format(card.id))
            msg_send(card)
        elif check_price(card.id, 'TCGPlayer'):
            print('Sending for id: {}'.format(card.id))
            msg_send(card)
        elif card.id == 3:
            msg_send(card)


if __name__ == '__main__':
    main()
