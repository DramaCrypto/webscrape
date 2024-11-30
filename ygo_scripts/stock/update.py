import json
import os
import pickle
import time
from pprint import pprint
from typing import List

import schedule
from sqlalchemy import and_, or_

from __orders import *
from config import PATH
from data.cards import Card
from data.db_session import DbSession
from sqlalchemy.ext.declarative import DeclarativeMeta


class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


def _set_up(currency: str = None):
    session = DbSession.factory()
    all_cards = session.query(Card).all()
    session.close()
    rarities = list(set([x.set_rarity for x in all_cards]))
    types = list(set([x.type for x in all_cards]))
    races = list(set([x.race for x in all_cards]))

    total = None
    if currency:
        if currency == "USD":
            total = [x.TCGPLAYER_USD_PRICE for x in all_cards
                     if
                     x.TCGPLAYER_USD_PRICE is not None and x.TCGPLAYER_USD_PRICE > 0 and x.YGOLEGACY_INVENTORY and x.YGOLEGACY_INVENTORY > 0]
        elif currency == "CAD":
            total = [x.TCGPLAYER_CAD_PRICE for x in all_cards
                     if
                     x.TCGPLAYER_CAD_PRICE is not None and x.TCGPLAYER_CAD_PRICE > 0 and x.YGOLEGACY_INVENTORY and x.YGOLEGACY_INVENTORY > 0]
    else:
        total = [x.YGOLEGACY_INVENTORY for x in all_cards
                 if x.YGOLEGACY_INVENTORY is not None and x.YGOLEGACY_INVENTORY > 0]
    if total:
        total = int(sum(total))
    else:
        total = 0
    return rarities, types, races, all_cards, {
        'total': total,
        'rarity_ordered': {},
        'rarity': {},
        'types': {},
        'types_ordered': {},
        'races': {},
        'races_ordered': {},
        'spell': {},
        'spell_ordered': {},
        'trap': {},
        'trap_ordered': {},
        'skill': {},
        'skill_ordered': {}
    }


def round_price(price):
    if .01 <= price <= .50:
        price = .25
    elif .51 <= price <= .99:
        price = .95
    else:
        price = float(int(price)) + .95
    return price


def update_row(main_dict, main_dict_key, column, card_, currency=None):
    if main_dict_key == 'rarity':
        if column in ['Ghost Rare', 'Ghost/Gold Rare']:
            column = 'Ghost Rare'
        elif column in ['Ultra Secret Rare', 'Ultra Rare']:
            column = 'Ultra Rare'
        elif column in ['Gold Rare', 'Gold Secret Rare']:
            column = 'Gold Rare'
        elif column in ['Common', 'Common ']:
            column = 'Common'
    if currency:
        if currency == 'USD' and card_.TCGPLAYER_USD_PRICE and card_.YGOLEGACY_INVENTORY:
            main_dict[main_dict_key][column] += round_price(card_.TCGPLAYER_USD_PRICE * card_.YGOLEGACY_INVENTORY)
        elif currency == 'CAD' and card_.TCGPLAYER_CAD_PRICE and card_.YGOLEGACY_INVENTORY:
            main_dict[main_dict_key][column] += round_price(card_.TCGPLAYER_CAD_PRICE * card_.YGOLEGACY_INVENTORY)
        # if currency == "USD" and card_.AVG_USD_PRICE and card_.YGOLEGACY_INVENTORY:
        #     main_dict[main_dict_key][column] += card_.AVG_USD_PRICE * card_.YGOLEGACY_INVENTORY
        # elif currency == "CAD" and card_.AVG_CAD_PRICE and card_.YGOLEGACY_INVENTORY:
        #     main_dict[main_dict_key][column] += card_.AVG_CAD_PRICE * card_.YGOLEGACY_INVENTORY
    else:
        if card_.YGOLEGACY_INVENTORY:
            main_dict[main_dict_key][column] += card_.YGOLEGACY_INVENTORY
    return main_dict


