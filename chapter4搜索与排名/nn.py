# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 15:10:51 2019

@author: Think
"""

from math import tanh
import sqlite3

def dtanh(y):
    return 1.0-y*y

class searchnet:
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()

    def maketables(self):
        self.con.execute('drop table if exists hiddennode')
        self.con.execute('drop table if exists wordhidden')
        self.con.execute('drop table if exists hiddenurl')
        self.con.execute('create table hiddennode(create_key)')
        self.con.execute('create table wordhidden(fromid,toid,strength)')
        self.con.execute('create table hiddenurl(fromid,toid,strength)')
        self.con.commit()
    
    #判断当前连接的强度 新连接只在必要时才会被创建，此方法在连接不存在时会返回一个默认值
    def getstrength(self,fromid,toid,layer):
        if layer==0:
            table='wordhidden'
        else:
            table='hiddenurl'
        res=self.con.execute('select strength from %s where fromid=%d and toid=%d' %(table,fromid,toid)).fetchone()
        if res==None:
            if layer==0:return -0.2
            if layer==1:return 0
        else:
            return res[0]
    
    #判断连接是否已存在，并利用新的强度值更新连接或创建连接
    def setstrength(self,fromid,toid,layer,strength):
        if layer==0:
            table='wordhidden'
        else:
            table='hiddenurl'
        #在层级表中查找索引号
        res=self.con.execute('select rowid from %s where fromid=%d and toid=%d' %(table,fromid,toid)).fetchone()
        if res==None:
            self.con.execute('insert into %s (fromid,toid,strength) values (%d,%d,%f)' %(table,fromid,toid,strength))
        else:
            rowid=res[0]
            self.con.execute('update %s set strength=%f where rowid=%d' %(table,strength,rowid))
    
    #每传入一组从未见过的单词组合，该函数就会在隐藏层中建立一个新的节点
    #[wordids]->wordhidden->hiddennode->hiddenurl->[urls]
    #hiddennode(create_key)
    #wordhidden(fromid,toid,strength)
    #hiddenurl(fromid,toid,strength)
    def generatehiddennode(self,wordids,urls):
        if len(wordids)>3:return None
        #检查我们是否已经为这组单词建好了一个节点 单词节点排序例 "1_2_3"
        createkey='_'.join(sorted([str(wi) for wi in wordids]))
        res=self.con.execute("select rowid from hiddennode where create_key='%s'" %createkey).fetchone()
        
        #如果没有，则建立之
        if res==None:
            cur=self.con.execute("insert into hiddennode (create_key) values ('%s')" %createkey)
            hiddenid=cur.lastrowid
            #设置默认权重
            for wordid in wordids:
                self.setstrength(wordid,hiddenid,0,1.0/len(wordids))
            for urlid in urls:
                self.setstrength(hiddenid,urlid,1,0.1)
            self.con.commit()
        
    #从隐藏层中找出与查询单词以及url相关的所有节点
    def getallhiddenids(self,wordids,urlids):
        l1={}
        for wordid in wordids:
            #找出所有查询的单词对应的隐藏层的节点
            cur=self.con.execute('select toid from wordhidden where fromid=%d' %wordid)
            for row in cur:
                l1[row[0]]=1
        for urlid in urlids:
            cur=self.con.execute('select fromid from hiddenurl where toid=%d' %urlid)
            for row in cur:
                l1[row[0]]=1
        
        #python3不支持dict的key索引
        return list(l1.keys())
    
    #建立起神经网络来
    def setupnetwork(self,wordids,urlids):
        #值列表
        self.wordids=wordids
        self.hiddenids=self.getallhiddenids(wordids,urlids)
        self.urlids=urlids
        
        #节点输出
        self.ai=[1.0]*len(self.wordids)
        self.ah=[1.0]*len(self.hiddenids)
        self.ao=[1.0]*len(self.urlids)
        
        #建立权重矩阵
        self.wi=[[self.getstrength(wordid,hiddenid,0) for hiddenid in self.hiddenids] for wordid in self.wordids]
        self.wo=[[self.getstrength(hiddenid,urlid,1) for urlid in self.urlids] for hiddenid in self.hiddenids]
        
    #构造前馈算法 算法接受一列输入，将其推入网络，然后返回所有输出层节点的输出结果
    #本例中由于已经构造了一个只与查询条件中的单词相关的网络，因此所有来自输入层节点的输出结果总是1
    #不同的单词组合决定的是采用哪几个查询节点
    def feedforward(self):
        #查询单词是仅有的输入
        for i in range(len(self.wordids)):
            self.ai[i]=1
        
        #隐藏层节点的活跃程度
        for j in range(len(self.hiddenids)):
            sum=0.0
            for i in range(len(self.wordids)):
                sum+=self.ai[i]*self.wi[i][j]
            self.ah[j]=tanh(sum)
        
        #输出层节点的活跃程度
        for k in range(len(self.urlids)):
            sum=0.0
            for j in range(len(self.hiddenids)):
                sum=sum+self.ah[j]*self.wo[j][k]
            self.ao[k]=tanh(sum)
        
        return self.ao[:]
    
    def getresult(self,wordids,urlids):
        self.setupnetwork(wordids,urlids)
        return self.feedforward()
    
    #反向传播法
    def backPropagate(self,targets,N=0.5):
        #计算输出层的误差
        output_deltas=[0.0]*len(self.urlids)
        for k in range(len(self.urlids)):
            error=targets[k]-self.ao[k]
            output_deltas[k]=dtanh(self.ao[k])*error
        
        #计算隐藏层的误差
        hidden_deltas=[0.0]*len(self.hiddenids)
        for j in range(len(self.hiddenids)):
            error=0.0
            for k in range(len(self.urlids)):
                error=error+output_deltas[k]*self.wo[j][k]
            hidden_deltas[j]=dtanh(self.ah[j])*error
        
        #更新输出权重
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                change=output_deltas[k]*self.ah[j]
                self.wo[j][k]=self.wo[j][k]+N*change
        
        #更新输入权重
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                change=hidden_deltas[j]*self.ai[i]
                self.wi[i][j]=self.wi[i][j]+N*change
    
    #更新数据库
    def updatedatabase(self):
        #将值存入数据库
        for i in range(len(self.wordids)):
            for j in range(len(self.hiddenids)):
                self.setstrength(self.wordids[i],self.hiddenids[j],0,self.wi[i][j])
        for j in range(len(self.hiddenids)):
            for k in range(len(self.urlids)):
                self.setstrength(self.hiddenids[j],self.urlids[k],1,self.wo[j][k])
        self.con.commit()
    
    
    #聚集各类方法 输入单词ID urlid 选择的url
    def trainquery(self,wordids,urlids,selectedurl):
        #如有必要，生成一个隐藏节点
        self.generatehiddennode(wordids,urlids)
        
        self.setupnetwork(wordids,urlids)
        self.feedforward()
        targets=[0.0]*len(urlids)
        targets[urlids.index(selectedurl)]=1.0
        self.backPropagate(targets)
        self.updatedatabase()
    
        
        
#mynet=searchnet('nn.db')
#mynet.maketables()
#wWorld,wRiver,wBank=101,102,103
#uWorldBank,uRiver,uEarth=201,202,203
'''
mynet.generatehiddennode([wWorld,wBank],[uWorldBank,uRiver,uEarth])
for c in mynet.con.execute('select * from wordhidden'):
    print(c)
print('\n')
for c in mynet.con.execute('select * from hiddenurl'):
    print(c)
'''
#此时未经训练，输出都一样
#mynet.trainquery([wWorld,wBank],[uWorldBank,uRiver,uEarth],uWorldBank)
#print(mynet.getresult([wWorld,wBank],[uWorldBank,uRiver,uEarth]))
    