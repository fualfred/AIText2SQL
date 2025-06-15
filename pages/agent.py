#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st
import time
import streamlit_antd_components as sac
from agent.ai_agent import get_agent, invoke
from config.settings import settings
from common.logger import logger

# 初始化
st.markdown("""
<style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stRadio [role=radiogroup] {
        gap: 8px;
    }
    .stRadio [data-testid=stMarkdown] {
        font-size: 16px;
        padding: 12px;
        border-radius: 4px;
        transition: all 0.3s;
    }
    .stRadio [data-testid=stMarkdown]:hover {
        background-color: #e9ecef;
    }
    .st-eb {
        padding: 20px !important;
    }
     .stSelectbox > div[data-baseweb="select"] {
        width: 180px; /* 自定义宽度 */
    }
</style>
""", unsafe_allow_html=True)
st.subheader("🤖Text2SQL助手")
database = st.selectbox("请选择数据库", ("sakila", "test"))
dialect = settings.db_configs.get(database)["dialect"]

agent = get_agent()

sac.divider(label='Text2SQL助手', icon='robot', align='center', color='gray')


def st_write_output(data):
    if isinstance(data, dict):
        if 'exec_str' in data:
            st.write(f"执行SQL语句：\n{data.get('exec_str')}\n ,执行的结果：\n", unsafe_allow_html=True)
        if 'answer' in data:
            st.write(pd.DataFrame(data.get('answer')))
    else:
        st.markdown(data)


def dataframe_stream_generator(df, chunk_size=5):
    """
    流式生成DataFrame分块
    参数:
        df (pd.DataFrame): 原始数据集
        chunk_size (int): 每批加载行数
    """
    total = len(df)

    # 先输出表头
    # yield df.head(0).to_markdown(index=False) + "\n"

    # 分块加载数据
    for i in range(0, total, chunk_size):
        chunk = df.iloc[i:i + chunk_size]

        # 转换为Markdown表格（带进度）
        md_table = chunk.to_markdown(index=False) + f"\n\n**已加载 {min(i + chunk_size, total)}/{total} 行**"

        yield md_table
        time.sleep(0.1)  # 控制加载速


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant",
                                  "content": "你好，我是Text2SQL助手，请选择数据库，我会尽力帮你查找数据！"}]

    # Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st_write_output(message["content"])
        else:
            st.markdown(message["content"])

    # React to user input

if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("...正在查询中，请稍等...", show_time=True):
        response = invoke(agent, dialect, database, prompt.strip())
        logger.info(f"返回的结果{response['output']}")
        output = response['output']

        # response_str_SQL = f"执行SQL语句：\n{output.get('exec_str')}\n ,执行的结果：\n"
        # response_str_answer = pd.DataFrame(output['answer']).to_string()

        # response_str = response_str_SQL + response_str_answer

        # response_str = st.write_stream()
        # res_data = f"查询的结果如下:\n{pd.DataFrame(response['output'])}"
        # Display assistant response in chat message container
        # response_str = "查询的结果如下:\n" + pd.DataFrame(list(response['output']))
        with st.chat_message("assistant"):
            st_write_output(output)
            # st.markdown(response_str, unsafe_allow_html=True)
        # st.write(response_str, unsafe_allow_html=True)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": output})
