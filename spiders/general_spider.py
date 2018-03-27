# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import oss2
import os


class GeneralSpider(CrawlSpider):
    name = "GeneralSpider"
    start_urls = []
    allowed_domains = []

    def __init__(self, rule):
        # print(rule)
        self.rule_id = rule.id
        self.name = rule.name
        
        # if len(rule.start_urls) == 0:
        #     raise SpiderRuleStartUrlsError()
        self.start_urls = [x for x in rule.start_urls.split(',') if x]
        self.allowed_domains = [x for x in rule.allowed_domains.split(',') if x]
        self.encoding = rule.encoding

        # rule_list = []

        # rule_list.append(Rule(LinkExtractor(
        #     allow=rule.allow_url.split(','),
        #     unique=True),
        #     follow=True,
        #     callback='parse_item'))

        super(GeneralSpider, self).__init__()

    rules = (
        Rule(LinkExtractor(allow='/20\d{2}-[0,1]\d/ART[\d\-_]*.html',
                           unique=True), callback='parse_item', follow=False),
        Rule(LinkExtractor(restrict_xpaths=[
             '//div[@class="page"]', '//div[@class="main_left"]/div[@class="list_model"]/div/h3']), follow=True)
    )

    # def parse(self, response):
    #     elm_page = response.xpath('//div[@class="main_left"]')
    #     print(elm_page)

    def parse_item(self, response):

        o = urlparse(response.url)
        (path, filename) = os.path.split('%s%s' % (o.hostname, o.path))

        if not filename.strip():
            filename = "index.html"

        (filename, ext) = os.path.splitext(filename)

        if not ext.strip():
            ext = ".html"
        filename = '%s/%s%s' % (path, filename, ext)

        if self.encoding != 'utf-8':
            html = response.body.decode(self.encoding).encode('utf-8')
        else:
            html = response.body_as_unicode()

        # # print(html)
        
        # print('ok......', filename)
        title = response.xpath('//div[@class="article_left"]/h1/text()').extract_first()
        content = response.xpath('//div[@class="article_left"]/div[@id="articleC"]').extract_first()
        # self.bucket.put_object(filename, html)
        yield {'filename': filename, 'html': content}
        # yield {'url': response.url, 'title': title, 'content': content}
        # yield {'url': response.url}
