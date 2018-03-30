from sqlalchemy import create_engine, Column, String, Integer, Boolean, BigInteger, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 初始化数据库连接:
engine = create_engine('mysql+pymysql://root:djejeUJ3qj^su22@101.37.179.99:3306/syzb_spider_db')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


# 定义Config对象:
class Config(Base):
    # 表的名字:
    __tablename__ = 'spider_config'

    # 表的结构:
    id = Column(Integer, primary_key=True)
    delta_fetch_enabled = Column(Boolean)
    delta_fetch_redis_db = Column(Integer)
    delta_fetch_redis_host = Column(String)
    delta_fetch_redis_password = Column(String)
    delta_fetch_redis_port = Column(Integer)

    oss_enabled = Column(Boolean)
    oss_bucket_name = Column(String)
    oss_endpoint = Column(String)
    oss_key_id = Column(String)
    oss_key_secret = Column(String)


class SpiderRule(Base):
    __tablename__ = 'spider_rule'

    id = Column(Integer, primary_key=True)
    spider_clsass = Column(String)
    name = Column(String)
    start_urls = Column(String)
    allowed_domains = Column(String)
    enable = Column(Boolean)
    cron = Column(String)
    encoding = Column(String)
    next_page = Column(String)
    allow_url = Column(String)

class SpiderTask(Base):
    __tablename__ = 'spider_task'

    id = Column(BigInteger, primary_key= True)
    spider_name = Column(String)
    spider_rule_id = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String)
