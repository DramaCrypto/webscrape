import concurrent
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing.pool import Pool
from pprint import pprint
from typing import Generator

from multiprocessing import cpu_count

import requests
from sqlalchemy.orm import sessionmaker
from forex_python.converter import CurrencyRates
from tqdm import tqdm

from db import *
import pandas as pd
from tqdm import tqdm

# TODO read rows from db instead of CSV
Session = sessionmaker(bind=engine)
#csv_updater = CsvDB('YGO_DB.csv')

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


def parse(row):
    new = row.copy()
    code = row['Set_code']
    if code:
        pass
        # ebay_ca = EbayCA()
        # price_ebay_ca = ebay_ca.find_lowest(code)
        # ebay_us = EbayUS()
        # price_ebay_us = ebay_us.find_lowest(code)
        # tcg_player = TCGPlayer()
        # price_tcg_player = tcg_player.find_lowest(code)
        # cad_avg = []
        # usd_avg = []
        #
        # if price_ebay_ca:
        #     new['EBAY.CA_CAD_PRICE'] = price_ebay_ca
        #     price_ebay_ca_usd = float(price_ebay_ca) * CAD_USD
        #     new['EBAY.CA_USD_PRICE'] = price_ebay_ca_usd
        #     usd_avg.append(price_ebay_ca_usd)
        #     cad_avg.append(price_ebay_ca)
        # if price_ebay_us:
        #     new['EBAY.COM_USD_PRICE'] = price_ebay_us
        #     price_ebay_us_cad = float(price_ebay_us) * USD_CAD
        #     new['EBAY.COM_CAD_PRICE'] = price_ebay_us_cad
        #     usd_avg.append(price_ebay_us)
        #     cad_avg.append(price_ebay_us_cad)
        # if price_tcg_player:
        #     new['TCGPLAYER_USD_PRICE'] = price_tcg_player
        #     price_tcg_player_cad = float(price_tcg_player) * USD_CAD
        #     new['TCGPLAYER_CAD_PRICE'] = price_tcg_player_cad
        #     usd_avg.append(price_tcg_player)
        #     cad_avg.append(price_tcg_player_cad)
        #
        # new['AVG_CAD_PRICE'] = sum([float(x) for x in cad_avg]) / len(cad_avg) if cad_avg else None
        # new['AVG_USD_PRICE'] = sum([float(x) for x in usd_avg]) / len(usd_avg) if usd_avg else None
    card_id = new['CARD ID']
    edition_id = "{}_{}_{}".format(new['Set_code'], card_id, new['edition'].lower()).replace(' ', '_')
    cond_edition_id = "{}_{}".format(edition_id, new['condition'].lower()).replace(' ', '_')
    card = Card(card_id=card_id,
                name=new['NAME'],
                type=new['TYPE'],
                description=new['Description'],
                attribute=new['Attribute'],
                archtype=new['Archtype'],
                race=new['Race'],
                ATK=new['ATK'],
                DEF=new['DEF'],
                level=new['Level'],
                images=new['Images'],
                set_name=new['Set_Name'],
                set_code=new['Set_code'],
                set_rarity=new['Set Rarity'],
                edition=new['edition'],
                condition=new['condition'],
                edition_id=edition_id,
                cond_edition_id=cond_edition_id)
    # s = Session()
    # s.add(card)
    # s.commit()
    # s.close()
    # TODO Update listing
    return card


# for chunk in chunks(data, 2000):
#     start = time.time()
#     s = Session()
#     with Pool(cpu_count()) as p:
#         result = list(tqdm(p.imap(parse, chunk), total=len(chunk)))
#         for r in result:
#             s.add(r)
#         try:
#             s.commit()
#         except:
#             continue
#     s.close()
#     print(time.time() - start)
#

def main():

    #data = csv_updater.data
    import pandas as pd

    df = pd.read_excel('new.xlsx')
    df = df.where((pd.notnull(df)), None)
    data = df.to_dict('records')

    # UPDATE COLUMN
    # csv_data = {}
    # for i, d in enumerate(data, 1):
    #     csv_data[i] = d

    # s = Session()
    # data = s.query(Card).all()
    # for d in tqdm(data):
    #     if d.AVG_CAD_PRICE:
    #         d.BUY_CAD_PRICE_75 = d.AVG_CAD_PRICE * .6
    #     if d.AVG_USD_PRICE:
    #         d.BUY_USD_PRICE_75 = d.AVG_USD_PRICE * .6
    # s.commit()
    # s.close()
    #
    # exit()

    s = Session()
    for chunk in chunks(data, 1000):
        for row in tqdm(chunk):
            s.add(parse(row))
        s.commit()
    s.close()
    exit()

    chunks_lst = list(chunks(data, 800))
    for idx, chunk in tqdm(enumerate(chunks_lst, 1), total=len(chunks_lst)):
        # print(f"{idx}/{len(chunks_lst)}")
        s = Session()
        start = time.time()

        with Pool(32) as p:
            result = tqdm(p.imap(parse, chunk), total=len(chunk))
            for r in result:
                s.add(r)

        # with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
        #     futures = []
        #     for row in chunk:
        #         futures.append(executor.submit(parse, row))
        #     for future in concurrent.futures.as_completed(futures):
        #         pass  # write to file here
        #         s.add(future.result())
        s.commit()
        elasped = time.time() - start
        print(elasped)
        s.close()


if __name__ == "__main__":
    main()

# https://towardsdatascience.com/implementing-auto-complete-with-postgres-and-python-e03d34824079
