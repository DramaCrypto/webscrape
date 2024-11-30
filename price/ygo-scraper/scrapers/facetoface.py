from typing import Optional

from scrapers.scraper import Scraper


class FaceToFace(Scraper):

    def find_lowest(self, code: str) -> Optional[float]:
        url = 'https://www.facetofacegames.com/products/search?q=' + code.replace(' ', '+')

        self.url = url
        soup = self.make_request(url, canada=True)

        if not soup:
            return None
        product = soup.find('li', {'class': 'product'})
        self.results = 0
        prices = []
        if not product:
            return
        variants = product.find('div', {'class': 'variants'})
        variants = variants.find_all('div', {'class': 'variant-row'})

        for row in variants:
            variant_name = row.find('span', {'class': 'variant-main-info'}).text.strip()
            #print(variant_name)
            if 'near mint' in variant_name.lower() or 'out of stock' in variant_name.lower():
                try:
                    price_str = row.find('span', {'class': 'price'}).text.strip()
                except:
                    #print('cant parse str', url)
                    continue
                price = float(price_str.replace('CAD$', '').replace(',','').strip())
                #print('price found', price)
                prices.append(price)
            else:
                pass
                #print('not matching at alll', url)

        if prices:
            avg, low, high = self.tmean(prices)
            self.results = len(prices)
            self.low = low
            self.high = high
           # print(float("{:.2f}".format(avg)), code)
            return float("{:.2f}".format(avg))

# ftf = FacetoFace()
# ftf.find_lowest('LOB-001 unlimited')