def update_values(main_dict, main_dict_key: str, all_cards, db_column_list, db_column: str, order_list: list,
                  currency=None, second_var=None, second_var_value=None):
    # print(db_column_list)
    # exit()
    for column in db_column_list:
        if column:
            main_dict[main_dict_key][column] = 0
    for column in db_column_list:
        if column:
            if second_var:
                [main_dict.update(update_row(main_dict, main_dict_key, column, card_, currency)) for card_ in all_cards
                 if
                 getattr(card_, db_column) == column and getattr(card_, second_var) == second_var_value]
            else:
                [main_dict.update(update_row(main_dict, main_dict_key, column, card_, currency)) for card_ in all_cards
                 if
                 getattr(card_, db_column) == column]

    [main_dict[f'{main_dict_key}_ordered'].update({x: main_dict[main_dict_key][x]}) for x in order_list]
    for column in db_column_list:
        if column:
            main_dict[f'{main_dict_key}_ordered'][column] = f"{int(main_dict[main_dict_key][column])}"
    return main_dict


def get_stock():
    rarities, types, races, all_cards, stock = _set_up()
    #
    # for key, lst in [('rarity', rarities), ('types', types),
    #                  ('races', races), ('spell', SPELLS_ORDER),
    #                  ('trap', TRAPS_ORDER), ('skill', SKILL_ORDER)]:
    #     for l in lst:
    #         stock[key][l] = 0
    #
    # for card_ in all_cards:
    #     for rarity in rarities:
    #         if card_.set_rarity == rarity:
    #             if rarity in ['Ghost Rare', 'Ghost/Gold Rare']:
    #                 rarity = 'Ghost Rare'
    #             elif rarity in ['Ultra Secret Rare', 'Ultra Rare']:
    #                 rarity = 'Ultra Rare'
    #             elif rarity in ['Gold Rare', 'Gold Secret Rare']:
    #                 rarity = 'Gold Rare'
    #             elif rarity in ['Common', 'Common ']:
    #                 rarity = 'Common'
    #             if card_.YGOLEGACY_INVENTORY:
    #                 if rarity in stock['rarity'].keys():
    #                     stock['rarity'][rarity] += card_.YGOLEGACY_INVENTORY
    #                 else:
    #                     stock['rarity'][rarity] = card_.YGOLEGACY_INVENTORY
    #             break
    #
    #     for card_type in types:
    #         if card_.type == card_type:
    #             if card_.YGOLEGACY_INVENTORY:
    #                 if card_type in stock['types'].keys():
    #                     stock['types'][card_type] += card_.YGOLEGACY_INVENTORY
    #                 else:
    #                     stock['types'][card_type] = card_.YGOLEGACY_INVENTORY
    #             break
    #
    #     for race in races:
    #         if card_.race == race:
    #             if card_.YGOLEGACY_INVENTORY:
    #                 if race in stock['races'].keys():
    #                     stock['races'][race] += card_.YGOLEGACY_INVENTORY
    #                 else:
    #                     stock['races'][race] = card_.YGOLEGACY_INVENTORY
    #             break
    #
    #     for spell in SPELLS_ORDER:
    #         if card_.race == spell and card_.type == 'Spell Card':
    #             if card_.YGOLEGACY_INVENTORY:
    #                 if spell in stock['spell'].keys():
    #                     stock['spell'][spell] += card_.YGOLEGACY_INVENTORY
    #                 else:
    #                     stock['spell'][spell] = card_.YGOLEGACY_INVENTORY
    #             break
    #
    #     for trap in TRAPS_ORDER:
    #         if card_.race == trap and card_.type == 'Trap Card':
    #             if card_.YGOLEGACY_INVENTORY:
    #                 if trap in stock['trap'].keys():
    #                     stock['trap'][trap] += card_.YGOLEGACY_INVENTORY
    #                 else:
    #                     stock['trap'][trap] = card_.YGOLEGACY_INVENTORY
    #             break
    #
    #     for skill in SKILL_ORDER:
    #         if card_.race == skill and card_.type == 'Skill Card':
    #             if card_.YGOLEGACY_INVENTORY:
    #                 if skill in stock['skill'].keys():
    #                     stock['skill'][skill] += card_.YGOLEGACY_INVENTORY
    #                 else:
    #                     stock['skill'][skill] = card_.YGOLEGACY_INVENTORY
    #             break
    # for key, order in [('rarity', RARITY_ORDER), ('types', TYPES_ORDER),
    #                    ('races', RACES_ORDER), ('spell', SPELLS_ORDER),
    #                    ('trap', TRAPS_ORDER), ('skill', SKILL_ORDER)]:
    #     [stock[f'{key}_ordered'].update({x: stock[key][x]}) for x in order]
    #
    # return stock

    stock = update_values(stock, 'rarity', all_cards, rarities, 'set_rarity', RARITY_ORDER)
    stock = update_values(stock, 'types', all_cards, types, 'type', TYPES_ORDER)
    stock = update_values(stock, 'races', all_cards, races, 'race', RACES_ORDER)
    stock = update_values(stock, 'spell', all_cards, SPELLS_ORDER, 'race', SPELLS_ORDER,
                          second_var='type',
                          second_var_value='Spell Card')
    stock = update_values(stock, 'trap', all_cards, TRAPS_ORDER, 'race', TRAPS_ORDER,
                          second_var='type',
                          second_var_value='Trap Card')
    stock = update_values(stock, 'skill', all_cards, SKILL_ORDER, 'race', SKILL_ORDER,
                          second_var='type',
                          second_var_value='Skill Card')

    return stock


