# -*- coding: utf-8 -*-
import scrapy

class Article(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()
    text = scrapy.Field()
    publish_time = scrapy.Field()
    source_site = scrapy.Field()