import random
import time
from multiprocessing.pool import Pool
from typing import Generator

import cssutils
from pprint import pprint
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from ebaysdk.finding import Connection

from data.cards import Card
from data.db_session import DbSession
from data.top100 import SoldCard

DbSession.global_init()

proxy_ca = 'http://api.buyproxies.org/?a=showProxies&pid=124209&key=91b9fa70313b8c6dff2dc3f98ecf7845&port=12345&country=Canada'
proxy_us = 'http://api.buyproxies.org/?a=showProxies&pid=124209&key=91b9fa70313b8c6dff2dc3f98ecf7845&port=12345&country=US'


def find_sold_card(set_code):
    session = DbSession.factory()
    cards = session.query(Card).filter(Card.set_code == set_code,
                                       Card.condition == "Near Mint")\
        .order_by(Card.TCGPLAYER_CAD_PRICE.desc())

    _id = cards[0].id
    print(set_code, 'ID is', _id)
    return _id


def get_proxies_from_url(url):
    proxies = requests.get(url + '&format=2').text.strip()
    proxies = proxies.split('\n')
    return [x for x in proxies if x.strip()]


PROXIES = get_proxies_from_url(proxy_us)


def get_current_set_codes():
    s = DbSession.factory()
    codes = [x for x in s.query(Card).distinct(Card.set_code).all()]  # .group_by(Card.set_code)
    s.close()
    return codes


api = Connection(config_file='ebay.yaml', debug=False, siteid="EBAY-US")


# t = ['RIRA-EN048', '5DS2-EN030', 'BP01-EN079']
#
# with open('proxies.txt', 'r') as file:
#     PROXIES = file.read().split('\n')


class Scraper:

    @staticmethod
    def make_request(url: str, headers=None, verify=True) -> BeautifulSoup:
        """
        makes HTTP get request
        :param verify:
        :param headers:
        :param url: url to make the request to
        :return: BeautifulSoup object
        """
        headers_ = {
            'authority': 'www.ebay.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'sec-fetch-site': 'none',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            # 'cookie': '__gads=ID=c674c97c5726032b:T=1568479646:S=ALNI_MabTSBP5tiQPDGoNgkh0hWGivh8ZA; aam_uuid=28337971759709071401725015118322143119; DG_IID=DF3CC3A6-D722-35FA-9C1D-7297547DE48D; DG_UID=B9C7CE6B-C692-324A-865E-28AE63667C2F; DG_ZID=CE496D02-2F36-3C17-A22F-9A885FABC922; DG_ZUID=537D0D95-D355-3285-991C-005AFA3F7652; DG_HID=43AE0AB7-7303-3146-A86B-DABAC277A404; DG_SID=83.28.82.21:lSSSytXWO4rFPTq+7j1hPkmCgSzIfBZs5Ioxu2Vpp/c; ak_bmsc=E0B1D7FF5D0D94EA787A3A639BF2779E58DDDD277901000033858B5DB6F2B26C~plAkm2p2fbO8zmMbbfxH+Bi9LYz0tpyo77PcCYWfB02mXBCNLvbfVUXmrkhQvCZtvVAuimlGpMNM0yoTxAHZ509731Q5rQJUm8E/jZMfdFlw41Lucgwv84GDFdCZ4p6xbNWc4qkRPapOWXJSdGSIJtPMp07X1eMwIwtknLJC3mKXUNjvjktnsXSbRLNNgoSJcAV7p+47Oz22+zcgIFzm4xOTBvkAq8UB+sZXq5Dpela3g=; AMCVS_A71B5B5B54F607AB0A4C98A2%40AdobeOrg=1; AMCV_A71B5B5B54F607AB0A4C98A2%40AdobeOrg=-1303530583%7CMCIDTS%7C18165%7CMCMID%7C28371153561892940091728435554731865650%7CMCAAMLH-1570029495%7C6%7CMCAAMB-1570029495%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCCIDH%7C-76443635%7CMCOPTOUT-1569431894s%7CNONE%7CvVersion%7C3.3.0; bm_sv=FA6123DC198B3FFAAB7F89E469E781C1~wQt2RgbFqRMW5ZZcRZcqk/DExMUaqQKLZD/xno03HnnGP0sVAJ9oERBAW7WcDKW5RM0YegdaMzwwhsrhLCj1ecY3br9PCUIJpLTH8zN7RQDogiVbA94UX+2lNkehBjPAT8UP0iRdZPJMfQf4E4gEHUigyPLio9/N2zDzICNwggk=; ns1=BAQAAAW1RHjjoAAaAANgASl9s0DRjNjl8NjAxXjE1Njg0Nzk2NDQ0MTdeXjFeM3wyfDV8NHw3fDExXl5eNF4zXjEyXjEyXjJeMV4xXjBeMV4wXjFeNjQ0MjQ1OTA3NbOYmXVgorUpKOHs05HpW1ZYs716; dp1=bu1p/QEBfX0BAX19AQA**614e03b4^bl/PL614e03b4^pbf/%23e0006000008100020000005f6cd034^; s=CgAD4ACBdjO40MzBhYzBhYzkxNmQwYTllNDJmMWQ3OTYxZmZmNDlmOWLwkBs8; nonsession=BAQAAAW1RHjjoAAaAAAgAHF2zKbQxNTY5MTg1MTUweDEzMzAyMTIxOTk1M3gweDJZADMABl9s0DQwMC04NTQAywABXYujvDgAygAgYU4DtDMwYWMwYWM5MTZkMGE5ZTQyZjFkNzk2MWZmZjQ5ZjliPLuKPuCisbQT6Oau7rgsE9pnQEA*; ebay=%5Ejs%3D1%5Esbf%3D%23%5Epsi%3DAXBWtriQ*%5E; npii=btguid/30ac0ac916d0a9e42f1d7961fff49f9b614e0414^cguid/30ac116916d0a4d12a30d466ca83a3f6614e0414^',
        }
        try:
            response = requests.get(url,
                                    proxies=Scraper.get_random_proxy() if PROXIES else {},
                                    headers=headers if headers else headers_,
                                    verify=verify
                                    )
        except Exception as e:
            print(e, url)
            return Scraper.make_request(url)
        status = response.status_code
        if status == 200:
            return BeautifulSoup(response.text, 'html.parser')
        elif status == 503:
            print(status, url)
            return Scraper.make_request(url)
        print(url, status)

    @staticmethod
    def get_random_proxy():
        p = random.choice(PROXIES)
        return {
            'http': 'http://' + p,
            'https': 'http://' + p
        }


