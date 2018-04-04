# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import oss2
import os

from scrapy import signals
from db import DBSession, SpiderTask
from datetime import datetime


class GeneralSpider(CrawlSpider):
    name = "GeneralSpider"
    start_urls = []
    allowed_domains = []

    def __init__(self, rule):
        self.rule_id = rule.id
        self.name = rule.name

        # if len(rule.start_urls) == 0:
        #     raise SpiderRuleStartUrlsError()
        self.start_urls = [x for x in rule.start_urls.split(',') if x]
        self.allowed_domains = [
            x for x in rule.allowed_domains.split(',') if x]
        self.encoding = rule.encoding

        self.rule = rule

        rule_list = []
        # 添加`下一页`的规则
        if rule.next_page:
            rule_list.append(
                Rule(LinkExtractor(restrict_xpaths=rule.next_page)))

        # 添加抽取文章链接的规则
        rule_list.append(Rule(LinkExtractor(
            allow=[rule.allow_url],
            # [rule.extract_from]
            # restrict_xpaths=['//div[@class="list_model"]/div/h3']
        ),
            callback='parse_item'))
        self.rules = tuple(rule_list)
        super(GeneralSpider, self).__init__()

    def spider_opened(self, spider):
        task = SpiderTask(
            spider_name=self.name,
            spider_rule_id=self.rule_id,
            start_time=datetime.now(),
            status='running'
        )
        session = DBSession()

        query = session.query(SpiderTask).filter(
            SpiderTask.spider_rule_id == task.spider_rule_id, SpiderTask.end_time == None)

        if query.count() == 0:
            session.add(task)
            session.commit()
        session.close()

    def spider_closed(self, spider):
        session = DBSession()
        task = session.query(SpiderTask).filter(SpiderTask.spider_rule_id == self.rule_id,
                                                SpiderTask.end_time == None
                                                ).first()
        if task:
            task.end_time = datetime.now()
            task.status = "closed"
            session.commit()
        session.close()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GeneralSpider, cls).from_crawler(
            crawler, *args, **kwargs)

        crawler.signals.connect(spider.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        return spider

    def parse_item(self, response):
        self.log('Hi, this is an article page! %s' % response.url)

        article = Article()

        # if self.encoding != 'utf-8':
        #     html = response.body.decode(self.encoding).encode('utf-8')
        # else:
        #     html = response.body_as_unicode()

        article["url"] = response.url

        title = response.xpath(self.rule.title_xpath).extract()
        article["title"] = title[0] if title else ""

        body = response.xpath(self.rule.body_xpath).extract()
        article["body"] = '\n'.join(body) if body else ""

        publish_time = response.xpath(self.rule.publish_time_xpath).extract()
        article["publish_time"] = publish_time[0].replace('\r','').replace('\n','').replace('\t','').replace(' ','') if publish_time else ""

        source_site = response.xpath(self.rule.source_site_xpath).extract()
        article["source_site"] = source_site[0] if source_site else ""

        return article


class Article(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    body = scrapy.Field()
    publish_time = scrapy.Field()
    source_site = scrapy.Field()