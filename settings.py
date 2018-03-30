# -*- coding: utf-8 -*-
from scrapy.settings import Settings


def get_scrapy_settings(config):

    settings = Settings()

    # 设置默认请求头
    settings.set("DEFAULT_REQUEST_HEADERS", {
        'Accept': 'text/html, application/xhtml+xml, application/xml',
        'Accept-Language': 'zh-CN,zh;q=0.8'}
    )

    # 注册自定义中间件，激活切换UA的组件和切换代理IP的组件
    settings.set("DOWNLOADER_MIDDLEWARES", {
        'middlewares.useragent_middleware.UserAgent': 1,
        'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
    })

    settings.set("SPIDER_MIDDLEWARES", {
        'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 100,
        'middlewares.deltafetch_middleware.DeltaFetch': 101,
    })

    # 设置爬取间隔
    settings.set("DOWNLOAD_DELAY", 5)

    # 禁用cookies
    settings.set("COOKIES_ENABLED", True)
    # settings.set("COOKIES_DEBUG", True)

    # 设定是否遵循目标站点robot.txt中的规则
    settings.set("ROBOTSTXT_OBEY", False)

    # Enables scheduling storing requests queue in redis.
    # settings.set("SCHEDULER", "scrapy_redis.scheduler.Scheduler")

    # Ensure all spiders share same duplicates filter through redis.
    # settings.set("DUPEFILTER_CLASS", "scrapy_redis.dupefilter.RFPDupeFilter")

    # 设置统计数据到redis
    # settings.set('STATS_CLASS', 'redis_statscol.RedisStatsCollector')

    settings.set('ITEM_PIPELINES', {
        'pipelines.OSSPipeline': 300,
    })

    # 设置OSS
    settings.set('OSS_ENABLE', config.oss_enabled)
    settings.set('OSS_KEY_ID', config.oss_key_id)
    settings.set('OSS_KEY_SECRET', config.oss_key_secret)
    settings.set('OSS_ENDPOINT', config.oss_endpoint)
    # settings.set('OSS_ENDPOINT', 'http://oss-cn-hangzhou-internal.aliyuncs.com')
    settings.set('OSS_BUCKET_NAME', config.oss_bucket_name)

    # 设置DeltaFetch.redis
    settings.set('DELTA_FETCH_ENABLED', config.delta_fetch_enabled)
    settings.set('DELTA_FETCH_REDIS_HOST', config.delta_fetch_redis_host)
    settings.set('DELTA_FETCH_REDIS_PORT', config.delta_fetch_redis_port)
    settings.set('DELTA_FETCH_REDIS_DB', config.delta_fetch_redis_db)
    settings.set('DELTA_FETCH_REDIS_PASSWORD', config.delta_fetch_redis_password)

    # scrapy_jsonrpc
    # settings.set('EXTENSIONS', {'scrapy_jsonrpc.webservice.WebService': 500,})
    # settings.set('JSONRPC_ENABLED', False)

    return settings
