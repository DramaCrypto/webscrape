# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv

from scrapy.exporters import CsvItemExporter
from scrapy import signals
from pydispatch import dispatcher

def item_type(item):
    # The CSV file names are used (imported) from the scrapy spider.
    # return type(item)
    return type(item).__name__.lower()

class QuoteAllDialect(csv.excel):
    quoting = csv.QUOTE_NONNUMERIC

class QuoteAllCsvItemExporter(CsvItemExporter):

    def __init__(self, *args, **kwargs):
        kwargs.update({'dialect': QuoteAllDialect, 'delimiter':';'})
        super(QuoteAllCsvItemExporter, self).__init__(*args, **kwargs)

class DapartoPipeline(object):
    fileNamesCsv = ['dapartoitem','dapartocomp']

    def __init__(self):
        self.files = {}
        self.exporters = {}
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_opened(self, spider):
        self.files = dict([ (name, open(name+'.csv','wb')) for name in self.fileNamesCsv ])
        for name in self.fileNamesCsv:
            self.exporters[name] = QuoteAllCsvItemExporter(self.files[name])

            if name == 'dapartoitem':
                # self.exporters[name].fields_to_export = ['ean', 'producer_name', 'item_number', 'item_status', 'competitors_site_url','price1', 'price2']
                self.exporters[name].fields_to_export = ['item_id', 'producer_name', 'item_number', 'item_status', 'competitors_site_url','price1', 'price2']
                self.exporters[name].start_exporting()

            if name == 'dapartocomp':
                # self.exporters[name].fields_to_export = ['producer_name', 'item_number', 'competitor', 'rating', 'price1', 'price2']
                self.exporters[name].fields_to_export = ['item_id', 'competitor', 'rating', 'price1', 'price2']
                self.exporters[name].start_exporting()

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        typesItem = item_type(item)
        if typesItem in set(self.fileNamesCsv):
            typesItem = item_type(item)
            self.exporters[typesItem].export_item(item)
        return item
