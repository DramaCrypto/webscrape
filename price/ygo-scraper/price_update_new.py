import re
import sys
import time
from multiprocessing.pool import Pool
from typing import Generator, Optional
from datetime import datetime

import schedule
from forex_python.converter import CurrencyRates
from sqlalchemy import and_, or_, func
from tqdm import tqdm
from data.ebay_listing import EbayPost

import ebay_api_services
from data.cards import Card, CardPriceHistory
from data.db_session import DbSession
from scrapers.ebay import EbayCA, EbayUS
from scrapers.facetoface import FaceToFace
from scrapers.tcgplayer import TCGPlayer
from scrapers.trollntoad import TrollAndToad

CONDITION = Card.condition == 'Near Mint'
NM = 'nm'

def get_exchange_rate(crr: str, to_currency: str) -> float:
    c = CurrencyRates()
    return c.get_rate(crr, to_currency)

global CAD_USD, USD_CAD
CAD_USD = get_exchange_rate('CAD', 'USD')
USD_CAD = get_exchange_rate('USD', 'CAD')


def update_price(main_filter: range):
    """ Update prices for selected group of cards.
    """
    chunks_lst = list(chunks(list(main_filter), 200))
    for idx, chunk in tqdm(enumerate(chunks_lst), total=len(chunks_lst)):
        session = Session()
        chunk_data = session.query(Card).filter(CONDITION,
                                                Card.id.in_(range(chunk[0], chunk[-1]))).all()

        ids = {}
        with Pool(16) as p:
            results = p.imap(run_parsers, chunk_data)
            for result in results:
                if result:
                    ids[result['id']] = result

        temp_index = 0
        for d in chunk_data:
            temp_index = temp_index + 1
            print('index ', temp_index)

            try:
                d_data = ids[d.id]
            except KeyError:
                continue
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
                session.add(history)

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
                session.add(history)

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
                session.add(history)

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
                session.add(history)

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
                session.add(history)

            other_conditions = session.query(Card).filter(and_(Card.edition_id == d.edition_id,
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

            session.commit()

        # for card in tqdm(chunk_data):
        #     result = run_parsers(card)
        #     if result:
        #         ids[result['id']] = result

        session.close()

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

def run_parsers(card: Card) -> Optional[dict]:
    data = {'id': card.id}
    if card:

        ebay_ca = EbayCA()
        ebay_com = EbayUS()
        tcg_player = TCGPlayer()
        troll_and_toad = TrollAndToad()
        face_to_face = FaceToFace()

        code = card.set_code
        if not code:
            return None
        rarity = card.set_rarity
        if not rarity:
            return None
        # skip codes starting with IGAS
        # if code.startswith('IGAS'):
        #     return None

        # create edition strings for search queries
        if card.edition == "1st Edition":
            edition = " 1st"
        elif card.edition == "Unlimited":
            edition = ' '
        elif not card.edition:
            return None
        else:
            edition = card.edition

        # EBAY
        ebay_query = create_ebay_query(card)
        price_ebay_ca = ebay_ca.find_lowest(ebay_query)
        if not price_ebay_ca:
            price_ebay_ca = ebay_ca.find_lowest(code)
        ebay_ca_url = ebay_ca.url
        ebay_ca_results = ebay_ca.results

        price_ebay_com = ebay_com.find_lowest(ebay_query)
        if not price_ebay_com:
            price_ebay_com = ebay_com.find_lowest(code)
        ebay_com_url = ebay_com.url
        ebay_com_results = ebay_com.results

        # TCG
        price_tcg_player = tcg_player.find_lowest(code, card.edition, card.condition, card.set_rarity)
        tcg_url = tcg_player.url
        tcg_results = tcg_player.results
        data['tcg_market_price'] = tcg_player.market_price
        data['tcg_market_price_cad'] = tcg_player.market_price * USD_CAD if tcg_player.market_price else None

        # TNT
        price_tnt = troll_and_toad.find_lowest(card.set_code if card.edition == "Limited Edition" else card.set_code)
        tnt_url = troll_and_toad.url
        tnt_results = troll_and_toad.results

        # FtF
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
        if price_ebay_com:
            data['EBAYCOM_USD_PRICE'] = price_ebay_com
            price_ebay_us_cad = float(price_ebay_com) * USD_CAD
            data['EBAYCOM_CAD_PRICE'] = price_ebay_us_cad

            data['ebaycom_avg_cad_low'] = ebay_com.low
            data['ebaycom_avg_usd_low'] = ebay_com.low * CAD_USD
            data['ebaycom_avg_cad_high'] = ebay_com.high
            data['ebaycom_avg_usd_high'] = ebay_com.high * CAD_USD
            data['ebay_com_aff_urls'] = ebay_com.urls
            usd_avg.append(price_ebay_com)
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
    return data


def create_ebay_query(card):
    code = card.set_code
    rarity = card.set_rarity
    if code.startswith('DT'):
        return code

    if card.edition == "1st Edition":
        edition = " 1st"
    elif card.edition == "Unlimited":
        edition = ' '
    elif 'limited' in card.edition.lower():
        edition = 'limited'
    else:
        edition = card.edition


    if 'secret' in rarity.lower():
        rarity_query = 'Secret -prismatic'
    elif 'ultra' in rarity.lower():
        rarity_query = 'ultra'
    elif 'super' in rarity.lower():
        rarity_query = 'super'
    elif rarity.lower() == 'rare':
        rarity_query = 'rare -prismatic -secret -ultra -super'
    elif 'common' in rarity.lower():
        rarity_query = ''
    else:
        rarity_query = rarity

    if card.edition == "Unlimited":
        rarity_edition = '-1st'
    else:
        rarity_edition = edition

    if 'prismatic' in rarity.lower():
        rarity_query = 'Prismatic -secret'

    ebay_query = f"{code} {rarity_query} {rarity_edition}".strip()
    ebay_query = re.sub(' +', ' ', ebay_query)
    return ebay_query

def round_price(price: float) -> float:
    """ Create Sell price.
    """
    if .01 <= price <= .50:
        price = .25
    elif .51 <= price <= .99:
        price = .95
    else:
        price = float(int(price)) + .95
    return price


def read_arguments() -> int:
    """ Read command line arguments,
    or return default one if no argument.
    """
    try:
        arg = int(sys.argv[1])
    except ValueError:
        raise ValueError("Argument has to be an integer from 1 to 4")
    except IndexError:
        arg = 0

    if arg not in range(0, 5):
        raise ValueError('Integer has to be from 0 to 4')
    return arg


def chunks(lst: list, chunk_size: int) -> Generator:
    """ Yield n-sized chunks from lst """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def job():
    filters = {
        # 1: (CONDITION, Card.id.in_(range(1, 40000))),
        # 2: (CONDITION, Card.id.in_(range(40000, 80000))),
        # 3: (CONDITION, Card.id.in_(range(80000, 120000))),
        # 4: (CONDITION, Card.id.in_(range(120000, 160000)))
        1: range(1, 40000),
        2: range(40000, 80000),
        3: range(80000, 120000),
        4: range(120000, 160000)
    }
    selected_filter = filters[read_arguments()]
    try:
        update_price(selected_filter)
    except:
        pass

if __name__ == '__main__':
    DbSession.global_init()
    Session = DbSession.factory
    schedule.every().day.at("01:00").do(job)
    schedule.every().day.at("04:00").do(job)
    schedule.every().day.at("07:00").do(job)
    schedule.every().day.at("10:00").do(job)
    schedule.every().day.at("13:00").do(job)
    schedule.every().day.at("17:00").do(job)
    schedule.every().day.at("20:00").do(job)
    schedule.every().day.at("23:00").do(job)
    job()
    while 1:
        schedule.run_pending()
        time.sleep(1)
