#!/usr/bin/python
# -*- coding: utf-8 -*-
import os


class Settings:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL = "deepseek-r1"
    COMPANY = "tencent"  # deepseek/ollama/tencent
    LOGS_PATH = os.path.join(BASE_PATH, "logs")
    DB_SCHEMA_DIR_PATH = os.path.join(BASE_PATH, "schema")
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 30
    db_configs = {
        "sakila": {
            "host": "localhost",
            "port": 3306,
            "username": "root",
            "password": "Aa123456",
            "dialect": "mysql",
            "db_id": "sakila",
            "comment": "sakila数据库"
        }
    }


settings = Settings()
