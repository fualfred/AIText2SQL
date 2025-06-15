#!/usr/bin/python
# -*- coding: utf-8 -*-
import streamlit as st

from common.logger import logger

st.set_page_config(page_title="app", layout="wide")
sql_agent_page = st.Page("./pages/agent.py", title="🤖Text2SQL助手", default=True)
pg = st.navigation([sql_agent_page])

pg.run()
