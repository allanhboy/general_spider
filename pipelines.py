# -*- coding: utf-8 -*-
import oss2
import logging

logger = logging.getLogger(__name__)

class OSSPipeline(object):
    def __init__(self, key_id, key_secret, endpoint, bucket_name):
        self.key_id = key_id
        self.key_secret = key_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name

    @classmethod
    def from_crawler(cls, crawler):
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
