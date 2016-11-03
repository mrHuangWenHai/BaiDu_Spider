# -*- coding: utf-8 -*-
import urllib2,re,json,time,argparse
import MySQLdb
import Queue
def getHtml(url,ref = None):
        request = urllib2.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.7.8 (KHTML, like Gecko) Version/9.1.3 Safari/601.7.8')

        if ref:
        	request.add_header('Referer',ref)
        try:
        	page = urllib2.urlopen(request,timeout = 20)
        	html = page.read()
        	follows_json = json.loads(html)
        except:
			print 'time out wait 4 minute'
			time.sleep(4*60)
			follows_json = {'errno':-1}
        return follows_json


class DB(object):
	"""docstring for ClassName"""
	def __init__(self):
		self.db = MySQLdb.connect('127.0.0.1','root','','Baidu',charset='utf8');
		self.cursor = self.db.cursor()

	def saveData(self,sql,arg):
		self.cursor.execute(sql,arg)
		self.db.commit()

	def getData(self,sql):
		try:
			self.cursor.execute(sql)
			results = self.cursor.fetchall()
			return results
		except:
			print "Error : unable to fecth data"

	def handleData(self,sql):
		try:
			self.cursor.execute(sql)
			self.db.commit()
		except:
			self.db.rollback()





		

class BaiDuPan(object):
	def  __init__(self):
	     self.request_queue=Queue.Queue(maxsize=20)
	     self.db = DB()

	def getShareList(self,uk,start):
		sharelists_url='http://yun.baidu.com/pcloud/feed/getsharelist?category=0&auth_type=1&request_location=share_home&start=%d&limit=60&query_uk=%d&channel=chunlei&clienttype=0&web=1' %(start,uk)
		ref = 'yun.baidu.com/share/home?uk= %d&view=share' %uk
		return getHtml(sharelists_url,ref)

	def getFollows(self,uk,start=0,limit=24):
		follows_url='http://yun.baidu.com/pcloud/friend/getfollowlist?query_uk=%d&limit=%d&start=%d&bdstoken=d82467db8b1f5741daf1d965d1509181&channel=chunlei&clienttype=0&web=1'%(uk,limit,start)
		ref='http://yun.baidu.com/pcloud/friendpage?type=follow&uk=%d&self=1'%uk
		return getHtml(follows_url,ref)

	def getFans(self,uk,start=0,limit=24):
		fans_url='http://yun.baidu.com/pcloud/friend/getfanslist?query_uk=%d&limit=%d&start=%d'%(uk,limit,start)
		return getHtml(fans_url)

	def initDbList(self):
		list_json=getHtml('http://yun.baidu.com/pcloud/friend/gethotuserlist?type=1&from=feed&start=0&limit=24&channel=chunlei&clienttype=0&web=1')
		if list_json['errno'] != 0:
			print 'failed to fecht list user'
			return False
		for item in list_json['hotuser_list']:
			if item['pubshare_count'] > 0:
				self.db.saveData("INSERT INTO share_list (intro,follow_count,fans_count,pubshare,uk,album_cout) VALUES (%s,%s,%s,%s,%s,%s)",(
					item['intro'].encode('utf-8'),item['follow_count'],item['fans_count'],item['pubshare_count'],item['hot_uk'],item['album_count']))


	def start(self):
		sql = 'select id,uk,pubshare,fans_count,follow_count from share_list ORDER BY pubshare DESC limit 0,20' 
		results = self.db.getData(sql)
		for row in results:
			self.request_queue.put({
				'sid':row[0],
				'uk':row[1],
				'pubshare':row[2],
				'fans_count':row[3],
				'follow_count':row[4]
				})
		while not self.request_queue.empty():
			target = self.request_queue.get()
			pubshare_count = 0
			fetch_count = 0
			total_count = target['pubshare']
			fans_fetch = 0
			fans_count = target['fans_count']
			if fans_count > 100:
				fans_count = 100
				target['fans_count']-=100
			else:
				target['fans_count']-=fans_count

			follow_fetch = 0
			follow_count = target['follow_count']
			if follow_count > 100:
				follow_count = 100
				target['follow_count'] -= 100

			else:
				target['follow_count'] -= follow_count
			while fetch_count < total_count:
				result_json = self.getShareList(target['uk'],fetch_count)
				#print target['uk']
				if result_json['errno'] == 0:
					for item in result_json['records']:
						print target['uk']
						fetch_count = fetch_count + 1
						if item.has_key('shorturl'):
							self.db.saveData("INSERT INTO file_list (title,shorturl,uk,type) VALUES(%s,%s,%s,%s)", (item['title'],item['shorturl'],target['uk'],0))
						else:
							if item.has_key('album_id'):
								self.db.saveData("INSERT INTO file_list (title,album,uk,type) VALUES(%s,%s,%s,%s)", (item['title'],item['album_id'],target['uk'],1))
							else:
								self.db.saveData("INSERT INTO file_list (title,shareid,uk,type) VALUES(%s,%s,%s,%s)", (item['title'],item['shareid'],target['uk'],2))

				else:
					print 'pubshare sleep %d %d' %(fetch_count,total_count)
					time.sleep(60)
					print 'pubshare start'

			while follow_fetch < follow_count:

				follow_json = self.getFollows(target['uk'],follow_fetch)
				if follow_json['errno'] == 0:
					print 'follow'
					for item in follow_json['follow_list']:
						follow_fetch = follow_fetch + 1
						self.db.saveData("INSERT INTO share_list (intro,follow_count,fans_count,pubshare,uk,album_cout) VALUES (%s,%s,%s,%s,%s,%s)",(
						item['intro'].encode('utf-8'),item['follow_count'],item['fans_count'],item['pubshare_count'],item['follow_uk'],item['album_count']))

				else:
					print 'follow sleep  %d %d' %(follow_fetch,follow_count)
					time.sleep(60)
					print 'follow start'


			while fans_fetch < fans_count:
				fans_json = self.getFans(target['uk'],fans_fetch)
				print 'fans'
				if fans_json['errno'] == 0:
					for item in fans_json['fans_list']:
						fans_fetch = fans_fetch + 1
						self.db.saveData("INSERT INTO share_list (intro,follow_count,fans_count,pubshare,uk,album_cout) VALUES (%s,%s,%s,%s,%s,%s)",(
						item['intro'].encode('utf-8'),item['follow_count'],item['fans_count'],item['pubshare_count'],item['fans_uk'],item['album_count']))

				else:
					print 'fans sleep'
					time.sleep(60)
					print 'fans start'
				
					time.sleep(60)
			if target['fans_count'] == 0 and target['follow_count'] == 0:
				deltesql = 'DELETE FROM share_list WHERE uk = %d' %target['uk']
				print 'delete %d' %target['sid']
				self.db.handleData(deltesql)
			else:
				print 'update'
				updatesql = 'UPDATE share_list SET follow_count = %d ,fans_count = %d , pubshare =%d where uk = %d' %(target['follow_count'],target['fans_count'],0,target['uk'])
				self.db.handleData(updatesql)









			




if __name__ == '__main__':
	parse = argparse.ArgumentParser()
	parse.add_argument("--seed-user", help="get seed user")
	args = parse.parse_args()
	parse.parse_args()
	baidu = BaiDuPan()
	if args.seed_user ==None:
		baidu.initDbList()

	else:
		while 1:
			baidu.start()
