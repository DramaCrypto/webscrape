import concurrent
import re
import sys
import time
from datetime import datetime
from multiprocessing.pool import Pool
from typing import Generator

from sqlalchemy import and_, or_, func
from forex_python.converter import CurrencyRates

import ebay_api_services
from data.cards import Card, CardPriceHistory
from data.ebay_listing import EbayPost
from scrapers.ebay import EbayCA, EbayUS
from scrapers.facetoface import FaceToFace
from scrapers.tcgplayer import TCGPlayer
from tqdm import tqdm
from data.db_session import DbSession

from scrapers.trollntoad import TrollAndToad


def get_exchange_rate(crr: str, to_currency: str):
    c = CurrencyRates()
    return c.get_rate(crr, to_currency)


global CAD_USD, USD_CAD
CAD_USD = get_exchange_rate('CAD', 'USD')
USD_CAD = get_exchange_rate('USD', 'CAD')


def chunks(lst: list, chunk_size: int) -> Generator:
    """ Yield n-sized chunks from lst """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def match_ebay_posting(_id):
    session = Session()
    card = session.query(EbayPost).filter(EbayPost.id == _id).first()
    if not card:
        card = EbayPost(id=_id, posted=False)
        session.add(card)
        session.commit()
        card = session.query(EbayPost).filter(EbayPost.id == _id).first()
    session.close()
    return card


