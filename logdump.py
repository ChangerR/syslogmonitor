#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from logparser import parser
from ipsearch import queryip,QueryIpAddressException
import json
import re
import sys
from pymongo import MongoClient
import os

class Mongo() :
    def __init__(self,ip,port,db,user,passwd) :
        url = 'mongodb://' + ip + ':' + str(port)
        self.client = MongoClient(url)
        self.db = self.client[db]
        if db != None :
            self.db.authenticate(user,passwd)
        
    def insert(self,collection,obj) :
        return self.db[collection].insert(obj)
    
    def close(self) :
        self.client.close()
        
class Dump() :
    def __init__(self) :
        self.prog = re.compile("^Addr=\('(\d+\.\d+\.\d+\.\d+)',\s+\d+\)\s+\<level\>=\<\d+\>\s+\<time\>=\<([^\>]+)\>\s+\<log\>\s+=\>\s+(.*)$",re.M|re.I)

    def dump(self,log) :
        loglist = log.split('->')
        if len(loglist) != 2 :
            return None
        logbody = loglist[1].lstrip()
        matchObj = self.prog.match(logbody)
        if matchObj != None :
            result = parser.parse(matchObj.group(3))
            if result != None :
                failed_times = 10
                ip_info = None
                while failed_times > 0 :
                    try :
                        failed_times = failed_times - 1
                        ip_info = queryip.query(result['ip'])
                        break
                    except :
                        pass
                if ip_info != None :
                    result['country'] = ip_info['country']
                    result['city'] = ip_info['city']
                    result['isp'] = ip_info['isp']
                else :
                    result['country'] = ''
                    result['city'] = ''
                    result['isp'] = ''
                result['src'] = matchObj.group(1)
                result['time'] = matchObj.group(2)
                return result

def dumpFile(filename,dump,mongo) :
    fd = open(filename,'r')
    
    data = fd.readline(1024)
    while data != '' :
        ret = dump.dump(data)
        if ret != None :
            #print(json.dumps(ret,ensure_ascii=False).encode('utf8'))
            mongo.insert('record',ret)
        data = fd.readline(1024)
    fd.close()

if __name__ == '__main__' :
    if len(sys.argv) < 2 :
        print('Please input log file!')
        sys.exit(1)
    logfile = sys.argv[1]
    dump = Dump()
    mongo = Mongo('192.168.1.8',27017,'syslog','syslog','syslog')
    os.listdir(logfile)
    if os.path.isdir(logfile) :
        files = filter( lambda f : re.match('syslog-(\d+).log',f,re.I) != None ,os.listdir(logfile))
        files.sort(key = lambda f : int(re.match('syslog-(\d+).log',f,re.I).group(1)))
        for f in files : 
            dumpFile(os.path.join(logfile,f),dump,mongo)
    else :
        dumpFile(logfile,dump,mongo)
    mongo.close()