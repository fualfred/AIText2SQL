#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Optional
from common.logger import logger


def get_db_engine(db_type: str, db_user: Optional[str] = None, db_password: Optional[str] = None,
                  db_host: Optional[str] = None,
                  db_port: Optional[int] = None,
                  db_name: Optional[str] = None):
    try:
        db_type = db_type.lower()
        if db_type == "mysql":
            engine = create_engine(
                f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8", pool_size=10,
                max_overflow=5, pool_timeout=15, pool_recycle=1800, pool_pre_ping=True)
        elif db_type == "oracle":
            engine = create_engine(f"oracle+oracle://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
                                   pool_size=15,
                                   max_overflow=5, pool_timeout=10, pool_recycle=1800, pool_pre_ping=True)
        elif db_type == "sqlite":
            engine = create_engine(f"sqlite:///{db_name}", pool_size=10,
                                   max_overflow=5, pool_timeout=15, pool_recycle=1800, pool_pre_ping=True)
        else:
            logger.info(f"not support other db type:{db_type}")
            raise Exception("not support other db type")
        return engine
    except Exception as e:
        logger.info("connect exception:{}".format(e))
        raise e


def get_session(engine):
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    return session


def run_query_sql(session, sql_str: str):
    try:
        result = session.execute(text(sql_str)).fetchall()
        return result
    except Exception as e:
        logger.info("run sql error:{}".format(e))
        raise e


if __name__ == '__main__':
    pass
    # db_engine = get_db_engine("mysql", "root", "Aa123456", "localhost", 3306, "sakila")
    # sql = 'select * from sakila.actor where last_name= "GUINESS";'
    # print(text(sql))
    # result_ = run_query_sql(get_session(db_engine), sql)
    # print(result_)
