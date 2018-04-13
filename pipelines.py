# -*- coding: utf-8 -*-
import oss2
import logging
from scrapy.exceptions import NotConfigured

from db.article import Article
from db import DBSession

logger = logging.getLogger(__name__)


class OSSPipeline(object):
    def __init__(self, key_id, key_secret, endpoint, bucket_name):
        self.key_id = key_id
        self.key_secret = key_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('OSS_ENABLE'):
            raise NotConfigured
        return cls(
            key_id=crawler.settings.get('OSS_KEY_ID'),
            key_secret=crawler.settings.get('OSS_KEY_SECRET'),
            endpoint=crawler.settings.get('OSS_ENDPOINT'),
            bucket_name=crawler.settings.get('OSS_BUCKET_NAME')
        )

    def open_spider(self, spider):
        auth = oss2.Auth(self.key_id, self.key_secret)
        self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        if item['filename']:
            if item['html']:
                filename = item['filename']
                html = item['html']
                logger.info("store oss: %s" % filename)
                self.bucket.put_object(filename, html)
        return item


from scrapy.exceptions import DropItem


class DuplicatesPipeline(object):
    def __init__(self):
        self.urls_seen = set()

    def open_spider(self, spider):
        self.session = DBSession()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        if item['url'] in self.urls_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.urls_seen.add(item['url'])
            count = self.session.query(Article).filter(
                Article.url == item['url']).count()
            if count == 0:
                return item
            else:
                raise DropItem("Duplicate item found: %s" % item)


from db import DBSession


class MysqlPipeline(object):
    def open_spider(self, spider):
        self.session = DBSession()

    def close_spider(self, spider):
        self.session.close()

    def process_item(self, item, spider):
        a = Article(title=item["title"],
                    url=item["url"],
                    body=item["body"],
                    text=item["text"],
                    publish_time=item["publish_time"],
                    source_site=item["source_site"])
        self.session.add(a)
        self.session.commit()
        return item


from bs4 import BeautifulSoup


class HtmlCleaningPipeline(object):
    def process_item(self, item, spider):
        if item['body']:

            soup = BeautifulSoup(item['body'])
            text = ''
            for p in soup.find_all("p"):
                p_text = p.get_text(strip=True).replace("：", ":").replace(
                    "，", ",").replace("。", ".").replace("（", "(").replace("）", ")").replace("％", "%")
                if p_text.find('来源:') == 0:
                    pass
                elif p_text.find('作者:') == 0:
                    pass
                elif p_text.find('(注:') == 0:
                    pass
                elif p_text.find('本文出品:') == 0:
                    pass
                elif p_text.find('转载声明:') == 0:
                    pass
                elif p_text.find('风险提示:') == 0:
                    pass
                elif p_text.find('声明:') == 0:
                    pass
                elif p_text.find('(本文为新三板在线原创稿件') == 0:
                    pass
                elif p_text.find('数据来源:') == 0:
                    pass
                else:
                    if text.strip():
                        text += "\n" + p_text
                    else:
                        text = p_text
            item['text'] = text
        return item


import urllib3


class ProxyIpMiddleware(object):
    def __init__(self, ip=''):
        self.ip = ip

    def process_request(self, request, spider):
        http = urllib3.PoolManager()
        r = http.request(
            'GET', 'http://proxy-pool.c2fd1643d9abe4d9fb2887ea58a7a3202.cn-hangzhou.alicontainer.com/get/')
        ip = r.data.decode('utf-8').strip()
        if ip:
            logger.debug('Current Proxy Ip: %s' % ip)
            request.meta["proxy"] = "http://"+ip
        r.close()