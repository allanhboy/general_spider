# -*- coding: utf-8 -*-
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
        print('GeneralSpider.__init__.%s'%rule.name)
        self.rule_id = rule.id
        self.name = rule.name
        
        # if len(rule.start_urls) == 0:
        #     raise SpiderRuleStartUrlsError()
        self.start_urls = [x for x in rule.start_urls.split(',') if x]
        self.allowed_domains = [x for x in rule.allowed_domains.split(',') if x]
        self.encoding = rule.encoding

        rule_list = []
        #添加`下一页`的规则
        if rule.next_page:
            rule_list.append(Rule(LinkExtractor(restrict_xpaths = rule.next_page)))

        #添加抽取文章链接的规则
        rule_list.append(Rule(LinkExtractor(
            allow=[rule.allow_url],
            restrict_xpaths = ['//div[@class="article_left"]']#[rule.extract_from]
            ),
            callback='parse_item'))
        self.rules = tuple(rule_list)
        super(GeneralSpider, self).__init__()

    def spider_opened(self, spider):
        task = SpiderTask(
            spider_name = self.name,
            spider_rule_id = self.rule_id,
            start_time = datetime.now(),
            status = 'running'
        )
        session = DBSession()

        query = session.query(SpiderTask).filter(SpiderTask.spider_rule_id == task.spider_rule_id, SpiderTask.end_time == None)

        if query.count() == 0 :
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
        spider = super(GeneralSpider, cls).from_crawler(crawler, *args, **kwargs)

        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
   

    

    # def parse(self, response):
    #     elm_page = response.xpath('//div[@class="main_left"]')
    #     print(elm_page)

    def parse_item(self, response):
        # o = urlparse(response.url)
        # (path, filename) = os.path.split('%s%s' % (o.hostname, o.path))

        # if not filename.strip():
        #     filename = "index.html"

        # (filename, ext) = os.path.splitext(filename)

        # if not ext.strip():
        #     ext = ".html"
        # filename = '%s/%s%s' % (path, filename, ext)

        if self.encoding != 'utf-8':
            html = response.body.decode(self.encoding).encode('utf-8')
        else:
            html = response.body_as_unicode()
        


        print(html)
        
        # # print('ok......', filename)
        # title = response.xpath('//div[@class="article_left"]/h1/text()').extract_first()
        # content = response.xpath('//div[@class="article_left"]/div[@id="articleC"]').extract_first()
        # # self.bucket.put_object(filename, html)
        # yield {'filename': filename, 'html': content}
        # # yield {'url': response.url, 'title': title, 'content': content}
        # # yield {'url': response.url}