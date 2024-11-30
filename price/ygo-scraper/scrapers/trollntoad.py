from typing import Optional

import requests
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper


class TrollAndToad(Scraper):
    """ Trollandtoad.com scraper class """

    def find_lowest(self, code: str) -> Optional[float]:
        url = f'https://www.trollandtoad.com/category.php?min-price=&max-price=&items-pp=60&item-condition=NM&search-words={code.lower().replace(" ", "+")}&selected-cat=4736'
        self.url = url
        soup = self.make_request(url, query=code.lower())
        if not soup:
            return None
        error = soup.find('div', {'class': 'text-danger font-italic'})
        if error and error.text == 'No exact matches found in this category.':
       #    print('No results for', code)
            self.results = 0
            return None

        error2 = soup.find('div', {'class': 'font-weight-bold text-center'})
        if error2:
            pass
            #print(error2.text.strip())

        card = soup.find('div', {'class': 'product-col'})
        if card is None:
       #     print('cand find card')
            return None
        options = card.find('div', {'class': 'buying-options-table'})
        prices = []
        for opt in options.find_all('div', {'class': 'row'})[1:]:
            price_str = opt.find('div', {'class': 'col-2 text-center p-1'}).text
            price = float(price_str.replace('$', '').replace(',', ''))
            prices.append(price)

        if prices:
          #  print(prices)
            avg, low, high = self.tmean(prices)
            self.results = len(prices)
            self.low = low
            self.high = high
    #    print('no prices')


    @staticmethod
    def make_request(url: str, headers=None, verify=True, canada=False, query=None) -> BeautifulSoup:
        """ make requet for tnt.
        """
        proxy = Scraper.get_random_proxy()
        session = requests.Session()
        try:
            response = session.get('https://www.trollandtoad.com/', proxies=proxy)
        except Exception as e:
            return TrollAndToad.make_request(url, headers, verify, canada, query)
        token = generate_token(response)
        headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
            'Sec-Fetch-User': '?1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        params = (
            ('selected-cat', '4736'),
            ('search-words', query),
            ('token', token),
        )
        try:
            response = session.get('https://www.trollandtoad.com/category.php', headers=headers, params=params, proxies=proxy)
        except Exception as e:
            return TrollAndToad.make_request(url, headers, verify, canada, query)
        status = response.status_code
        if status == 200:
            return BeautifulSoup(response.text, 'html.parser')
        elif status != 404:
            print(status, url)
            return TrollAndToad.make_request(url, headers, verify, canada, query)
     #   print(url, status)


def generate_token(response) -> Optional[str]:
    """ generate token.
    """
    soup = BeautifulSoup(response.content, 'html.parser')
    token = soup.find('input', {'id': 'token'})
    if token:
        return token.get('value')
