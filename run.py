# -*- coding: utf-8 -*-
from scrapy.crawler import CrawlerProcess
from apscheduler.schedulers.twisted import TwistedScheduler
from apscheduler.triggers.cron import CronTrigger

from settings import get_scrapy_settings
from spiders.general_spider import GeneralSpider
from db import DBSession,Config, SpiderRule

# from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from twisted.web import server, resource
from twisted.internet import reactor, endpoints, defer


configure_logging()
session = DBSession()
config = session.query(Config).filter(Config.id == 1).one()

runner = CrawlerRunner(get_scrapy_settings(config))

@defer.inlineCallbacks
def crawl(rule):
    dot = rule.spider_clsass.rindex('.')
    module, name = rule.spider_clsass[:dot], rule.spider_clsass[dot+1:]
    if (module == GeneralSpider.__module__ and name == GeneralSpider.__name__) :
        yield runner.crawl(GeneralSpider, rule)

        

sched = TwistedScheduler()
# sched.add_jobstore('sqlalchemy', url='mysql+pymysql://root:djejeUJ3qj^su22@101.37.179.99:3306/apscheduler')

spiderRules = session.query(SpiderRule).filter(SpiderRule.enable, SpiderRule.cron).all()


for sr in spiderRules:
    if sr.cron:
        sched.add_job(crawl, CronTrigger.from_crontab(sr.cron) , args=[sr], name=sr.name, id='%s'%sr.id)
    # else:
    #     sched.add_job(crawl, 'date', args=[sr],  name=sr.name, id='%s'%sr.id)
session.close()


class Simple(resource.Resource):
    # count = 0
    def __init__(self, scheduler):
        self.scheduler = scheduler
        # self.jobs = works
        
        super(Simple, self).__init__()
    
    isLeaf = True
    def render_GET(self, request):
        # self.count +=1
        
        sessionweb = DBSession()
        spiderRule = sessionweb.query(SpiderRule).filter(SpiderRule.enable and SpiderRule.cron == None).one()
        # spiderRule.name = '%s-%s'%(spiderRule.name,self.count)
        # print('我来了%s次!!!'%spiderRule.name)
        self.scheduler.add_job(crawl, 'date', args=[spiderRule],  name=spiderRule.name, id='%s'%spiderRule.id, replace_existing=True)
        
        sessionweb.close()
        request.setHeader("Content-Type", "text/html; charset=utf-8")
        return ("<html>Hello, world!</html>").encode('utf-8')
    
    def render_POST(self, request):
        pass





site = server.Site(Simple(sched))
endpoint = endpoints.TCP4ServerEndpoint(reactor, 8080)
endpoint.listen(site)

sched.start()
reactor.run() 