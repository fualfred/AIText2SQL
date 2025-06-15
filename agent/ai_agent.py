#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Dict, List

from langchain.agents import initialize_agent, AgentType
from sqlalchemy import text

from common.get_llm import get_llm
from langchain_community.document_loaders import TextLoader
from common.logger import logger
from langchain.tools import tool
import os
from config.settings import settings
from common.session_pool import session_handle
from common.db_engine import get_db_engine, get_session
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from common.schema_engine import SchemaEngine
from common.utils import format_schema_str
from langchain.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field


class SqlResult(BaseModel):
    exec_str: str = Field(str, description="最终执行的sql语句")
    answer: List = Field(List, description="执行sql语句的返回结果",
                         examples=[{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Joan'}])


if not os.path.exists(settings.DB_SCHEMA_DIR_PATH):
    os.mkdir(settings.DB_SCHEMA_DIR_PATH)


def load_schema(db_name: str) -> str:
    schema_path = os.path.join(settings.DB_SCHEMA_DIR_PATH, db_name) + ".txt"
    data = TextLoader(schema_path).load()
    schema = ""
    for d in data:
        schema = schema.join(d.page_content)
    return schema


def get_exec_session(db_id):
    if not session_handle.get_session(db_id):
        db_config = settings.db_configs.get(db_id, None)
        engine = get_db_engine(db_config['dialect'], db_config['username'], db_config['password'], db_config['host'],
                               db_config['port'],
                               db_config['db_id'])
        # engine = get_db_engine(dialect, username, password, host, port, db_id)
        session = get_session(engine)
        session_handle.add_session(db_id, session)
    return session_handle.get_session(db_id)


def write_schema(db_name: str):
    db_name_file = f"{db_name}.txt"
    if not os.path.exists(os.path.join(settings.DB_SCHEMA_DIR_PATH, db_name_file)):
        db_config = settings.db_configs.get(db_name, None)
        if not db_config:
            raise Exception("db_name not found")

        engine = get_db_engine(db_config['dialect'], db_config['username'], db_config['password'], db_config['host'],
                               db_config['port'],
                               db_config['db_id'])

        schema_engine = SchemaEngine(engine)
        schema_str = schema_engine.mschema.to_mschema()
        final_schema_str = format_schema_str(schema_str, db_name)
        with open(os.path.join(settings.DB_SCHEMA_DIR_PATH, db_name_file), "w") as f:
            f.write(final_schema_str)


@tool
def run_query_sql(db_id, sql_str: str):
    """
    传入数据库名和生成的sql语句执行，返回执行结果
    :param db_id:
    :param sql_str:
    :return:
    """
    try:
        logger.info("run_query_sql:{}".format(sql_str))
        if not session_handle.get_session(db_id):
            db_config = settings.db_configs.get(db_id)
            engine = get_db_engine(db_config['dialect'], db_config['username'], db_config['password'],
                                   db_config['host'],
                                   db_config['port'],
                                   db_config['db_id'])
            session = get_session(engine)
            session_handle.add_session(db_id, session)
        exec_session = session_handle.get_session(db_id)

        result = exec_session.execute(text(sql_str))

        return result.mappings().all()
    except Exception as e:
        logger.info("run sql error:{}".format(e))
        raise e


system_prompt = """
    你是一个能够进行数据分析的智能体，当用户输入数据分析需求时，你需要将提取数据库的db_id和转换成可以执行的SQL语句，并调用工具执行，只需要返回SQL执行的结果，对执行结果进行总结输出
     
    你可以一步一步来分析需求，最终确定需要生成的查询SQL
    为了提高SQL生成的准确行，请从不同纬度一次性生成三个SQL，并投票选出最合适的SQL来执行
    当执行SQL失败时，你需要更具错误信息来修正SQL再重新尝试执行
    
    ## SQL要求 ##
    1. SQL语句必须符合语法规范
    2. SQL语句必须能够正确执行
    3.不能生成Drop Update、Create、Delete语句
    4.SELECT语句不要返回全部字段，返回用户问题关键信息即可
    5.日期的字段要转化格式'%Y-%m-%d %H:%i:%s'字符表示，如2025-01-01 00:00:00
    
    
    ### 工具 ###
    run_query_sql： 传入数据库名和生成的sql语句执行，并返回执行结果
"""


# parser = PydanticOutputParser(pydantic_object=SqlResult)

# system_prompt_template = PromptTemplate(template=system_prompt,
# partial_variables={"format_instructions": parser.get_format_instructions()})
# system_prompt_str = system_prompt_template.format()
# print(system_prompt_str)


def get_agent():
    # 创建系统提示字符串，已经注入格式指令

    # logger.info("system_prompt_str:{}".format(system_prompt_str))
    agent_executor = initialize_agent(tools=[run_query_sql], llm=get_llm(), verbose=True,
                                      agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                                      handle_parsing_errors=True)
    return agent_executor


user_prompt = """
    你是一个{dialect}数据分析专家，你被给了数据的schema以下
    
    【Schema】
    
    {schema}
    
   【Question】
   
    {question}
    
    阅读问题和理解数据库的schema，并生成SQL语句
"""


def invoke(agent, dialect, db_name: str, msg: str):
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)]).invoke(
        {"dialect": dialect, "schema": load_schema(db_name), "question": msg})

    return agent.invoke(prompt)


if __name__ == '__main__':
    # print(run_query_sql("sakila", "select * from actor"))
    pass
    # response = invoke("sakila", "请查找姓名是GUINESS的演员")
    # print(f"response:{response}")
