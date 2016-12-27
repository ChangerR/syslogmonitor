#!/usr/bin/python
# -*- coding: UTF-8 -*-
import socket
import sys
import logging
import os
import datetime
import select

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

def trans(port,host) :
        try:
                sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                sock_send = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                sock.bind(("0.0.0.0",port))
        except:
                print("bind addreess failed,please check!")
                sys.exit(1)
        readlist = []
        readlist.append(sock)
        s_addr = (host,port)
        while True :
                try:
                        can_read,can_write,can_x = select.select(readlist,[],[],100)
                        if len(can_read) > 0 :
                                for s in can_read :
                                        data,addr = s.recvfrom(1024)
                                        sock_send.sendto(data,s_addr)
                except (socket.error,socket.timeout),e:
                        logging.error(e)
                        pass
                except select.error,e:
                        logging.error(e)

if __name__ == '__main__' :
    logfile = 'syslog-%s.log'%(datetime.datetime.now().strftime('%y%m%d%H%M%S'))
    logging.basicConfig(level=logging.INFO,
          format='%(levelname)s %(asctime)s %(filename)s[line:%(lineno)d] -> %(message)s',
          datefmt='%Y-%m-%d %H:%M:%S',
          filename=logfile,
          filemode='w')
    daemon('udpnat.pid')
    trans(55555,'local.changer.site')
