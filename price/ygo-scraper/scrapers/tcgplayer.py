import json
import time
from typing import Optional

from scrapers.scraper import Scraper


class TCGPlayer(Scraper):
    """ TCGPlayer.com scraper class"""

    def find_lowest(self, code: str, edition, condition, rarity) -> Optional[float]:
        """
        Goes to website and finds lowest price for the code
        :param code:
        :return:
        """
        if 'limited' in edition.lower():
            edition = 'limited'
        url = 'https://shop.tcgplayer.com/yugioh/product/show?' \
              f'advancedSearch=true&Number={code}&Price_Condition=Less+Than'
        self.url = url + "?partner=YGOTRADER&utm_campaign=affiliate&utm_medium=YGOTRADER&utm_source=YGOTRADER"
      #  print(url)

        soup = self.make_request(url)

        cards = soup.find_all('div', {'class': 'product__card'})
        matched_card = None
        for card in cards:
            extended = card.find('div', {'class': 'product__extended-fields'})
            card_rarity = extended.find_all('span')[-1].text.replace('Rarity', '').strip().lower()

            if rarity.lower() == card_rarity:
                matched_card = card

        if not matched_card:
            return None
        else:
            soup = matched_card

        market_price = soup.find('dl', {'class': 'product__market-price'})
        market_price = market_price.find('dd').text.strip() if market_price else None
        try:
            market_price = float(market_price.replace('$', '')) if market_price else None
            market_price = float("{:.2f}".format(market_price)) if market_price else None
            self.market_price = market_price
        except:
            self.market_price = None

        offers = soup.find('div', {'class': 'product__offers'})
        json_data = offers.find('script', {'type': 'text/javascript'}) if offers else None
        if offers and json_data:
            json_data = json_data.text.strip()
            json_data = json_data[json_data.find('=')+1:-1]
            try:
                json_data = json.loads(json_data)
            except:
                print('no json data')
                return None
            _id = json_data['product_id']
            listings = []
            for i in range(1, 7):
                api_url = 'https://shop.tcgplayer.com/productcatalog/product/changedetailsfilter?filterName=Condition&filterValue=NearMint&productId={}&gameName=yugioh&useV2Listings=false&page={}&_={}'.format(_id, i, int(time.time()))
                #print('API URL:',api_url)
                soup = self.make_request(api_url)
                page_listings = soup.find_all('div', {'class': 'product-listing'})
                if len(page_listings) == 0:
                    break
                listings += page_listings
                self.results = len(listings)
            prices = []
            for listing in listings:
                try:
                    cond_and_edition = listing.find('div', {'class': 'product-listing__condition'}).text.strip().lower()
                except:
                    continue
                if edition.lower().strip() not in cond_and_edition:
                    continue
                price = listing.find('span', {'class': 'product-listing__price'})
                if not price:
                    continue
                price = price.text
                price = float(price.replace('$', '').replace(',',''))
                try:
                    shipping = listing.find('span', {'class': 'product-listing__shipping'}).text
                except:
                    shipping = 0.0
                try:
                    shipping = float(shipping.replace('+ $', '').replace('Shipping', ''))
                except:
                    shipping = 0.0
                total = price + shipping
                prices.append(total)
            if prices:
                avg, low, high = self.tmean(prices)
                self.results = len(listings)
                self.low = low
                self.high = high
                return float("{:.2f}".format(avg))
