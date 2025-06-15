#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading


class SessionPool:
    _instance_lock = threading.Lock()
    _session_pool = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super().__new__(cls)
                    cls._instance._init_session_pool()
        return cls._instance

    def _init_session_pool(self):
        self._session_pool = {}

    def get_session_pool(self):
        return self._session_pool


class HandleSessionPool:
    _instance_lock = threading.Lock()

    def __init__(self, session_pool):
        self._session_pool = session_pool

    def add_session(self, key, session):
        with self._instance_lock:
            if key not in self._session_pool:
                self._session_pool[key] = session

    def get_session(self, key):
        with self._instance_lock:
            return self._session_pool.get(key, None)

    def remove_session(self, key):
        with self._instance_lock:
            if key in self._session_pool:
                del self._session_pool[key]
            return self._session_pool

    def update_session(self, key, session):
        with self._instance_lock:
            if key in self._session_pool:
                self._session_pool[key] = session


session_pools = SessionPool().get_session_pool()
session_handle = HandleSessionPool(session_pools)
