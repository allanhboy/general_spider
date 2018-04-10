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


class HtmlCleaningPipeline(object):
    def process_item(self, item, spider):
        if item['body']:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(item['body'])
            text = ''
            for p in soup.find_all("p"):
                p_text = p.get_text(strip=True)
                if p_text:
                    text+=p_text
                item['text'] = text
        return item
        