# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from settings import get_scrapy_settings
from spiders.general_spider import GeneralSpider
from rules.spider_rule import SpiderRule
from apscheduler.schedulers.twisted import TwistedScheduler
from apscheduler.triggers.cron import CronTrigger
import redis


# 加载设置
process = CrawlerProcess(get_scrapy_settings())

sched = TwistedScheduler()

server = redis.StrictRedis(host='localhost', port=6379, db=0)

spiderRuleKeys = server.lrange("spider_rule_keys", 0, -1)
for key in spiderRuleKeys:
    sr = SpiderRule(server.hgetall(key))
    if sr.enable:
        if sr.cron:
            sched.add_job(process.crawl, CronTrigger.from_crontab(sr.cron) , args=[GeneralSpider], kwargs={'rule': sr})
        else:
            sched.add_job(process.crawl, 'date', args=[GeneralSpider], kwargs={'rule': sr})

sched.start()
process.start(False)