##pprint(response.json(), indent=4)

def get_sold(url):
    # set_code = crd[0]
   # print(url)
    # name = crd[1]
    # url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw={}&_sacat=0&LH_Sold=1&rt=nc'.format(set_code)
    # url = 'https://www.ebay.com/sch/31395/i.html?_from=R40&_nkw={}&LH_Sold=1'.format(set_code)
    soup = Scraper.make_request(url)
    if soup is None:
        return None

    selectors = {}
    for styles in soup.select('style'):
        css = cssutils.parseString(styles.encode_contents())
        for rule in css:
            if rule.type == rule.STYLE_RULE:
                style = rule.selectorText.replace('span.', '')
                selectors[style] = {}
                for item in rule.style:
                    propertyname = item.name
                    value = item.value
                    selectors[style][propertyname] = value

    # results = soup.find('h1', {'class': 'srp-controls__count-heading'})
    # if results:
    #     results = results \
    #         .text.replace('results', '') \
    #         .replace('result', '') \
    #         .replace('ados', '') \
    #         .replace('ado', '') \
    #         .replace(set_code, '') \
    #         .replace('para', '') \
    #         .replace('for', '') \
    #         .strip()
    #     if ' for ' in results:
    #         results = results.split(' for ')[0].strip()
    #     try:
    #         results = int(results)
    #     except Exception as e:
    #         print('error results', url, e)
    #         return
    # else:
    #     results = 0
    # if results == 0:
    #     print('results shows 0', url)
    #     return
    # result_list = soup.find('ul', {'class': 'srp-results'})
    # if not result_list:
    #     print('no result list')
    #     return
    # print('results:', results)
    items = soup.find_all('li', {'class': 's-item'})
    if not items:
        return []
    cards = []
    # s = DbSession.factory()
    for item in items:
        try:
            title = item.find('h3', {'class': 's-item__title'}).text
        except:
            continue
        #print(title)
        x3 = True if '3x' in title else False
        price = item.find('span', {'class': 's-item__price'})
        if not price:
            continue
        price = price.text.strip()
        if 'to' in price:
            # print('to inside')
            continue
        if 'Trending' in price:
            # print('trending inside', price)
            continue

        try:
            price = float(price.replace('$', '').replace(',', ''))
        except ValueError:
            print('cant parse price', price)
            continue

        if x3:
            price = price / 3

        shipping = item.find('span', {'class': 's-item__shipping'})
        if shipping:
            shipping = shipping.text. \
                replace('$', ''). \
                replace('shipping', '')
            try:
                shipping = float(shipping)
            except ValueError:
                shipping = 0
            price += shipping

        link = item.find('a', {'class': 's-item__link'})['href']
        item_id = link[link.rfind('/') + 1:link.find('?')]
        sold_date = item.find('div', {'class': 's-item__title-tag'})

        def check_class(cls):
            if selectors[cls]['display'] == 'none':
                return False
            return True

        # sold_date = ''.join([x.text for x in sold_date if check_class(x['class'][0])])
        sold_date = sold_date.text.strip()
        sold_date = sold_date.replace('SOLD', '').strip()
        sold_date = datetime.strptime(sold_date, "%b %d, %Y")
        match = match_set_code(title)
        if not match:
            continue
        set_code, name = match

        card = SoldCard(id=item_id,
                        set_code=set_code,
                        name=name,
                        sold_date=sold_date,
                        price=price,
                        card_id=find_sold_card(set_code))
        cards.append(card)
    return cards
    #     s.add(card)
    #     try:
    #         s.commit()
    #     except:
    #         continue
    #
    # s.close()


