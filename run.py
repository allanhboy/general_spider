# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from apscheduler.schedulers.twisted import TwistedScheduler
from apscheduler.triggers.cron import CronTrigger

from settings import get_scrapy_settings
from spiders.general_spider import GeneralSpider
from db import DBSession,Config, SpiderRule


session = DBSession()
config = session.query(Config).filter(Config.id == 1).one()

# 加载设置
process = CrawlerProcess(get_scrapy_settings(config))

sched = TwistedScheduler()

spiderRules = session.query(SpiderRule).filter(SpiderRule.enable).all()

for sr in spiderRules:
    if sr.cron:
        sched.add_job(process.crawl, CronTrigger.from_crontab(sr.cron) , args=[GeneralSpider], kwargs={'rule': sr})
    else:
        sched.add_job(process.crawl, 'date', args=[GeneralSpider], kwargs={'rule': sr})

session.close()

sched.start()
process.start(False)
