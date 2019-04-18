# coding=utf-8
# 自动检测Mysql运行效率脚本
# @author: Ravior(zhoufei@gfun.me)
# @date:2017-10-18

from __future__ import print_function
import MySQLdb
import sys, getopt
from tabulate import tabulate

# Mysql配置
HOST = '192.168.10.18'
PORT = 3306
USER = 'root'
PASSWD = '2016db-pachong'
CHARSET = 'utf8'

opts, args = getopt.getopt(sys.argv[1:], "h:u:p:")
for k,v in opts:
	if k in ('-h',):
		HOST = v
	elif k in ('-u',):
		USER = v
	elif k in ('-p',):
		PASSWD = v


conn = None
cursor = None

try:
	# 链接数据库
	conn = MySQLdb.connect(
	    host = HOST,
	    port = PORT,
	    user = USER,
	    passwd = PASSWD,
	    charset = CHARSET
	)
	cursor = conn.cursor()
except Exception as e:
	print("数据库链接失败, 失败原因:[%s]"%(e))
	exit()

print('数据库链接失败')
	
cursor.execute('show databases;')
tables = cursor.fetchall()


cursor.execute("show status like '%connect%'")
for row in cursor.fetchall():
	if row[0] == 'Max_used_connections':
		print('历史最大连接数:', row[1])
	elif row[0] == 'Max_used_connections_time':
		print('历史最大连接数发生时间:', row[1])
	elif row[0] == 'Threads_connected':
		print('当前连接数:',row[1])

cursor.execute("show variables")
for row in cursor.fetchall():
	# print(row)
	if row[0] == 'datadir':
		print('数据库文件存在路径:', row[1])
	elif row[0] == 'max_connections':
		print('数据库最大连接数:', row[1])

conn.select_db('information_schema')
cursor.execute("select concat(round(sum(`data_length`)/(1024*2014),2), 'MB') as 'DB_SIZE',concat(round(sum(`index_length`)/(1024*2014),2), 'MB') as 'INDEX_SIZE' from tables")
db_size = cursor.fetchone()
print('数据库大小:',db_size[0])
print('数据库索引大小:',db_size[1])

print('当前连接情况')
print('-'*100)
cursor.execute("show processlist")
processlist = cursor.fetchall()
print(tabulate(list(processlist), headers=["Pid","User", "Client","Table","Status","Time","Type","Operate"]))
print('-'*100)

tables2 = []
for row in tables:
	cursor.execute("select concat(round(sum(`data_length`)/(1024*2014),2), 'MB') as 'DB_SIZE',concat(round(sum(`index_length`)/(1024*2014),2), 'MB') as 'INDEX_SIZE' from tables where table_schema='%s'"%(row[0]))
	
	db_size = cursor.fetchone()
	tables2.append([row[0],db_size[0],db_size[1]])

print(tabulate(tables2, headers=[u"数据库",u"数据大小", u"索引大小"]))
print('-'*100)

cursor.close()
conn.close()