def parse(card):
    # s = Session()
    # card = s.query(Card).filter(row.id == Card.id).first()
    data = {'id': card.id}
    if card:
        code = card.set_code
        if code.lower().startswith('igas'):
            return None
        if code:
            if card.edition == "1st Edition":
                edition = " 1st"
            elif card.edition == "Unlimited":
                edition = ' '
            else:
                edition = card.edition
            if edition:
                condition = {
                    'Near Mint': 'nm',
                    'Slightly Played': 'sp',
                    'Moderately Played': 'mp',
                    'Heavily Played': 'hp'
                }[card.condition]

                query = code + " " + edition
                # if code in ["NECH-EN054", 'LEHD-ENA04']:
                #     query = query.strip() + " " + card.set_rarity
                #  query = query.strip() + " " + condition
                query = query.strip()

                rarity = card.set_rarity

                query = re.sub(' +', ' ', query + " " + rarity)

                # Handle dual terminal
                if card.set_code.startswith('DT'):
                    query = card.set_code

                if card.set_rarity == "Rare":
                    query += " -prismatic -Secret Rare -Ultra Rare -Ultimate Rare -Ghost Rare -Gold Rare -Super Rare"
                elif card.set_rarity == "Secret Rare":
                    query += " -prismatic"
                if card.edition == "Unlimited":
                    query += " -1st"

                if 'prismatic' in rarity.lower():
                    query = "{} {} {}".format(card.set_code, edition, 'prismatic')
                    query = re.sub(' +', ' ', query + " " + rarity)

                ebay_ca = EbayCA()



                price_ebay_ca = ebay_ca.find_lowest(card.set_code if card.edition == "Limited Edition" else query)
                # if not price_ebay_ca:
                #     price_ebay_ca = ebay_ca.find_lowest(code)
                ebay_ca_url = ebay_ca.url
                ebay_ca_results = ebay_ca.results

                ebay_us = EbayUS()
                price_ebay_us = ebay_us.find_lowest(card.set_code if card.edition == "Limited Edition" else query)
                # if not price_ebay_us:
                #     price_ebay_us = ebay_us.find_lowest(code)
                ebay_com_url = ebay_us.url
                ebay_com_results = ebay_us.results

                tcg_player = TCGPlayer()
                price_tcg_player = tcg_player.find_lowest(code, card.edition, card.condition, card.set_rarity)
                tcg_url = tcg_player.url
                tcg_results = tcg_player.results
                data['tcg_market_price'] = tcg_player.market_price
                data['tcg_market_price_cad'] = tcg_player.market_price * USD_CAD if tcg_player.market_price else None

                troll_and_toad = TrollAndToad()
                # price_tnt = troll_and_toad.find_lowest(
                #     code + " " + card.edition if 'limited edition' not in card.edition.lower() else code)
                price_tnt = troll_and_toad.find_lowest(card.set_code if card.edition == "Limited Edition" else query)
                tnt_url = troll_and_toad.url
                tnt_results = troll_and_toad.results

                face_to_face = FaceToFace()
                price_ftfg = face_to_face.find_lowest(code + " " + card.edition + " " + card.set_rarity)
                ftfg_url = face_to_face.url
                ftfg_results = face_to_face.results

                data['last_updated'] = datetime.now()

                cad_avg = []
                usd_avg = []

                data['ebayca_url'] = ebay_ca_url
                data['ebayca_results'] = ebay_ca_results
                data['ebaycom_url'] = ebay_com_url
                data['ebaycom_results'] = ebay_com_results
                data['tcg_url'] = tcg_url
                data['tcg_results'] = tcg_results

                if price_ebay_ca:
                    data['EBAYCA_CAD_PRICE'] = price_ebay_ca
                    price_ebay_ca_usd = float(price_ebay_ca) * CAD_USD
                    data['EBAYCA_USD_PRICE'] = price_ebay_ca_usd

                    data['ebayca_avg_cad_low'] = ebay_ca.low
                    data['ebayca_avg_usd_low'] = ebay_ca.low * CAD_USD
                    data['ebayca_avg_cad_high'] = ebay_ca.high
                    data['ebayca_avg_usd_high'] = ebay_ca.high * CAD_USD
                    usd_avg.append(price_ebay_ca_usd)
                    cad_avg.append(price_ebay_ca)
                    data['ebay_ca_aff_urls'] = ebay_ca.urls
                if price_ebay_us:
                    data['EBAYCOM_USD_PRICE'] = price_ebay_us
                    price_ebay_us_cad = float(price_ebay_us) * USD_CAD
                    data['EBAYCOM_CAD_PRICE'] = price_ebay_us_cad

                    data['ebaycom_avg_cad_low'] = ebay_us.low
                    data['ebaycom_avg_usd_low'] = ebay_us.low * CAD_USD
                    data['ebaycom_avg_cad_high'] = ebay_us.high
                    data['ebaycom_avg_usd_high'] = ebay_us.high * CAD_USD
                    data['ebay_com_aff_urls'] = ebay_us.urls
                    usd_avg.append(price_ebay_us)
                    cad_avg.append(price_ebay_us_cad)
                if price_tcg_player:
                    data['TCGPLAYER_USD_PRICE'] = price_tcg_player
                    price_tcg_player_cad = float(price_tcg_player) * USD_CAD
                    data['TCGPLAYER_CAD_PRICE'] = price_tcg_player_cad

                    data['tcg_avg_cad_low'] = tcg_player.low
                    data['tcg_avg_usd_low'] = tcg_player.low * CAD_USD
                    data['tcg_avg_cad_high'] = tcg_player.high
                    data['tcg_avg_usd_high'] = tcg_player.high * CAD_USD
                    usd_avg.append(price_tcg_player)
                    cad_avg.append(price_tcg_player_cad)

                data['tnt_url'] = tnt_url
                data['tnt_results'] = tnt_results
                if price_tnt:
                    data['tnt_usd_price'] = price_tnt
                    price_tnt_cad = float(price_tnt) * USD_CAD
                    data['tnt_cad_price'] = price_tnt_cad

                    data['tnt_avg_usd_low'] = troll_and_toad.low
                    data['tnt_avg_cad_low'] = troll_and_toad.low * USD_CAD
                    data['tnt_avg_usd_high'] = troll_and_toad.high
                    data['tnt_avg_cad_high'] = troll_and_toad.high * USD_CAD

                    usd_avg.append(price_tnt)
                    cad_avg.append(price_tnt_cad)

                data['ftfg_url'] = ftfg_url
                data['ftfg_results'] = ftfg_results
                if price_ftfg:
                    data['ftfg_cad_price'] = price_ftfg
                    price_ftfg_usd = float(price_ftfg) * CAD_USD
                    data['ftfg_usd_price'] = price_ftfg_usd

                    data['ftfg_avg_cad_low'] = face_to_face.low
                    data['ftfg_avg_usd_low'] = face_to_face.low * CAD_USD
                    data['ftfg_avg_cad_high'] = face_to_face.high
                    data['ftfg_avg_usd_high'] = face_to_face.high * CAD_USD

                    usd_avg.append(price_ftfg_usd)
                    cad_avg.append(price_ftfg)

                data['AVG_CAD_PRICE'] = sum([float(x) for x in cad_avg]) / len(cad_avg) if cad_avg else None
                data['AVG_USD_PRICE'] = sum([float(x) for x in usd_avg]) / len(usd_avg) if usd_avg else None
                data['USD_TO_CAD_EXCHANGE_RATE'] = USD_CAD
    # pprint(data, indent=4)
    return data


