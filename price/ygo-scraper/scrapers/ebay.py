from bs4 import BeautifulSoup

from scrapers.scraper import Scraper

AFF = 'http://rover.ebay.com/rover/1/711-53200-19255-0/1?ff3=4&pub=5575502459&toolid=10001&campid=5338533011&customid=&mpre='

ebay_headers = {
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


class EbayUS(Scraper):
    """ eBay.com Scraping class"""

    def find_lowest(self, code: str) -> float:
        """
        Goes to website and finds lowest price for the code
        """
        self.url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={code.replace(" ", "+")}&_sacat=0&LH_PrefLoc=3&_sop=15'
        soup = Scraper.make_request(self.url, headers=ebay_headers)
        if not soup:
            return

        results = soup.find('h1', {'class': 'srp-controls__count-heading'})
        if not results:
            return
        results = results \
            .text.replace('results', '') \
            .replace('result', '') \
            .replace('ados', '') \
            .replace('ado', '') \
            .replace(code, '') \
            .replace('para', '') \
            .replace('for', '') \
            .strip()
        if ' for ' in results:
            results = results.split(' for ')[0].strip()
        try:
            results = int(results)
        except Exception as e:
            return

        if results == 0:
            return
        result_list = soup.find('ul', {'class': 'srp-results'})
        if not result_list:
            return
        items = result_list.find_all('li', {'class': 's-item'})
        prices = [self.process_item(x) for x in items[:results] if x]
        prices = [x for x in prices if x]
        if prices:
            prices = prices
            avg, low, high = self.tmean(prices)
            self.results = results
            self.low = low
            self.high = high
            self.urls = ','.join(self.urls)
            return float("{:.2f}".format(avg))


    def process_item(self, item):
        try:
            title = item.find('h3', {'class': 's-item__title'}).text
        except:
            return None
        x3 = True if '3x' in title else False
        price = item.find('span', {'class': 's-item__price'})
        if not price:
            return None
        price = price.text.strip()

        if 'to' in price:
            return None
        if 'Trending' in price:
            return None

        try:
            price = float(price.replace('$', '').replace(',', ''))
        except ValueError:
            return None

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

        link = item.find('a', {'class': 's-item__link'})
        if link:
            link = link['href']
            link = AFF + link[:link.find('?')]
            self.urls.append(link)
        return price
        #prices.append(price)

class EbayCA(Scraper):
    """ eBay.ca Scraping class"""

    def find_lowest(self, code: str) -> float:
        """
        Goes to website and finds lowest price for the code
        """
        self.url = f'https://www.ebay.ca/sch/i.html?_from=R40&_sacat=0&_nkw={code.replace(" ", "+")}&LH_PrefLoc=1&_sop=15'

        soup = Scraper.make_request(self.url, canada=True)
        if not soup:
            return

        items = []

        result_items = soup.find('ul', {'id': 'ListViewInner'})
        if not result_items:
            return
        for li in result_items.find_all('li', {'class': 'lvresult'}):
            if 'sresult' in li['class']:
                items.append(li)
            else:
                break

        results = len(items)
        prices = [self.process_items(x) for x in items]
        prices = [x for x in prices if x]
        if prices:
            prices = prices
            avg, low, high = self.tmean(prices)
            self.results = results
            self.low = low
            self.high = high
            self.urls = ','.join(self.urls)
            return float("{:.2f}".format(avg))

    def process_items(self, item):
        try:
            title = item.find('h3', {'class': 'lvtitle'}).text
        except:
            return
        x3 = True if '3x' in title else False
        price = item.find('span', {'class': 'bold'})
        if not price:
            return
        price = price.text.strip()
        if ' to ' in price:
            return
        if 'Trending' in price:
            return

        try:
            price = float(price.replace('C $', '').replace(',', ''))
        except ValueError:
            return
        if x3:
            price = price / 3

        shipping = item.find('span', {'class': 'fee'})
        if shipping:
            shipping = shipping.text. \
                replace('+C $', ''). \
                replace('shipping', '')
            try:
                shipping = float(shipping)
            except ValueError:
                shipping = 0
            price += shipping
        link = item.find('a', {'class': 's-item__link'})
        if link:
            link = link['href']
            link = AFF + link[:link.find('?')]
            self.urls.append(link)
        return price
