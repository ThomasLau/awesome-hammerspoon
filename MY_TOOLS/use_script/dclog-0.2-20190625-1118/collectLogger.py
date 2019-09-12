#!/usr/bin/python
#encoding=utf-8
'''''
基于BaseHTTPServer的http server实现，包括get，post方法，get参数接收，post参数接收。
'''
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import io,shutil
import urllib
import os, sys
import datetime
import time, threading
import logging
import json
import urllib2
import traceback



from logging.handlers import TimedRotatingFileHandler
LOG_FILE = "logs/app.log"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE,when='D',interval=1,backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)



class collectLogger:
    def getInstance(self):
         return logger
    