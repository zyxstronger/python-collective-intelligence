# -*- coding: utf-8 -*-
"""
Created on Sat Aug 24 09:24:37 2019

@author: Think
"""
import sqlite3
from bs4 import BeautifulSoup
import re
import nn
mynet=nn.searchnet('nn.db')

class crawler:
    #初始化crawer类并传入数据库名称
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()


#连接到数据库    
crawler=crawler('searchindex.db')
#print([row for row in crawler.con.execute('select * from wordlist')])
#print(crawler.con.execute('select * from wordlocation where location=327 and urlid=1').fetchone())
#print(crawler.con.execute('select * from wordlist where rowid=145').fetchone())
crawler.__del__()

#定义一个用于搜索的类
class searcher:
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()

    #查询函数 将输入字符串拆成多个单词，进行查找，只查找包含所有不同单词的URL
    def getmatchrows(self,q):
        #构造查询的字符串
        fieldlist='w0.urlid'
        tablelist=''
        clauselist=''
        wordids=[]
        
        #根据空格拆分单词
        words=q.split(' ')
        tablenumber=0
        
        for word in words:
            #获取单词的ID
            wordrow=self.con.execute("select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow!=None:
                wordid=wordrow[0]
                wordids.append(wordid)
                if tablenumber>0:
                    tablelist+=','
                    clauselist+=' and '
                    clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
                fieldlist+=',w%d.location' %tablenumber
                tablelist+='wordlocation w%d' % tablenumber
                clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
                tablenumber+=1
        
        #根据各个组分，建立查询
        fullquery='select %s from %s where %s' %(fieldlist,tablelist,clauselist)
        cur=self.con.execute(fullquery)
        #row: urlid location1 location2 ... 
        rows=[row for row in cur]
        
        #[(urlid location1 location2) ... ]+[wordid1 wordid2]
        return rows,wordids
    
    #接受查询请求，将获取到的行集置于字典中，并以格式化列表的形式显示输出
    def getscoredlist(self,rows,wordids):
        totalscores=dict([(row[0],0) for row in rows])
        
        #此处是稍后放置评价函数的地方
        #weights=[(1.0,self.frequencyscore(rows)),(1.0,self.locationscore(rows)),(1.0,self.pagerankscore(rows)),(1.0,self.linktextscore(rows,wordids))]
        weights=[(1.0,self.nnscore(rows,wordids))]
        
        for (weight,scores) in weights:
            for url in totalscores:
                totalscores[url]+=weight*scores[url]
        
        return totalscores
    
    #返回url的值
    def geturlname(self,id):
        return self.con.execute("select url from urllist where rowid=%d" %id).fetchone()[0]
    
    #输出排序后的结果
    def query(self,q):
        rows,wordids=self.getmatchrows(q)
        scores=self.getscoredlist(rows,wordids)
        rankedscores=sorted([(score,url) for (url,score) in scores.items()],reverse=1)
        for (score,urlid) in rankedscores[0:10]:
            print('%f\t%d %s' %(score,urlid,self.geturlname(urlid)))
        #返回单词ID以及urlID
        return wordids,[r[1] for r in rankedscores[0:10]]
            
    #归一化函数 接受一个包含ID与评价值的字典，并返回一个包含ID与评价值（最佳结果为1，最差为0）的字典
    def normalizescores(self,scores,smallIsBetter=0):
        vsmall=0.00001 #避免被零整除
        if smallIsBetter:
            minscore=min(scores.values())
            return dict([(u,float(minscore)/max(vsmall,l)) for (u,l) in scores.items()])
        else:
            maxscore=max(scores.values())
            if maxscore==0:maxscore=vsmall
            return dict([(u,float(c)/maxscore) for (u,c) in scores.items()])
    
    #以单词频度作为度量手段
    def frequencyscore(self,rows):
        #建立一个字典，去掉重复出现的url，所有key的value都是0
        counts=dict([(row[0],0) for row in rows])
        for row in rows:
            #对每一个url进行检索，检索到一次加1，代表该url中多了一个正在检索的单词
            counts[row[0]]+=1
        return self.normalizescores(counts)
    
    #以文档位置为度量手段 搜索单词在网页中的位置离网页开始处的位置越近代表越好
    def locationscore(self,rows):
        #建立一个字典 去掉重复的url，所有key的value都设为很大
        locations=dict([(row[0],1000000) for row in rows])
        for row in rows:
            loc=sum(row[1:])
            #对每一个url进行检索，如果有距离更小的，便置为value
            if locations[row[0]]>loc:locations[row[0]]=loc
        
        return self.normalizescores(locations,smallIsBetter=1)
    
    #以单词距离为度量手段 当查询包含多个单词时，寻找彼此间距很近的往往是很有意义的
    def distancescore(self,rows):
        #如果仅有一个单词，则得分都一样
        if len(rows[0])<=2:
            return dict([(row[0],1.0) for row in rows])
        
        #初始化字典，并填入一个很大的数
        mindistance=dict([(row[0],1000000) for row in rows])
        
        for row in rows:
            dist=sum([abs(row[i]-row[i-1]) for i in range(2,len(row))])
            if dist<mindistance[row[0]]:
                mindistance[row[0]]=dist
        
        return self.normalizescores(mindistance,smallIsBetter=1)
    
    #利用外部回指链接 对网页引用的越多，代表其内容越可靠
    #对网页上统计链接的数目进行简单计数
    def inboundlinkscore(self,rows):
        uniqueurls=set([row[0] for row in rows])
        #在数据库中查询各toid(即不同url)出现的次数，即外部引用数
        inboundlinkcount=dict([(u,self.con.execute('select count(*) from link where toid=%d' %u).fetchone()[0]) for u in uniqueurls])
        return self.normalizescores(inboundlinkcount)
    
    #计算pagerank值，代表网页的重要性
    def calculatepagerank(self,iterations=20):
        #清除当前的PageRank表
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key,score)')
        
        #初始化每个url，令其PageRank值为1
        #此语句为insert的一种用法，作用为选择urllist中(rowid,1.0)插入pagerank表中的(urlid,score)
        self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
        self.dbcommit()
        
        for i in range(iterations):
            print("Iteration %d" %i)
            for (urlid,) in self.con.execute('select rowid from urllist'):
                pr=0.15
                
                #循环遍历指向当前网页的所有网页
                for (linker,) in self.con.execute('select distinct fromid from link where toid=%d' %urlid):
                    #得到链接源
                    linkingpr=self.con.execute('select score from pagerank where urlid=%d' %linker).fetchone()[0]
                    
                    #根据链接源，求得总的链接数
                    linkingcount=self.con.execute('select count(*) from link where fromid=%d' %linker).fetchone()[0]
                    pr+=0.85*(linkingpr/linkingcount)
                #将pr值存入该url对应的PageRank值中
                self.con.execute('update pagerank set score=%f where urlid=%d' %(pr,urlid))
            self.dbcommit()
    
    #对PageRank值进行评分并做归一化处理
    def pagerankscore(self,rows):
        pageranks=dict([(row[0],self.con.execute('select score from pagerank where urlid=%d' %row[0]).fetchone()[0]) for row in rows])
        #maxrank=max(pageranks.values())
        #normalizedscores=dict([(u,float(l)/maxrank) for (u,l) in pageranks.items()])
        #return normalizedscores
        return self.normalizescores(pageranks)
    
    #利用链接文本 根据指向某一网页的链接文本来决定网页的相关程度
    #原理 一个网页如果拥有大量来自其他重要网页的链接指向，且这些网页又满足查询条件，则该网页会得到一个很高的评价
    def linktextscore(self,rows,wordids):
        linkscores=dict([(row[0],0) for row in rows])
        for wordid in wordids:
            #找出urllink中含有搜索词的，并在link表中查找fromid和toid
            cur=self.con.execute('select link.fromid,link.toid from linkwords,link where wordid=%d and linkwords.linkid=link.rowid' %wordid)
            for (fromid,toid) in cur:
                if toid in linkscores:
                    pr=self.con.execute('select score from pagerank where urlid=%d' %fromid).fetchone()[0]
                    linkscores[toid]+=pr
        return self.normalizescores(linkscores)
    
    #利用神经网络去进行排序
    def nnscore(self,rows,wordids):
        #获得一个由唯一的URL ID构成的有序列表
        urlids=[urlid for urlid in set([row[0] for row in rows])]
        nnres=mynet.getresult(wordids,urlids)
        scores=dict([(urlids[i],nnres[i]) for i in range(len(urlids))])
        return self.normalizescores(scores)
            

e=searcher('searchindex.db')
rows,wordids=e.getmatchrows("functional programming")
urlids=[]
for row in rows:
    urlids.append(row[0])
#给urlids去重 重复的节点过多会对神经网络有影响
t=set(urlids)
urlids=list(t)
for i in range(5):
    mynet.trainquery(wordids,urlids,220)


#打印出来的应该是[(x1,x2,x3)...]的形式
#其中x1表示url的id，具体url可用过id在urllist中找到
#x2表示查询的第一个单词在该url对应的网页提取出来的文本的具体位置
#x3表示查询的第二个单词在该url对应的网页提取出来的文本的具体位置
#print(e.getmatchrows("functional programming"))
#输出查询到的排在前十的url
e.query("functional programming")
#e.calculatepagerank()






