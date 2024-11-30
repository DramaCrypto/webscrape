# -*- coding: utf-8 -*-
import scrapy
import csv
import json
import random
from collections import defaultdict
import logging

import scrapy
from daparto.items import DapartoItem, DapartoComp

class DapartoSpiderSpider(scrapy.Spider):
    name = 'daparto_spider'
    allowed_domains = ['daparto.de']
    start_urls = ['http://daparto.de/']
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    def __init__(self, day):
        self.count = 0
        self.day = day
        self.search_retries = defaultdict(int)
        self.item_retries = defaultdict(int)
        self.competitor_retries = defaultdict(int)

    def start_requests(self):
        print('Starting the scrap process')
        with open('/root/daparto/daparto/input_items_for_scraping.csv', 'r', encoding='utf-8') as csv_file:
            print("Loaded csv file")
            print(f"Processing data with day {self.day}")
            csv_reader = csv.reader(csv_file)
            next(csv_reader, None)
            count = 0
            for r in csv_reader:
                count += 1
                r_list = r[0].split(";")
                # r_list = r
                # Second index ProducerNumber
                s = r_list[2].replace('"', "")
                # try:
                #     scrap_day = r_list[4].replace('"', "")
                # except IndexError:
                #     continue
                url = "https://www.daparto.de/api/Teilenummernsuche/Teile/Alle-Hersteller/{}".format(s)
                username = 'lum-customer-hl_115d7767-zone-static-route_err-pass_dyn'
                password = 'xd9l9to77oz3'
                port = 22225
                session_id = random.random()
                super_proxy_url = ('http://%s-country-de-session-%s:%s@zproxy.lum-superproxy.io:%d' %(username, session_id, password, port))
                print('No.{} : getting item for {}'.format(count, url))
                try:
                    yield scrapy.Request(url=url, callback=self.parse, meta={'proxy':super_proxy_url, 'ean':r_list[0], 'producer_name':r_list[1].replace('"', ""),'producer_number': s, 'item_id':r_list[5].replace('"', ""),'url':url, 'count':count}, dont_filter=True)
                except:
                    print('No.{} : Error getting item for {}'.format(count, url))
                    logging.error('No.{} : Error getting item for {}'.format(count, url))

    def parse(self, response):
        ean = response.meta['ean']
        producer_name = response.meta['producer_name']
        producer_number = response.meta['producer_number']
        item_id = response.meta['item_id']
        url = response.meta['url']
        count = response.meta['count']
        username = 'lum-customer-hl_115d7767-zone-static-route_err-pass_dyn'
        password = 'xd9l9to77oz3'
        port = 22225
        session_id = random.random()
        super_proxy_url = ('http://%s-country-de-session-%s:%s@zproxy.lum-superproxy.io:%d' %(username, session_id, password, port))
        if response.status in [403, 404]:
            if self.search_retries[producer_number] == 20:
                print("Retrying reach max count, stopping retry.")
                logging.error("Stopping retries for {}".format(item_id))
            else:
                yield scrapy.Request(url=url, callback=self.parse, meta={'proxy':super_proxy_url, 'ean':ean, 'producer_name':producer_name ,'producer_number': producer_number, 'item_id':item_id, 'url':url, 'count':count}, dont_filter=True)
                # self.item_retries[producer_number] = self.item_retries.get(producer_number, 0) + 1
                self.search_retries[producer_number] += 1
        else:
            jsonresponse = json.loads(response.body_as_unicode())
            if not jsonresponse['spareParts']:
                # print(f"No.{count}-No item found for {producer_number}")
                self.logger.info(f"No.{count}-No item found for {producer_number}")
                yield {
                    'EAN': ean,
                    'Producer Name': producer_name,
                    'Item Number' : producer_number,
                    'Item Status': f'No result found for {producer_number}'
                }
            else:
                referer = 'https://www.daparto.de' + jsonresponse['spareParts'][0]['url']
                item_url = "https://www.daparto.de/api/Ersatzteil/{}?kbaTypeId=null".format(jsonresponse['spareParts'][0]['id'])
                competitors_url = "https://www.daparto.de/api/Ersatzteil/{}/Angebote/CPO?categoryId=&kbaTypeId=null".format(jsonresponse['spareParts'][0]['id'])
                # print('No.{}-getting update for {}'.format(count, producer_number))
                yield scrapy.Request(item_url, callback = self.parse_item, meta={'proxy':super_proxy_url, 'referer':referer, 'item_url':item_url, 'count':count, 'ean':ean, 'item_id':item_id}, headers={'referer':referer}, dont_filter=True)
                yield scrapy.Request(competitors_url, callback = self.parse_competitors, meta={'proxy':super_proxy_url, 'referer':referer, 'competitors_url':competitors_url, 'count':count, 'producer_name':producer_name, 'producer_number':producer_number, 'item_id':item_id}, headers={'referer':referer}, dont_filter=True)

    def parse_item(self, response):
        items = DapartoItem()
        item_url = response.meta['item_url']
        referer = response.meta['referer']
        ean = response.meta['ean']
        item_id = response.meta['item_id']
        count = response.meta['count']
        username = 'lum-customer-hl_115d7767-zone-static-route_err-pass_dyn'
        password = 'xd9l9to77oz3'
        port = 22225
        session_id = random.random()
        super_proxy_url = ('http://%s-country-de-session-%s:%s@zproxy.lum-superproxy.io:%d' %(username, session_id, password, port))
        # print(f"{response.status} for {item_url}")
        if response.status in [403, 404]:
            if self.item_retries[ean] == 20:
                print("Retrying reach max count, stopping retry.")
                logging.error("Stopping retries for {}".format(item_id))
            else:
                print(f'No.{count}-retrying url with {item_url} - code {response.status}')
                self.logger.info(f'No.{count}-retrying url with {item_url} - code {response.status}')
                yield scrapy.Request(item_url, callback = self.parse_item, meta={'proxy':super_proxy_url, 'referer':referer, 'item_url':item_url, 'count':count, 'ean':ean, 'item_id':item_id}, headers={'referer':referer}, dont_filter=True)
                self.item_retries[ean] += 1
        else:
            jsonresponse = json.loads(response.body_as_unicode())
            # item_dict = {
            #     'EAN': ean,
            #     'Producer Name' : jsonresponse['article']['manufacturer']['name'],
            #     'Item Number' : jsonresponse['article']['number'],
            #     'Item Status' : jsonresponse['article']['condition'],
            #     'Price1' : jsonresponse['article']['price'],
            #     'Price2' : jsonresponse['article']['totalPrice']          
            # }
            # items['ean'] = str(ean)
            items['item_id'] = str(item_id)
            items['producer_name'] = str(jsonresponse["article"]["manufacturer"]["name"])
            items['item_number'] = str(jsonresponse["article"]["number"])
            items['item_status'] = str(jsonresponse["article"]["condition"])
            items['competitors_site_url'] = str(f'https://www.daparto.de{jsonresponse["article"]["url"].split("?")[0]}')
            items['price1'] = str(jsonresponse['article']['price']).replace(".", ",")
            items['price2'] = str(jsonresponse['article']['totalPrice']).replace(".", ",")

            # print(f"No.{count}-{items}")
            yield items
            # with open('items.csv', mode='w') as items_file:
            #     items_writer = csv.DictWriter(items_file, fieldnames=item_dict.keys(), delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            #     items_writer.writeheader()
            #     items_writer.writerow(item_dict)

    def parse_competitors(self, response):
        comps = DapartoComp()
        competitors_url = response.meta['competitors_url']
        item_id = response.meta['item_id']
        referer = response.meta['referer']
        producer_name = response.meta['producer_name']
        producer_number = response.meta['producer_number']
        count = response.meta['count']
        username = 'lum-customer-hl_115d7767-zone-static-route_err-pass_dyn'
        password = 'xd9l9to77oz3'
        port = 22225
        session_id = random.random()
        super_proxy_url = ('http://%s-country-de-session-%s:%s@zproxy.lum-superproxy.io:%d' %(username, session_id, password, port))
        if response.status in [403, 404]:
            if self.competitor_retries[producer_number] == 20:
                print("Retrying reach max count, stopping retry.")
                logging.error("Stopping retries for {}".format(item_id))
            else:
                print(f'No.{count}-retrying url with {competitors_url} - code {response.status}')
                self.logger.info(f'No.{count}-retrying url with {competitors_url} - code {response.status}')
                yield scrapy.Request(competitors_url, callback = self.parse_competitors, meta={'proxy':super_proxy_url, 'referer':referer, 'competitors_url':competitors_url, 'count':count, 'producer_name':producer_name, 'producer_number':producer_number, 'item_id':item_id}, headers={'referer':referer}, dont_filter=True)
                self.competitor_retries[producer_number] += 1
        else:
            jsonresponse = json.loads(response.body_as_unicode())
            if jsonresponse:
                for each in jsonresponse:
                    # competitor_dict = {
                    #     'Producer Name' : producer_name,
                    #     'Item Number' : producer_number,
                    #     'Competitor' : each['shop']['name'] if each['shop']['name'] else 'N/A',
                    #     'Rating' : each['shop']['rating'] if each['shop']['rating'] else 'N/A',
                    #     'Price1' : each['price'] if each['price'] else 'N/A',
                    #     'Price2' : each['totalPrice'] if each['totalPrice'] else 'N/A'         
                    # }
                    # comps['producer_name'] = str(producer_name)
                    # comps['item_number'] = str(producer_number)
                    comps['item_id'] = str(item_id)
                    comps['competitor'] = str(each["shop"]["name"]) if each["shop"]["name"] else "N/A"
                    comps['rating'] = each['shop']['rating'] if each['shop']['rating'] else 'N/A'
                    comps['price1'] = str(each['price']).replace(".", ",") if each['price'] else 'N/A'
                    comps['price2'] = str(each['totalPrice']).replace(".", ",") if each['totalPrice'] else 'N/A'
                    yield comps
