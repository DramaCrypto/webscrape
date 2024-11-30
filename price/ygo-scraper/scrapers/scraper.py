from statistics import mean
from random import choice

import requests
from bs4 import BeautifulSoup
import numpy as np
from scipy import stats

proxy_ca = 'http://api.buyproxies.org/?a=showProxies&pid=124209&key=91b9fa70313b8c6dff2dc3f98ecf7845&port=12345&country=Canada'
proxy_us = 'http://api.buyproxies.org/?a=showProxies&pid=124209&key=91b9fa70313b8c6dff2dc3f98ecf7845&port=12345&country=US'


def get_proxies_from_url(url):
    proxies = requests.get(url + '&format=2').text.strip()
    proxies = proxies.split('\n')
    return [x for x in proxies if x.strip()]


PROXIES = get_proxies_from_url(proxy_us)
PROXIES_CANADA = get_proxies_from_url(proxy_ca)


# with open('proxies.txt') as f:
#     PROXIES = f.read().split('\n')
#     PROXIES = [x for x in PROXIES if x.strip()]
# 
# with open('proxies_cad.txt') as f:
#     PROXIES_CANADA = f.read().split('\n')
#     PROXIES_CANADA = [x for x in PROXIES if x.strip()]


class Scraper:

    def __init__(self):
        self.url = ""
        self.results = None
        self.market_price = None
        self.low = None
        self.high = None
        self.urls = []

    @staticmethod
    def find_lowest(code: str) -> float:
        """
        Goes to website and finds lowest price for the code
        :param code:
        :return:
        """
        pass

    @staticmethod
    def make_request(url: str, headers=None, verify=True, canada=False) -> BeautifulSoup:
        """
        makes HTTP get request
        :param verify:
        :param headers:
        :param url: url to make the request to
        :return: BeautifulSoup object
        """
        headers_ = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }

        if canada:
            proxies = Scraper.get_random_proxy(True) if PROXIES_CANADA else {}
        else:
            proxies = Scraper.get_random_proxy() if PROXIES else {}
        try:
            response = requests.get(url,
                                    proxies=proxies,
                                    headers=headers if headers else headers_,
                                    verify=verify
                                    )
        except Exception as e:
            print(e, url)
            return Scraper.make_request(url, headers, verify, canada)
        status = response.status_code
        if status == 200:
            return BeautifulSoup(response.text, 'html.parser')
        elif status != 404:
            print(status, url)
            return Scraper.make_request(url, headers, verify, canada)
        print(url, status)

    @staticmethod
    def get_random_proxy(canada=False):
        proxy = choice(PROXIES if not canada else PROXIES_CANADA)
        return {
            'http': 'http://' + proxy,
            'https': 'http://' + proxy
        }

    @staticmethod
    def tmean(lst):
        trimmed = list(stats.trimboth(lst, 0.2))  # trim 20% from both ends
        low = float(min(trimmed))
        high = float(max(trimmed))
        avg = float(mean(trimmed))
        return avg, low, high

# t0 = [1, 5, 4, 5, 9]
# t1 = [1, 1, 2, 7, 5, 7, 8, 6, 7, 87, 79]
# Scraper.tmean(t0)
# Scraper.tmean(t1)
