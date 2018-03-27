# -*- coding: utf-8 -*-
import logging
import time

from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy import signals
from scrapy.utils.request import request_fingerprint
from scrapy.utils.project import data_path
from scrapy.utils.python import to_bytes
from scrapy.exceptions import NotConfigured

import redis

logger = logging.getLogger(__name__)


class DeltaFetch(object):

    def __init__(self, redis_host, redis_port, redis_db, redis_password, stats=None):
        self.stats = stats
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password

    @classmethod
    def from_crawler(cls, crawler):
        s = crawler.settings
        if not s.getbool('DELTA_FETCH_ENABLED'):
            raise NotConfigured
            
        host = s.get('DELTA_FETCH_REDIS_HOST', 'localhost')
        port = s.get('DELTA_FETCH_REDIS_PORT', 6379)
        db = s.get('DELTA_FETCH_REDIS_DB', 0)
        password = s.get('DELTA_FETCH_REDIS_PASSWORD', None)
        o = cls(host, port, db, password, crawler.stats)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.server = redis.StrictRedis(
            host=self.redis_host, port=self.redis_port, db=self.redis_db, password=self.redis_password)

    def spider_closed(self, spider):
        pass

    def process_spider_output(self, response, result, spider):
        for r in result:
            if isinstance(r, Request):
                key = self._get_key(r)
                if self.server.get(key):
                    logger.info("Ignoring already visited: %s" % r)
                    if self.stats:
                        self.stats.inc_value(
                            'deltafetch/skipped', spider=spider)
                    continue
            elif isinstance(r, (BaseItem, dict)):
                key = self._get_key(response.request)
                self.server.set(key, response.request.url)
                logger.debug("stored data: %s" % r)
                if self.stats:
                    self.stats.inc_value('deltafetch/stored', spider=spider)

            yield r

    def _get_key(self, request):
        key = request.meta.get('deltafetch_key') or request_fingerprint(request)
        # request_fingerprint() returns `hashlib.sha1().hexdigest()`, is a string
        return to_bytes(key)
