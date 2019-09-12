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
###引入自定义py文件
import DCDataBean
import staticJob
import collectLogger

SERVER_PORT=8888



appCollectLogger=collectLogger.collectLogger()
appLogger=appCollectLogger.getInstance()


''' example：
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
dcData={}

###结构同上，Map<List<Bean>>

class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        mpath,margs=urllib.splitquery(self.path) # ?分割
        if (mpath.startswith('/hourly')):
            self.do_hourly(mpath, margs)
        else:
            self.do_action(mpath, margs)
            
        return

    def do_POST(self):
        mpath,margs=urllib.splitquery(self.path)
        datas = self.rfile.read(int(self.headers['content-length']))
        self.do_action(mpath, datas)

    def do_action(self, path, data):
        self.outfile(path, data)
        self.outputtxt("do_action ok")
          
    def outfile(self, path, data):
        file_pre=os.environ["dc_filepath"]
        with open(file_pre+ path, "w") as f:
            f.write(data)
        f.close()

    def outputtxt(self, content):
        #指定返回编码
        enc = "UTF-8"
        content = content.encode(enc)
        f = io.BytesIO()
        f.write(content)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        shutil.copyfileobj(f,self.wfile)
    def do_hourly(self, path, margs):
     try:
       
    	appLogger.info("do_hourly,path====>"+path)
    	appLogger.info("do_hourly,margs====>"+margs)
    	ctTimeHost=path.split('_', 2)
    	ctTime=ctTimeHost[1]
        
        host=ctTimeHost[2]
        paramskv=margs.split('=')
        params=paramskv[1].split('@')
        appLogger.info("do_hourly,params="+''.join(params))
        for idx in range(1,len(params)):
        	kv=params[idx].split('_', 1)
        	key=kv[0]
        	totalNumber=int(kv[1])
        	dcBean=DCDataBean.DCDataBean(key,host,totalNumber)
        	dcBean.create(key,host,totalNumber)
        	dcData.setdefault(ctTime,{}).setdefault(key,{}).setdefault(host,dcBean)
        
       ##赋值
        appLogger.info("---dcData="+ str(dcData)) 	
       
        self.outputtxt("do_hourly ok,host="+host+",")
     except Exception , err:
          appLogger.error("error do_hourly",err)
          traceback.print_exc()
          
     finally:
          appLogger.info("finish do_hourly success")      
        

if __name__ == "__main__":
    print "Starting server"
    print os.getenv('dc_filepath')
    # Start a simple server, and loop forever
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('0.0.0.0', SERVER_PORT), MyRequestHandler)
    t1 = threading.Thread(target=staticJob.staticDayJob, args=(0,0))
    t1.setDaemon(True)
    t1.start()
    t2 = threading.Thread(target=staticJob.staticHourlyJob, args=(0,dcData))
    t2.setDaemon(True)
    t2.start()
    print "Starting server....===== startup ok ====="
    sys.stdout.flush()
    server.serve_forever()