def get_value(currency):
    rarities, types, races, all_cards, stock = _set_up()
    stock['total'] = 0

    stock = update_values(stock, 'rarity', all_cards, rarities, 'set_rarity', RARITY_ORDER, currency)

    stock = update_values(stock, 'types', all_cards, types, 'type', TYPES_ORDER, currency)
    stock = update_values(stock, 'races', all_cards, races, 'race', RACES_ORDER, currency)
    stock = update_values(stock, 'spell', all_cards, SPELLS_ORDER, 'race', SPELLS_ORDER,
                          currency=currency,
                          second_var='type',
                          second_var_value='Spell Card')
    stock = update_values(stock, 'trap', all_cards, TRAPS_ORDER, 'race', TRAPS_ORDER,
                          currency=currency,
                          second_var='type',
                          second_var_value='Trap Card')
    stock = update_values(stock, 'skill', all_cards, SKILL_ORDER, 'race', SKILL_ORDER,
                          currency=currency,
                          second_var='type',
                          second_var_value='Skill Card')
    for key, value in stock['rarity_ordered'].items():
        stock['total'] += int(value)

    return stock


def save_to_pickle(name, data):
    path = os.path.join(PATH, f'{name}.pickle')
    with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(f'{path} saved')


def update_pages():
    result_list: List[Card] = get_above_10_avg(True)
    results = []
    for result in result_list:
        result = result.__dict__
        del result['_sa_instance_state']
        results.append(result)
    save_to_pickle('ebay10', results)

    stock = get_value('USD')
    save_to_pickle('value_usd', stock)

    stock = get_value('CAD')
    save_to_pickle('value_cad', stock)

    stock = get_stock()
    save_to_pickle('stock', stock)


def get_above_10_avg(below=False):
    session = DbSession.factory()
    all_above_10 = session.query(Card) \
        .filter(
        and_(
            Card.YGOLEGACY_INVENTORY > 0,
            or_(Card.TCGPLAYER_CAD_PRICE < 10 if below else Card.TCGPLAYER_CAD_PRICE >= 10,
                Card.TCGPLAYER_CAD_PRICE is None))).all()
    session.close()

    return all_above_10


if __name__ == '__main__':
    while True:
        DbSession.global_init()
        update_pages()
        time.sleep(180 * 60)
