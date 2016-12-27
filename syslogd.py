#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import socket
import sys
import re
import smtplib
from email.mime.text import MIMEText
import logging
import urllib2
import json
from logging.handlers import RotatingFileHandler
import datetime
import os
import signal
import select

global g_running
g_running = True

class SyslogParseException(Exception) :
	def __init__(self,log) :
		Exception.__init__(self,log)
		self.log = log

class LoggingSuccessParseException(Exception) :
	def __init__(self,log) :
		Exception.__init__(self,log)
		self.log = log
	
class QueryIpAddressException(Exception) :
	def __init__(self,ip) :
		Exception.__init__(self,ip)
		self.ip = ip
		
def parseSuccessLogging(log) :
	matchObj = re.match(r"^dropbear\[\d+\]:\sPassword\sauth\ssucceeded\sfor\s\'([^\']+)\'\sfrom\s(\d+\.\d+\.\d+\.\d+):\d+",log,re.I|re.M)
	if matchObj != None :
		return (matchObj.group(1),matchObj.group(2))
	else :
		raise LoggingSuccessParseException(log)
		
def parseSyslog(log) :
	matchObj = re.match(r'^<(\d+)>(\w+\s\d+\s\d+:\d+:\d+)\s(.*)$',log,re.I|re.M)
	if matchObj != None :
		t = datetime.datetime.strptime(matchObj.group(2),'%b %d %H:%M:%S')
		t = t.replace(year=datetime.datetime.now().year)
		return (matchObj.group(1),t.strftime('%y-%m-%d %H:%M:%S'),matchObj.group(3))
	else :
		raise SyslogParseException(log)
		
def recvSyslog(port,handler) :
	try:
		sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		sock.bind(("0.0.0.0",port))
	except:
		print("bind addreess failed,please check!")
		sys.exit(1)
	readlist = []
	readlist.append(sock)
	while g_running:
		try:
			can_read,can_write,can_x = select.select(readlist,[],[],100)
			if len(can_read) > 0 :
				for s in can_read :
					data,addr = s.recvfrom(1024)
					handler(data,addr)
			print 'running:' + str(g_running)
		except (socket.error,socket.timeout),e:
			pass
		except select.error,e:
			logging.error(e)


def emailMessage(server,username,password,from_addr,to_addr,title,ip,user,more) :
	try :
		msg = u'''
		<h1>未知用户连入系统</h1>
		<table style="border:solid 1px black;">
		<tr>
		<th>ip地址</th>
		<th>用户</th>
		<th>备注</th>
		</tr>
		<tr>
			<td style="color:red;">%s</td><td>%s</td><td>%s</td>
		</tr>
		</table>
		'''% (ip,user,more.decode('utf8'))
		sm = smtplib.SMTP(server,timeout=20)
		sm.ehlo()
		sm.starttls()
		sm.login(username,password)
		sm.ehlo()
		message = MIMEText(msg.encode('utf8'), 'html', 'utf-8')
		message['From'] = from_addr
		message['To'] = to_addr
		message['Subject'] = title
		sm.sendmail(from_addr,to_addr,message.as_string())
		sm.quit()
	except smtplib.SMTPException:
		print "failed to send email!!"
	except socket.gaierror :
		print "Unknown server hostname"
	
def queryIp(ip) :
	url = 'http://ip.taobao.com/service/getIpInfo.php?ip=%s'%ip
	try :
		link = urllib2.urlopen(url)
		data = json.loads(link.read())
		link.close()
		if data['code'] != 0 :
			raise QueryIpAddressException(ip)
		return (data['data'])
	except (urllib2.URLError,urllib2.URLError) :
		raise QueryIpAddressException(ip)
	
def formatIpRes(data) :
	return (data['country']  + ' ' + data['city'] + ' ' + data['isp']).encode('utf8')
	
def handleMessage(data,addr) :
	try :
		(level,t,log) = parseSyslog(data)
		logging.info('Addr=%s <level>=<%s> <time>=<%s> <log> => %s'%(addr,level,t,log))
		(user,ip) = parseSuccessLogging(log)
		more = formatIpRes(queryIp(ip))
		emailMessage(g_config['mailsmtp'],g_config['mailuser'],g_config['mailpass'],g_config['mailuser'],g_config['mailto'],'%s connect'%(ip),ip,user,more)
	except SyslogParseException as e:
		logging.error('Syslog parse error:%s' % (e.log))
	except LoggingSuccessParseException as e:
		pass
	except QueryIpAddressException as e:
		logging.error('failed to queryIp:%s' % (e.ip))
	
def daemon(pidfile) :
	try:
		if os.fork() > 0 :
			sys.exit(0)
	except OSError, e:
		logging.error("try to start daemon failed!")
	try:
		pid = open(pidfile,'w')
		pid.write('%d\n' % (os.getpid()))
		pid.flush()
		pid.close()
	except IOError,e:
		logging.error('cannot open this file:%s' % (pidfile))
		sys.exit(1)
	for f in sys.stdout, sys.stderr:
		f.flush()
	si = open(os.devnull, 'r')
	so = open(os.devnull, 'a+')
	se = open(os.devnull, 'a+', 0)
	os.dup2(si.fileno(), sys.stdin.fileno())
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())

def parseConfig(filename) :
	try :
		conf_file = open(filename,'r')
		data = conf_file.read()
		config = json.loads(data)
		return config
	except IOError,e:
		logging.error('read config file failed,please set config file')
		sys.exit(1)
	except ValueError,e:
		logging.error(e)
		sys.exit(1)
		
def close(signum, frame) :
	logging.info('recv stop cmd,try to stop!')
	sys.exit(0)
	
if __name__ == '__main__' :
	global g_config

	signal.signal(signal.SIGTSTP, close)
	signal.signal(signal.SIGINT, close)
	signal.signal(signal.SIGQUIT, close)
	logfile = 'syslog-%s.log'%(datetime.datetime.now().strftime('%y%m%d%H%M%S'))
	logging.basicConfig(level=logging.INFO,
                format='%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d] -> %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename=logfile,
                filemode='w')
	if len(sys.argv) < 2 :
		logging.error("error args...")
	g_config = parseConfig(sys.argv[1])
	if g_config['daemon'] :
		daemon(g_config['pidfile'])
	else :
		console = logging.StreamHandler()
		console.setLevel(logging.INFO)
		formatter = logging.Formatter('%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d] -> %(message)s')
		console.setFormatter(formatter)
		logging.getLogger('').addHandler(console)
	recvSyslog(g_config['port'],handleMessage)
	if os.path.exists(g_config['pidfile']) :
		os.remove(g_config['pidfile'])
	