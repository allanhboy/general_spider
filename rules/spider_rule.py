# -*- coding: utf-8 -*-
class SpiderRule:

    def __init__(self, ent):
        self.id = int(ent.get(b'id', b'0').decode('utf-8'))
        self.name = ent.get(b'name', b'').decode('utf-8')
        self.start_urls = [x for x in ent.get(
            b'start_urls', b'').decode('utf-8').split(',') if x]
        self.allowed_domains = [x for x in ent.get(
            b'allowed_domains', b'').decode('utf-8').split(',') if x]
        self.enable = ent.get(b'enable', b'False').decode('utf-8') == "True"
        self.cron = ent.get(b'cron', b'').decode('utf-8')
        self.encoding = ent.get(b'encoding', b'utf-8').decode('utf-8')

    def __str__(self):
        return 'id=%s&name=%s&start_urls=%s&allowed_domains=%s&enable=%s&cron=%s' % (self.id, self.name, self.start_urls, self.allowed_domains, self.enable, self.cron)
