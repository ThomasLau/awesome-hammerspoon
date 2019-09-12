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
import DCDataBean
###todo log
import collectLogger

jobCollectLogger=collectLogger.collectLogger()
jobLogger=jobCollectLogger.getInstance()


ES_URL="http://10.135.20.38:9201/dclog/hourly/"

bizdcDic={'110002':'packet','110007':'user','110008':'friend','111002':'heartbeat','111000':'clientubt'}



###data数据格式 todo 修改为对象
'''
{ 
  '2019051303':{
	  '111000':{
	    '10.135.16.44':42,
	    '10.135.16.45':42
	  },
	  '111002':{
	    '10.135.16.44':42,
	    '10.135.16.45':42
	  }
	}
}
'''

def staticDaily():
    # app_pre=os.environ["dc_home"]
    path=os.path.abspath(sys.argv[0])
    app_pre=path[:path.rfind("/")]
    os.system(app_pre + "/all_sts_hourly")
    time.sleep(60)

def staticDayJob(h=0, m=0):
    while True:
        while True:
            now = datetime.datetime.now()
            if now.hour==5 and now.minute==30:
            # if now.minute%2==1:
                break
            time.sleep(30)
        staticDaily()

def staticHourly(dcData,last_hour):
    jobLogger.info("begin to static ,last_hour="+last_hour+",dcData="+str(dcData))
    # post 前一小时结果，ifnow.minute >= 40 清空
   
    post_data={}
    for  key, dcmap  in dcData.get(last_hour,{}).items():
         #jobLogger.info("key="+str(key))
         #jobLogger.info("dcmap"+str(dcmap))
         total=0
         for dcBean in dcmap.values():
    		total=total+dcBean.totalNumber
    	 post_data[bizdcDic.get(key,"def")] = total
    jobLogger.info("post:"+last_hour+":"+ str(post_data))
    
    # post
    if post_data: # only when not empty
        try:
          timestp=(datetime.datetime.now()-datetime.timedelta(hours=9)).strftime("%Y-%m-%dT%H:%M:%SZ")
          print "timestp="+timestp
          post_data['@timestamp']=timestp
          post_es(last_hour, post_data)
          jobLogger.info("begin to pop dcData")
    	  if dcData.get(last_hour,{}):
    		dcData.pop(last_hour)
        except Exception,err:
          jobLogger.error("error postting es")
    '''
    if datetime.datetime.now().minute>=40:
        jobLogger.info("begin to pop dcData")
    	if dcData.get(last_hour,{}):
    		dcData.pop(last_hour)
    '''	
    time.sleep(60)
    
    
def post_es(id, to_json):
    url=ES_URL+id
    headers = {'content-type': 'application/json'}
    request = urllib2.Request(url, data=json.dumps(to_json), headers=headers)
    response = urllib2.urlopen(request)
    res=response.read()
    jobLogger.info("es resp:"+res)

def staticHourlyJob(self,dcData):
    while True:
        while True:
             jobLogger.info("now,dcData="+str(dcData))
             now = datetime.datetime.now()
             ##15,45
             if now.minute==57 or now.minute>1:
                 break
             print "i am working now............"
             time.sleep(30)
        last_hour=(datetime.datetime.now()-datetime.timedelta(hours=1)).strftime("%Y%m%d%H")
        staticHourly(dcData,"2019053016")
        
        
        

