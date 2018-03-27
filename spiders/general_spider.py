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
        print(rule)
        # auth = oss2.Auth('LTAIEGPz3hY8pCTU', '8V0l4V8F2SZP5RasV0kw6ljusPlNSD')
        # endpoint = 'http://oss-cn-hangzhou-internal.aliyuncs.com'  # 假设Bucket处于杭州区域
        # self.bucket = oss2.Bucket(auth, endpoint, 'syzb01')
        self.name = rule.name
        self.rule_id = rule.id
        # if len(rule.start_urls) == 0:
        #     raise SpiderRuleStartUrlsError()
        self.start_urls = rule.start_urls
        self.allowed_domains = rule.allowed_domains
        self.encoding = rule.encoding

        # rule_list = []

        # rule_list.append(Rule(LinkExtractor(
        #     allow=rule.allow_url.split(','),
        #     unique=True),
        #     follow=True,
        #     callback='parse_item'))

        super(GeneralSpider, self).__init__()
        pass

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
