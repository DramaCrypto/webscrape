# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DapartoItem(scrapy.Item):
    # ean = scrapy.Field()
    item_id = scrapy.Field()
    producer_name = scrapy.Field()
    item_number = scrapy.Field()
    item_status = scrapy.Field()
    competitors_site_url = scrapy.Field()
    price1 = scrapy.Field()
    price2 = scrapy.Field()

class DapartoComp(scrapy.Item):
    # producer_name = scrapy.Field()
    # item_number = scrapy.Field()
    item_id = scrapy.Field()
    competitor = scrapy.Field()
    rating = scrapy.Field()
    price1 = scrapy.Field()
    price2 = scrapy.Field()
