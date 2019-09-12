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

from logging.handlers import TimedRotatingFileHandler
LOG_FILE = "logs/app.log"
ES="http://10.135.20.38:9200/dclog/hourly/"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = TimedRotatingFileHandler(LOG_FILE,when='D',interval=1,backupCount=30)
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)
fh.setFormatter(formatter)
logger.addHandler(fh)
'''
logging.basicConfig(level=logging.INFO,
                    filename='output.log',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')
logger = logging.getLogger(__name__)
'''


data={}
data_ip={}
bizdcDic={'110002':'packet','110007':'user','110008':'friend','111002':'heartbeat','111000':'clientubt'}
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
class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        mpath,margs=urllib.splitquery(self.path) # ?分割
        if (mpath.startswith('/hourly')):
            self.do_hourly(mpath, margs)
        else:
            self.do_action(mpath, margs)
        # self.outputtxt("ok")
        return

    def do_POST(self):
        mpath,margs=urllib.splitquery(self.path)
        datas = self.rfile.read(int(self.headers['content-length']))
        self.do_action(mpath, datas)

    def do_action(self, path, data):
        self.outfile(path, data)
            # self.outputtxt(path + args )
    def outfile(self, path, data):
        file_pre=os.environ["dc_filepath"]
        # print(file_pre)
        with open(file_pre+ path, "w") as f:
            # print data
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
    	# print "%s d:%s - %s" %(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),path, margs)
    	logger.info("path:"+path+":"+ str(margs))
    	info=path.split('_', 2)
        ctTime=info[1]
        host=info[2]
        paramskv=margs.split('=')
        params=paramskv[1].split('@')
        for idx in range(1,len(params)):
        	kv=params[idx].split('_', 1)
        	key=kv[0]
        	amount=int(kv[1])
        	data.setdefault(ctTime,{}).setdefault(key,{}).setdefault(host,amount)
                data_ip.setdefault(ctTime,{}).setdefault(host,{}).setdefault(key,amount)

def doSth():
    # app_pre=os.environ["dc_home"]
    path=os.path.abspath(sys.argv[0])
    app_pre=path[:path.rfind("/")]
    os.system(app_pre + "/all_sts_hourly")
    time.sleep(60)

def job(h=0, m=0):
    while True:
        while True:
            now = datetime.datetime.now()
            if now.hour==5 and now.minute==30:
            # if now.minute%2==1:
                break
            time.sleep(30)
        doSth()
        
###统计并写入es        
def static2ES():
     last_str=(datetime.datetime.now()-datetime.timedelta(hours=1)).strftime("%Y%m%d%H")
     staticByBizKey(last_str)
     staticByStashIP(data_ip ,last_str)
     if datetime.datetime.now().minute>=40:
        logger.info("pop data :"+last_str+" start")
    	if data.get(last_str,{}):
    		data.pop(last_str)
    	if data_ip.get(last_str,{}):
    		data_ip.pop(last_str)	
    	logger.info("pop data :"+last_str+" finish")	
     time.sleep(60)
     
##按小时统计 并写入es
def staticByBizKey(last_str):
    # post 前一小时结果，ifnow.minute >= 40 清空
    post_data={}
    for key, dcmap in data.get(last_str,{}).items():
    	total=0
    	for value in dcmap.values():
    		total=total+value
    	post_data[bizdcDic.get(key,"def")] = total
    logger.info("staticByBizKey:"+last_str+":"+ str(post_data))
    # post
    if post_data: # only when not empty
        try:
          timestp=(datetime.datetime.now()-datetime.timedelta(hours=9)).strftime("%Y-%m-%dT%H:%M:%SZ")
          post_data['@timestamp']=timestp
          post_es(last_str, post_data)
        except Exception,err:
          logger.error("error postting es")
   
    
    
 ###按ip写入   
def staticByStashIP(data ,last_str):
    ##业务key dc数据=ip:count
      post_data2=data
      logger.info("staticByStashIP:"+last_str+":"+ str(post_data2)) 
      if post_data2: # only when not empty
        try:
          timestp=(datetime.datetime.now()-datetime.timedelta(hours=9)).strftime("%Y-%m-%dT%H:%M:%SZ")
          post_data2['@timestamp']=timestp
          post_es(last_str+"_detail", post_data2)
        except Exception,err:
          logger.error("error staticByStashIP es")
              
    
def post_es(id, to_json):
    es_url=ES+id
    headers = {'content-type': 'application/json'}
    request = urllib2.Request(es_url, data=json.dumps(to_json), headers=headers)
    response = urllib2.urlopen(request)
    res=response.read()
    logger.info("es resp:"+res)

def job2(h=0, m=0):
    while True:
        while True:
            now = datetime.datetime.now()
            if now.minute==15 or now.minute==45:
            #if now.minute>5:
                break
            time.sleep(30)
        static2ES()

if __name__ == "__main__":
    print "Starting server"
    print os.getenv('dc_filepath')
    # Start a simple server, and loop forever
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('0.0.0.0', 8888), MyRequestHandler)
    t1 = threading.Thread(target=job, args=(0,0))
    t1.setDaemon(True)
    t1.start()
    t2 = threading.Thread(target=job2, args=(0,0))
    t2.setDaemon(True)
    t2.start()
    print "Starting server....===== startup ok ====="
    sys.stdout.flush()
    server.serve_forever()