def match_set_code(title):
    match = [set_code[0] for set_code in set_codes if set_code[0].lower() in title.lower()]
 #   print(match)
    if match:
        return match[0], set_codes_dict[match[0]]
    else:
        return None


# def get_sold_api(set_code, name):
#     request = {
#         'keywords': set_code,
#         'itemFilter': [
#             {'name': 'SoldItemsOnly', 'value': True}
#         ],
#         'paginationInput': {
#             'entriesPerPage': 100,
#             'pageNumber': 1
#         },
#         'sortOrder': 'PricePlusShippingLowest'
#     }
#
#     response = api.execute('findCompletedItems', request)
#     items = response.reply.searchResult
#     if items._count == "0":
#         items = []
#     else:
#         items = items.item
#     # if len(items) == 10:
#     #     print('next page')
#     s = DbSession.factory()
#     for item in items:
#         price = item.sellingStatus.currentPrice.value
#         # print(item.itemId)
#         # print(item.listingInfo.endTime)
#         card = SoldCard(id=item.itemId,
#                         set_code=set_code,
#                         name=name,
#                         sold_date=item.listingInfo.endTime,
#                         price=price)
#         yield card
#         s.add(card)
#         try:
#             s.commit()
#         except:
#             continue
#     s.close()


def chunks(lst: list, chunk_size: int) -> Generator:
    """ Yield n-sized chunks from lst """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


set_codes = list(set([(x.set_code, x.name) for x in get_current_set_codes() if x.set_code]))
set_codes_dict = {}
for x in set_codes:
    set_codes_dict[x[0]] = x[1]


def main():
    # https://www.ebay.com/b/Individual-Yu-Gi-Oh-Cards/31395/bn_1890424?rt=nc&LH_Sold=1
    # set_codes = list(set([(x.set_code, x.name) for x in get_current_set_codes()]))
    # # print(set_codes[0], set_codes[1])
    # # print(len(set_codes))
    # #exit()
    # chunks_lst = list(chunks(set_codes, 100))
    # for card_lst in tqdm(chunks_lst):
    #
    #     session = DbSession.factory()
    #     with Pool(8) as p:
    #         results = tqdm(p.imap(get_sold, card_lst), total=len(card_lst))
    #         for lst in results:
    #             if lst:
    #                 for result in lst:
    #                     session.add(result)
    #                     try:
    #                         session.commit()
    #                     except:
    #                         continue
    #     session.close()
    #
    #     time.sleep(7)

    # for page in range(359, 2000):
    #     session = DbSession.factory()
    #     print(page)
    #     results = get_sold('https://www.ebay.com/b/Individual-Yu-Gi-Oh-Cards/31395/bn_1890424?LH_Sold=1&rt=nc&_pgn={}&_sop=13'.format(page))
    #     for result in results:
    #         session.add(result)
    #         try:
    #             session.commit()
    #         except:
    #             continue
    #
    #     session.close()
    #     print('added')

    ###################
    session = DbSession.factory()
    results = get_sold(
        'https://www.ebay.com/b/Individual-Yu-Gi-Oh-Cards/31395/bn_1890424?LH_Sold=1&rt=nc&_pgn=1&_sop=13')
    for result in results:
        session.add(result)
        try:
            session.commit()
        except:
            continue

    session.close()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(120)
    # for card in card_lst:
    #     code = card.set_code
    #     if code:
    #         get_sold(code, card.name)
    #         time.sleep(10)

# for card in get_current_set_codes():
#     code = card.set_code
#     if code:
#         get_sold(code, card.name)
#         time.sleep(10)