def round_two(num: float) -> str:
    return "{:.2f}".format(num)


def calculate_price_text(price: float) -> str:
    if not price:
        return ''
    if price <= 19:
        return round_two(price * 0.5)
    elif 19 < price <= 40:
        return round_two(price * 0.65)
    elif 40 < price <= 70:
        return round_two(price * 0.7)
    elif price > 70:
        return 'TBD'


def round_price(price):
    if .01 <= price <= .50:
        price = .25
    elif .51 <= price <= .99:
        price = .95
    else:
        price = float(int(price)) + .95
    return price

def main():
    # session = Session()
    # data = session.query(Card).filter(Card.condition == "Near Mint").all()
    # print(len(data))
    # session.close()

    s = Session()
    data = s.query(Card).filter(*FILTER).all()

    chunks_lst = list(chunks(data, 1000))
    s.close()
    for idx, chunk in tqdm(enumerate(chunks_lst), total=len(chunks_lst)):
        s = Session()
        data = s.query(Card).filter(*FILTER).all()

        chunks_lst = list(chunks(data, 1000))
        start = time.time()
        try:
            chunk = chunks_lst[idx]
        except:
            print('continue!!!!!!!!!!!!')
            continue


       # test_lst = [] # FOR TESTING PURPOSES
        ids = {}
        with Pool(8) as p:
            results = tqdm(p.imap(parse, chunk), total=len(chunk))
            for result in results:
                if result:
                #test_lst.append(result)  # TESTING
                    ids[result['id']] = result

        # # TESTING #
        # import pandas as pd
        # df = pd.DataFrame(test_lst)
        # df.to_csv('prices.csv')
        # # TESTING END #
        for d in chunk:

            d_data = ids[d.id]
            d.tcg_market_price = float(d_data.get('tcg_market_price')) if d_data.get(
                'tcg_market_price') else None
            d.tcg_market_price_cad = float(d_data.get('tcg_market_price_cad')) if d_data.get(
                'tcg_market_price_cad') else None
            d.EBAYCA_CAD_PRICE = d_data.get('EBAYCA_CAD_PRICE')
            d.EBAYCA_USD_PRICE = d_data.get('EBAYCA_USD_PRICE')
            d.EBAYCOM_USD_PRICE = d_data.get('EBAYCOM_USD_PRICE')
            d.EBAYCOM_CAD_PRICE = d_data.get('EBAYCOM_CAD_PRICE')
            d.TCGPLAYER_USD_PRICE = d_data.get('TCGPLAYER_USD_PRICE')
            d.TCGPLAYER_CAD_PRICE = d_data.get('TCGPLAYER_CAD_PRICE')
            d.tnt_usd_price = d_data.get('tnt_usd_price')
            d.tnt_cad_price = d_data.get('tnt_cad_price')
            d.ftfg_usd_price = d_data.get('ftfg_usd_price')
            d.ftfg_cad_price = d_data.get('ftfg_cad_price')

            d.ebayca_avg_cad_low = d_data.get('ebayca_avg_cad_low')
            d.ebayca_avg_cad_high = d_data.get('ebayca_avg_cad_high')
            d.ebayca_avg_usd_low = d_data.get('ebayca_avg_usd_low')
            d.ebayca_avg_usd_high = d_data.get('ebayca_avg_usd_high')

            d.ebaycom_avg_cad_low = d_data.get('ebaycom_avg_cad_low')
            d.ebaycom_avg_cad_high = d_data.get('ebaycom_avg_cad_high')
            d.ebaycom_avg_usd_low = d_data.get('ebaycom_avg_usd_low')
            d.ebaycom_avg_usd_high = d_data.get('ebaycom_avg_usd_high')

            d.tcg_avg_cad_low = d_data.get('tcg_avg_cad_low')
            d.tcg_avg_cad_high = d_data.get('tcg_avg_cad_high')
            d.tcg_avg_usd_low = d_data.get('tcg_avg_usd_low')
            d.tcg_avg_usd_high = d_data.get('tcg_avg_usd_high')

            d.tnt_avg_cad_low = d_data.get('tnt_avg_cad_low')
            d.tnt_avg_cad_high = d_data.get('tnt_avg_cad_high')
            d.tnt_avg_usd_low = d_data.get('tnt_avg_usd_low')
            d.tnt_avg_usd_high = d_data.get('tnt_avg_usd_high')

            d.ftfg_avg_cad_low = d_data.get('ftfg_avg_cad_low')
            d.ftfg_avg_cad_high = d_data.get('ftfg_avg_cad_high')
            d.ftfg_avg_usd_low = d_data.get('ftfg_avg_usd_low')
            d.ftfg_avg_usd_high = d_data.get('ftfg_avg_usd_high')

            d.AVG_CAD_PRICE = d_data.get('AVG_CAD_PRICE')
            d.AVG_USD_PRICE = d_data.get('AVG_USD_PRICE')
            d.ebayca_url = d_data.get('ebayca_url')
            d.ebaycom_url = d_data.get('ebaycom_url')
            d.tcg_url = d_data.get('tcg_url')
            d.tnt_url = d_data.get('tnt_url')
            d.ftfg_url = d_data.get('ftfg_url')
            d.ebayca_results = d_data.get('ebayca_results')
            d.ebaycom_results = d_data.get('ebaycom_results')
            d.tcg_results = d_data.get('tcg_results')
            d.tnt_results = d_data.get('tnt_results')
            d.ftfg_results = d_data.get('ftfg_results')

            d.ebay_ca_aff_urls = d_data.get('ebay_ca_aff_urls')
            d.ebay_com_aff_urls = d_data.get('ebay_com_aff_urls')

            if d.TCGPLAYER_CAD_PRICE:
                d.BUY_CAD_PRICE_75 = round_price(d.TCGPLAYER_CAD_PRICE * .6)
            if d.TCGPLAYER_USD_PRICE:
                d.BUY_USD_PRICE_75 = round_price(d.TCGPLAYER_USD_PRICE * .6)

            if d.YGOLEGACY_INVENTORY and d.YGOLEGACY_INVENTORY > 0:
                ebay_posting = match_ebay_posting(d.id)
                if ebay_posting and ebay_posting.posted:
                    cond_dict = {
                        'Near Mint': 'NM',
                        'Moderately Played': "MP",
                        'Slightly Played': 'SP',
                        'Heavily Played': 'HP'
                    }
                    if '1st' in d.edition:
                        title = f"Yugioh {d.name} {d.set_rarity} 1st {d.set_code} {cond_dict[d.condition]}"
                    else:
                        title = f"Yugioh {d.name} {d.set_rarity} {d.set_code} {cond_dict[d.condition]}"
                    title = title.replace('&', "and")
                    title = title[:70]  # Shorten to 70 char title limit
                    if ebay_posting.price_type == 'Auto' and d.EBAYCA_CAD_PRICE:
                        new_price = d.EBAYCA_CAD_PRICE * ebay_posting.price_value
                        ebay_api_services.update_item(ebay_posting.ebay_id, title, new_price, ebay_posting.image,
                                                      str(d.YGOLEGACY_INVENTORY))
                        ebay_posting.posted = True
                        ebay_posting.price = new_price

            # d.buylist_price = calculate_price_text(d.TCGPLAYER_CAD_PRICE)

            history = CardPriceHistory(card_id=d.id,
                                       site='Ebay US',
                                       price_cad=d.EBAYCOM_CAD_PRICE,
                                       price_usd=d.EBAYCOM_USD_PRICE,
                                       average_low_cad=d.ebaycom_avg_cad_low,
                                       average_high_cad=d.ebaycom_avg_cad_high,
                                       average_low_usd=d.ebaycom_avg_usd_low,
                                       average_high_usd=d.ebaycom_avg_usd_high,
                                       time=func.now()
                                       )
            if not all(not x for x in [history.price_cad, history.price_usd, history.average_low_cad,
                                       history.average_high_cad, history.average_low_usd,
                                       history.average_high_usd]):
                s.add(history)

            history = CardPriceHistory(card_id=d.id,
                                       site='Ebay Canada',
                                       price_cad=d.EBAYCOM_CAD_PRICE,
                                       price_usd=d.EBAYCOM_USD_PRICE,
                                       average_low_cad=d.ebayca_avg_cad_low,
                                       average_high_cad=d.ebayca_avg_cad_high,
                                       average_low_usd=d.ebayca_avg_usd_low,
                                       average_high_usd=d.ebayca_avg_usd_high,
                                       time=func.now()
                                       )
            if not all(not x for x in [history.price_cad, history.price_usd, history.average_low_cad,
                                       history.average_high_cad, history.average_low_usd,
                                       history.average_high_usd]):
                s.add(history)

            history = CardPriceHistory(card_id=d.id,
                                       site='TCGPlayer',
                                       price_cad=d.TCGPLAYER_CAD_PRICE,
                                       price_usd=d.TCGPLAYER_USD_PRICE,
                                       average_low_cad=d.tcg_avg_cad_low,
                                       average_high_cad=d.tcg_avg_cad_high,
                                       average_low_usd=d.tcg_avg_usd_low,
                                       average_high_usd=d.tcg_avg_usd_high,
                                       time=func.now()
                                       )
            if not all(not x for x in [history.price_cad, history.price_usd, history.average_low_cad,
                                       history.average_high_cad, history.average_low_usd,
                                       history.average_high_usd]):
                s.add(history)

            history = CardPriceHistory(card_id=d.id,
                                       site='Troll and Toad',
                                       price_cad=d.tnt_cad_price,
                                       price_usd=d.tnt_usd_price,
                                       average_low_cad=d.tnt_avg_cad_low,
                                       average_high_cad=d.tnt_avg_cad_high,
                                       average_low_usd=d.tnt_avg_usd_low,
                                       average_high_usd=d.tnt_avg_usd_high,
                                       time=func.now()
                                       )
            if not all(not x for x in [history.price_cad, history.price_usd, history.average_low_cad,
                                       history.average_high_cad, history.average_low_usd,
                                       history.average_high_usd]):
                s.add(history)

            history = CardPriceHistory(card_id=d.id,
                                       site='Face to Face',
                                       price_cad=d.ftfg_cad_price,
                                       price_usd=d.ftfg_usd_price,
                                       average_low_cad=d.ftfg_avg_cad_low,
                                       average_high_cad=d.ftfg_avg_cad_high,
                                       average_low_usd=d.ftfg_avg_usd_low,
                                       average_high_usd=d.ftfg_avg_usd_high,
                                       time=func.now()
                                       )
            if not all(not x for x in [history.price_cad, history.price_usd, history.average_low_cad,
                                       history.average_high_cad, history.average_low_usd,
                                       history.average_high_usd]):
                s.add(history)

            other_conditions = s.query(Card).filter(and_(Card.edition_id == d.edition_id,
                                                         Card.condition != "Near Mint",
                                                         Card.set_rarity == d.set_rarity))

            for cond in other_conditions:

                condition = {
                    'Slightly Played': 0.85,
                    'Moderately Played': 0.65,
                    'Heavily Played': 0.45
                }[cond.condition]

                cond.EBAYCA_CAD_PRICE = d_data.get('EBAYCA_CAD_PRICE') * condition if d_data.get(
                    'EBAYCA_CAD_PRICE') else None
                cond.EBAYCA_USD_PRICE = d_data.get('EBAYCA_USD_PRICE') * condition if d_data.get(
                    'EBAYCA_USD_PRICE') else None
                cond.EBAYCOM_USD_PRICE = d_data.get('EBAYCOM_USD_PRICE') * condition if d_data.get(
                    'EBAYCOM_USD_PRICE') else None
                cond.EBAYCOM_CAD_PRICE = d_data.get('EBAYCOM_CAD_PRICE') * condition if d_data.get(
                    'EBAYCOM_CAD_PRICE') else None

                cond.TCGPLAYER_USD_PRICE = float(d_data.get('TCGPLAYER_USD_PRICE')) * condition if d_data.get(
                    'TCGPLAYER_USD_PRICE') else None
                cond.TCGPLAYER_CAD_PRICE = float(d_data.get('TCGPLAYER_CAD_PRICE')) * condition if d_data.get(
                    'TCGPLAYER_CAD_PRICE') else None

                cond.tnt_usd_price = float(d_data.get('tnt_usd_price')) * condition if d_data.get(
                    'tnt_usd_price') else None
                cond.tnt_cad_price = float(d_data.get('tnt_cad_price')) * condition if d_data.get(
                    'tnt_cad_price') else None
                cond.ftfg_usd_price = float(d_data.get('ftfg_usd_price')) * condition if d_data.get(
                    'ftfg_usd_price') else None
                cond.ftfg_cad_price = float(d_data.get('ftfg_cad_price')) * condition if d_data.get(
                    'ftfg_cad_price') else None

                cond.tcg_market_price = float(d_data.get('tcg_market_price')) * condition if d_data.get(
                    'tcg_market_price') else None
                cond.tcg_market_price_cad = float(d_data.get('tcg_market_price_cad')) * condition if d_data.get(
                    'tcg_market_price_cad') else None

                cond.ebayca_avg_cad_low = d_data.get('ebayca_avg_cad_low') * condition if d_data.get(
                    'ebayca_avg_cad_low') else None
                cond.ebayca_avg_cad_high = d_data.get('ebayca_avg_cad_high') * condition if d_data.get(
                    'ebayca_avg_cad_high') else None
                cond.ebayca_avg_usd_low = d_data.get('ebayca_avg_usd_low') * condition if d_data.get(
                    'ebayca_avg_usd_low') else None
                cond.ebayca_avg_usd_high = d_data.get('ebayca_avg_usd_high') * condition if d_data.get(
                    'ebayca_avg_usd_high') else None

                cond.ebaycom_avg_cad_low = d_data.get('ebaycom_avg_cad_low') * condition if d_data.get(
                    'ebaycom_avg_cad_low') else None
                cond.ebaycom_avg_cad_high = d_data.get('ebaycom_avg_cad_high') * condition if d_data.get(
                    'ebaycom_avg_cad_high') else None
                cond.ebaycom_avg_usd_low = d_data.get('ebaycom_avg_usd_low') * condition if d_data.get(
                    'ebaycom_avg_usd_low') else None
                cond.ebaycom_avg_usd_high = d_data.get('ebaycom_avg_usd_high') * condition if d_data.get(
                    'ebaycom_avg_usd_high') else None

                cond.tcg_avg_cad_low = d_data.get('tcg_avg_cad_low') * condition if d_data.get(
                    'tcg_avg_cad_low') else None
                cond.tcg_avg_cad_high = d_data.get('tcg_avg_cad_high') * condition if d_data.get(
                    'tcg_avg_cad_high') else None
                cond.tcg_avg_usd_low = d_data.get('tcg_avg_usd_low') * condition if d_data.get(
                    'tcg_avg_usd_low') else None
                cond.tcg_avg_usd_high = d_data.get('tcg_avg_usd_high') * condition if d_data.get(
                    'tcg_avg_usd_high') else None

                cond.tnt_avg_cad_low = d_data.get('tnt_avg_cad_low') * condition if d_data.get(
                    'tnt_avg_cad_low') else None
                cond.tnt_avg_cad_high = d_data.get('tnt_avg_cad_high') * condition if d_data.get(
                    'tnt_avg_cad_high') else None
                cond.tnt_avg_usd_low = d_data.get('tnt_avg_usd_low') * condition if d_data.get(
                    'tnt_avg_usd_low') else None
                cond.tnt_avg_usd_high = d_data.get('tnt_avg_usd_high') * condition if d_data.get(
                    'tnt_avg_usd_high') else None

                cond.ftfg_avg_cad_low = d_data.get('ftfg_avg_cad_low') * condition if d_data.get(
                    'ftfg_avg_cad_low') else None
                cond.ftfg_avg_cad_high = d_data.get('ftfg_avg_cad_high') * condition if d_data.get(
                    'ftfg_avg_cad_high') else None
                cond.ftfg_avg_usd_low = d_data.get('ftfg_avg_usd_low') * condition if d_data.get(
                    'ftfg_avg_usd_low') else None
                cond.ftfg_avg_usd_high = d_data.get('ftfg_avg_usd_high') * condition if d_data.get(
                    'ftfg_avg_usd_high') else None
                # cond.last_updated = datetime.now()

                cond.ebay_ca_aff_urls = d_data.get('ebay_ca_aff_urls')
                cond.ebay_com_aff_urls = d_data.get('ebay_com_aff_urls')

                cond.AVG_CAD_PRICE = d_data.get('AVG_CAD_PRICE') * condition if d_data.get('AVG_CAD_PRICE') else None
                cond.AVG_USD_PRICE = d_data.get('AVG_USD_PRICE') * condition if d_data.get('AVG_USD_PRICE') else None

                cond.ebayca_url = d_data.get('ebayca_url')
                cond.ebaycom_url = d_data.get('ebaycom_url')
                cond.tcg_url = d_data.get('tcg_url')
                cond.tnt_url = d_data.get('tnt_url')
                cond.ftfg_url = d_data.get('ftfg_url')
                cond.ebayca_results = d_data.get('ebayca_results')
                cond.ebaycom_results = d_data.get('ebaycom_results')
                cond.tcg_results = d_data.get('tcg_results')
                cond.tnt_results = d_data.get('tnt_results')
                cond.ftfg_results = d_data.get('ftfg_results')

                # cond.buylist_price = calculate_price_text(d.TCGPLAYER_CAD_PRICE)

                if cond.AVG_CAD_PRICE:
                    cond.BUY_CAD_PRICE_75 = cond.AVG_CAD_PRICE * .6
                if d.AVG_USD_PRICE:
                    cond.BUY_USD_PRICE_75 = cond.AVG_USD_PRICE * .6

                if d.YGOLEGACY_INVENTORY and d.YGOLEGACY_INVENTORY > 0:
                    ebay_posting = match_ebay_posting(d.id)
                    if ebay_posting and ebay_posting.posted:
                        cond_dict = {
                            'Near Mint': 'NM',
                            'Moderately Played': "MP",
                            'Slightly Played': 'SP',
                            'Heavily Played': 'HP'
                        }
                        if '1st' in d.edition:
                            title = f"Yugioh {d.name} {d.set_rarity} 1st {d.set_code} {cond_dict[d.condition]}"
                        else:
                            title = f"Yugioh {d.name} {d.set_rarity} {d.set_code} {cond_dict[d.condition]}"
                        title = title.replace('&', "and")
                        title = title[:70]  # Shorten to 70 char title limit
                        if ebay_posting.price_type == 'Auto' and d.EBAYCA_CAD_PRICE:
                            new_price = d.EBAYCA_CAD_PRICE * ebay_posting.price_value
                            ebay_api_services.update_item(ebay_posting.ebay_id, title, new_price, ebay_posting.image,
                                                          str(d.YGOLEGACY_INVENTORY))
                            ebay_posting.posted = True
                            ebay_posting.price = new_price

            s.commit()
        s.close()
        elasped = time.time() - start

    s.close()




# data = s.query(Card).filter().all()
if __name__ == "__main__":
    main_filters = {
        '0': (Card.condition == 'Near Mint', Card.set_code.startswith('IGAS')),
        'none': (Card.condition == "Near Mint", Card.tnt_cad_price.is_(None)),
        "1": (Card.condition == "Near Mint", Card.AVG_CAD_PRICE <= 1.5),
        "2": (Card.condition == "Near Mint", and_(Card.AVG_CAD_PRICE > 1.5, Card.AVG_CAD_PRICE <= 2.5)),
        "3": (Card.condition == "Near Mint", and_(Card.AVG_CAD_PRICE > 2.5, Card.AVG_CAD_PRICE <= 5)),
        "4": (Card.condition == "Near Mint", and_(Card.AVG_CAD_PRICE > 5, Card.AVG_CAD_PRICE <= 15)),
        "5": (Card.condition == "Near Mint", Card.AVG_CAD_PRICE >= 15),
        'x': (Card.id == 2391, Card.condition == 'Near Mint')
    }
    try:
        arg = sys.argv[1]
    except IndexError:
        arg = 'none'
    FILTER = main_filters[arg]
    DbSession.global_init()
    Session = DbSession.factory
    while True:
        main()
        time.sleep(5)
