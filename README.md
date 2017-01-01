# Syslog Monitor 

### syslog日志监控脚本，当脚本监控到用户登录时会给配置的邮件用户发送email
---
#### 开发说明
| 文件 | 用途 |
| -- | -- |
| ipsearch.py  |  ip地址工具类 |
| syslogd.py | 接受syslog，解析 |
| udpnat.py | udp转发 |
| logparser.py | 解析工具类 |
| logdump.py | 对syslogd生成的日志文件解析工具 |
----

#### 运行
##### 环境要求
``` shell
#开启系统rsyslog服务（没有此服务需要安装）
# yum install -y rsyslog
# apt-get install -y rsyslog
#添加syslog转发
#在/etc/rsyslog.conf中添加
## *.* @[目标IP]:55555;RSYSLOG_TraditionalForwardFormat
#开启syslogd
python syslogd.py syslog.json
```

##### 配置
``` js
{
	"mailsmtp":"xxxx",       /*smtp服务器*/
	"mailuser":"xxx",        /*发送邮箱账户*/
	"mailpass":"xxx",        /*发送邮箱密码*/
	"mailto":"xx",           /*接受邮件用户*/
	"daemon":false,          /*程序是否以daemon方式运行*/
	"port":55555,            /*syslogd监听udp端口*/
	"pidfile":"syslog.pid"   /*生成的pid文件*/
}
```

#### logdump
``` bash
#logdump用于将syslogd生成的日志解析并且存放到mongodb中
python logdump.py syslog-xxxx.log
```


