#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import urllib2
import json
from time import sleep

class QueryIpAddressException(Exception) :
    def __init__(self,ip) :
        Exception.__init__(self,ip)
        self.ip = ip

class QueryIpInfo() :
    def __init__(self,count = 1024,times = 5) :
        self.iptable = dict()
        self.count = count
        self.times = times

    def query(self,ip) :
        ip_info = self.iptable.get(ip)
        if ip_info != None :
            return ip_info
        else :
            if len(self.iptable) > self.count :
                self.iptable.clear()
            return self.__query__(ip)
                
    
    def __query__(self,ip) :
        url = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s'%ip
        times = self.times
        while times > 0 :
            try :
                times = times - 1
                link = urllib2.urlopen(url)
                data = json.loads(link.read())
                link.close()
                if data['code'] != 0 :
                    raise QueryIpAddressException(ip)
                self.iptable[ip] = data['data']
                return (data['data'])
            except (Exception) as e :
                if times > 0:
                    sleep(1)
                    pass
                else :
                    raise QueryIpAddressException(e,ip)

queryip = QueryIpInfo()