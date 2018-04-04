# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, BigInteger
from db  import Base


class Article(Base):
    # 表的名字:
    __tablename__ = 'article'

    # 表的结构:
    id = Column(BigInteger, primary_key=True)
    title = Column(String)
    url = Column(String)
    body = Column(String)
    publish_time = Column(String)
    source_site = Column(String)