from time import *
import requests
import hmac
import hashlib
from urllib.parse import urlencode, quote_plus
from decimal import Decimal
from PyQt5.QtCore import *

from Util.Helper import log
from Pricing.PricingConf import \
    Api_Base_Url, AD_Price_Low_Limit, AD_Price_High_Limit, AD_Price_Delta, Sell_Url_Params

class PricingModule(QThread):
    signalPricing = pyqtSignal('QString')
    signalSelling = pyqtSignal('QString')

    def __init__(self, authKey, secretKey):
        QThread.__init__(self)
        self.baseURL = Api_Base_Url
        self.authKey = authKey
        self.secretKey = secretKey
        self.lowLimitPrice = AD_Price_Low_Limit
        self.highLimitPrice = AD_Price_High_Limit

    def run(self):
        while True:
            self.getSellADList()
            self.sellADPrice()
            sleep(15)

    def getSellADList(self):
        try:
            self.signalPricing.emit('Get List of SellAD: Start...')
            self.listADPrice = []
            reply = requests.get(self.baseURL + '/buy-bitcoins-online/gb/united-kingdom/national-bank-transfer/.json')
            ad_list = reply.json()['data']['ad_list']
            index = 0
            for item in ad_list:
                ad_item = {}
                ad_item['seller'] = item['data']['profile']['name']
                ad_item['method'] = item['data']['trade_type']
                ad_item['rate'] = item['data']['temp_price']
                ad_item['limit'] = item['data']['limit_to_fiat_amounts']
                self.listADPrice.append(ad_item)
                if index > 6:
                    break
                index = index + 1
            self.signalPricing.emit('Get List of SellAD: Succes! AD Count: {0}'.format(index))
        except Exception as e:
            log(str(e))
            self.signalPricing.emit('Get List of SellAD: *** Occur Exception ***')

    def sellADPrice(self):
        if len(self.listADPrice) == 0:
            return
        try:
            self.signalSelling.emit('Sell AD Price: Start...')

            top_price = float(self.listADPrice[0]['rate'])
            price_update_info = self.getPriceEquation(top_price - AD_Price_Delta)
            new_price_equation = price_update_info['price_equation']
            new_price = price_update_info['price']

            body_data = Sell_Url_Params
            body_data['price_equation'] = str(new_price_equation)
            urlencoded_body_data = urlencode(body_data)

            self.refreshMyAds()
            sleep(0.01)

            nonce = int(time() * 100000)

            if len(self.self_ad_list) > 0:      # If I have ad list already, update ads based on the new price
                for my_ad in self.self_ad_list:
                    ad_data = my_ad["data"]
                    ad_id = ad_data["ad_id"]
                    ad_price = float(ad_data["temp_price"])

                    # If my ad price is fit the price condition already, no need to update
                    if (ad_price < top_price and ad_price >= new_price):
                        log('No need to update my ad', ad_id, ' current price is ', ad_price,
                            ' (the lowest price in localbitcoin is ', top_price, ' and candidate price was ', new_price, ')')
                        continue

                    api_endpoint = "/api/ad/" + str(ad_id) + "/"
                    url = self.baseURL + "/api/ad/" + str(ad_id) + "/"

                    message = str(nonce) + self.authKey + api_endpoint + urlencoded_body_data
                    message_bytes = message.encode('utf-8')

                    signature = hmac.new(self.secretKey.encode('utf-8'), msg=message_bytes,
                                         digestmod=hashlib.sha256).hexdigest().upper()
                    header = self.getApiHeader(str(nonce), signature)
                    reply = requests.post(url, headers=header, data=body_data)
                    data_json = reply.json()
                    if 'error' in data_json:
                        self.signalSelling.emit("Sell AD Price: ADS Update Failed On LocalBitcoins")
                    else:
                        log('Updated my ad(id: ', ad_id, ', price: ', ad_price, ' equation: ', ad_data['price_equation'],
                            ') to (price: ', new_price, ', price_equation: ', new_price_equation, ')')
                        self.signalSelling.emit("Sell AD Price: ADS Update Successfully On LocalBitcoins")
            else:
                api_endpoint = "/api/ad-create/"
                url = self.baseURL + "/api/ad-create/"

                message = str(nonce) + self.authKey + api_endpoint + urlencoded_body_data
                message_bytes = message.encode('utf-8')
                signature = hmac.new(self.secretKey.encode('utf-8'), msg=message_bytes,
                                     digestmod=hashlib.sha256).hexdigest().upper()
                header = self.getApiHeader(str(nonce), signature)

                reply = requests.post(url, headers=header, data=body_data)
                data_json = reply.json()
                if 'error' in data_json:
                    self.signalSelling.emit("Sell AD Price: ADS Create Failed On LocalBitcoins")
                else:
                    log('Created my ad(price: ', new_price, ' equation: ', new_price_equation, ')')
                    self.signalSelling.emit("Sell AD Price: ADS Create Successfully On LocalBitcoins")
        except Exception as e:
            log(str(e))
            self.signalSelling.emit('Sell AD Price: *** Occur Exception ***')

    # Get localbitcoin api header
    def getApiHeader(self, nonce, signature):
        return {
            'Apiauth-Key': self.authKey,
            'Apiauth-Nonce': str(nonce),
            'Apiauth-Signature': signature
        }

    # Get price equation from the top price, should less than the delta amount
    def getPriceEquation(self, price):
        reply = requests.get(self.baseURL + '/api/equation/btc_in_usd*USD_in_GBP*1')
        btc_in_gbp = float(reply.json()['data'])
        margin = float(price / btc_in_gbp)
        low_limit = round(Decimal(self.lowLimitPrice) / Decimal(100), 6)
        high_limit = round(Decimal(self.highLimitPrice) / Decimal(100), 6)
        if margin < low_limit:
            margin = low_limit
        elif margin > high_limit:
            margin = high_limit
        price_equation = "btc_in_usd*USD_in_GBP*" + str(margin)
        return {'price_equation': price_equation, 'price': margin * btc_in_gbp}

    # Get my ads
    def refreshMyAds(self):
        nonce = int(time() * 100000)
        api_endpoint = "/api/ads/"
        url = self.baseURL + api_endpoint
        get_or_post_params_urlencoded = ''
        message = str(nonce) + self.authKey + api_endpoint + get_or_post_params_urlencoded
        message_bytes = message.encode('utf-8')
        signature = hmac.new(self.secretKey.encode('utf-8'), msg=message_bytes,
                             digestmod=hashlib.sha256).hexdigest().upper()
        params = {
            'Apiauth-Key': self.authKey,
            'Apiauth-Nonce': str(nonce),
            'Apiauth-Signature': signature
        }
        reply = requests.get(url, headers=params)
        ads_data_json = reply.json()
        self.self_ad_list = []
        if not 'error' in ads_data_json:
            self.self_ad_list = ads_data_json['data']['ad_list']

