# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings

from daparto.items import DapartoComp, DapartoItem
from daparto.spiders.daparto_spider import DapartoSpiderSpider
from daparto.pipelines import DapartoPipeline
import daparto.middlewares
import daparto.settings as mysettings
import csv
from ftplib import FTP
from zipfile import ZipFile

#dependencies
import urllib.robotparser
import scrapy.spiderloader 
import scrapy.statscollectors 
import scrapy.logformatter 
import scrapy.dupefilters 
import scrapy.squeues 
import scrapy.extensions.spiderstate 
import scrapy.extensions.corestats 
import scrapy.extensions.telnet 
import scrapy.extensions.logstats 
import scrapy.extensions.memusage 
import scrapy.extensions.memdebug 
import scrapy.extensions.feedexport 
import scrapy.extensions.closespider 
import scrapy.extensions.debug 
import scrapy.extensions.httpcache 
import scrapy.extensions.statsmailer 
import scrapy.extensions.throttle 
import scrapy.core.scheduler 
import scrapy.core.engine 
import scrapy.core.scraper 
import scrapy.core.spidermw 
import scrapy.core.downloader
import scrapy.downloadermiddlewares.stats 
import scrapy.downloadermiddlewares.httpcache 
import scrapy.downloadermiddlewares.cookies 
import scrapy.downloadermiddlewares.useragent 
import scrapy.downloadermiddlewares.httpproxy 
import scrapy.downloadermiddlewares.ajaxcrawl 
import scrapy.downloadermiddlewares.chunked 
import scrapy.downloadermiddlewares.decompression 
import scrapy.downloadermiddlewares.defaultheaders 
import scrapy.downloadermiddlewares.downloadtimeout 
import scrapy.downloadermiddlewares.httpauth 
import scrapy.downloadermiddlewares.httpcompression 
import scrapy.downloadermiddlewares.redirect 
import scrapy.downloadermiddlewares.retry 
import scrapy.downloadermiddlewares.robotstxt 
import scrapy.spidermiddlewares.depth 
import scrapy.spidermiddlewares.httperror 
import scrapy.spidermiddlewares.offsite 
import scrapy.spidermiddlewares.referer 
import scrapy.spidermiddlewares.urllength 
import scrapy.pipelines 
import scrapy.core.downloader.handlers.http
import scrapy.core.downloader.handlers.datauri
import scrapy.core.downloader.handlers.file
import scrapy.core.downloader.handlers.s3
import scrapy.core.downloader.handlers.ftp 
import scrapy.core.downloader.contextfactory
import scrapy.exporters
import scrapy_useragents.downloadermiddlewares.useragents

with open('/root/daparto/daparto/day.txt', 'r') as read_txt:
    day = read_txt.read()
    print(f'Getting records for {day}')

while True:
    try:
        #download and extract file
        ftp = FTP("185.201.145.121")
        ftp.login("daparto_scrap", "nNKRfeP4ZpIs")
        path = '/input_data/'
        filename = 'input_items_for_scraping.zip'
        ftp.cwd(path)
        ftp.retrbinary("RETR " + filename ,open("/root/daparto/daparto/" + filename, 'wb').write)
        ftp.quit()
        break
    except:
        pass


with ZipFile("/root/daparto/daparto/" + filename, 'r') as zipObj:
    zipObj.extractall("/root/daparto/daparto/")

crawler_settings = Settings()
crawler_settings.setmodule(mysettings)
process = CrawlerProcess(settings=crawler_settings)
process.crawl(DapartoSpiderSpider, day=day)
process.start()

# while True:
#     try:
#         #upload file
#         ftp = FTP("185.201.145.121")
#         ftp.login("daparto_scrap", "nNKRfeP4ZpIs")
#         path = '/output_data/'
#         ftp.cwd(path)
#         with ZipFile('daparto_result.zip', 'w') as zipObj:
#             zipObj.write('dapartocomp.csv')
#             zipObj.write('dapartoitem.csv')

#         with open('daparto_result.zip', 'rb') as f:
#             ftp.storbinary('STOR %s' % 'daparto_result.zip', f)
#         ftp.quit()
#         break
#     except:
#         pass

with open('/root/daparto/daparto/day.txt', 'w') as write_txt:
    if int(day) == 3:
        day = 1
    else:
        day = int(day) + 1
    write_txt.write(str(day))

print("Job completed")
