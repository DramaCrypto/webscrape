# from tqdm import tqdm
#
# from ygolegacy.data.cards import Card
# from ygolegacy.data.db_session import DbSession
#
# DbSession.global_init()
#
# def round_two(num: float) -> str:
#     return "{:.2f}".format(num)
#
#
# def calculate_price_text(price: float) -> str:
#     if price <= 19:
#         return round_two(price * 0.5)
#     elif 19 < price <= 40:
#         return round_two(price * 0.65)
#     elif 40 < price <= 70:
#         return round_two(price * 0.7)
#     elif price > 70:
#         return 'TBD'
#
#
# def update_buylist_table():
#     session = DbSession.factory()
#     cards = session.query(Card).all()
#     for card in tqdm(cards):
#         if card.TCGPLAYER_CAD_PRICE:
#             buy_price = calculate_price_text(card.TCGPLAYER_CAD_PRICE)
#         else:
#             buy_price = None
#         card.buylist_price = buy_price
#     session.commit()
#     session.close()
#
# update_buylist_table()


import os
import pickle
import sys
from ygolegacy.data.cards import Card


def read_pickle(name):
    path = os.path.join('D:\Dev\Projects\WorkProjects\Ygolegacy_projects\count_and_value_updater\data',
                        f'{name}.pickle')
    with open(path, 'rb') as handle:
        return pickle.load(handle)


lst = read_pickle('ebay10')
for l in lst:
    card = Card(**l)
    print(card['id'])
