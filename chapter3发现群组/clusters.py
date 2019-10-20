# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 10:56:00 2019

@author: Think
"""
from math import sqrt
import random
from PIL import Image,ImageDraw

#处理文件数据 分为单词、书名、数据
def readfile(filename):
    lines=[line for line in open(filename)]
    
    #第一行是标题
    colnames=lines[0].strip().split('\t')[1:]
    rownames=[]
    data=[]
    for line in lines[1:]:
        p=line.strip().split('\t')
        #每行的第一列是书名
        rownames.append(p[0])
        #剩下部分就是该行对应的数据
        data.append([float(x) for x in p[1:]])
    return rownames,colnames,data


#利用皮尔逊相关度作相关性判断
#传入的参数为两个list
def person(v1,v2):
    #简单求和
    sum1=sum(v1)
    sum2=sum(v2)
    
    #求平方和
    sum1Sq=sum([pow(v,2) for v in v1])
    sum2Sq=sum([pow(v,2) for v in v2])
    
    #求乘积之和
    pSum=sum([v1[i]*v2[i] for i in range(len(v1))])
    
    #计算r
    num=pSum-(sum1*sum2/len(v1))
    den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
    if den==0:return 0
    
    #让相似度越大的两个元素之间的距离变得更小
    return 1.0-num/den

#代表层级数
class bicluster:
    def __init__(self,vec,left=None,right=None,distance=0.0,id_number=None):
        self.left=left
        self.right=right
        self.vec=vec
        self.id_number=id_number
        self.distance=distance

#聚类算法（直到聚为1类才停止）
def hcluster(rows,distance=person):
    distances={}
    currentclustid=-1
    
    #最开始的聚类就是数据集中的行 有多少行就有多少类
    clust=[bicluster(rows[i],id_number=i) for i in range(len(rows))]
    
    while len(clust)>1:
        lowstpair=(0,1)
        closest=distance(clust[0].vec,clust[1].vec)
        
        #遍历每一个配对，寻找最小距离
        for i in range(len(clust)):
            for j in range(i+1,len(clust)):
                #用distances来缓存距离的计算值
                if(clust[i].id_number,clust[j].id_number) not in distances:
                    distances[(clust[i].id_number,clust[j].id_number)]=distance(clust[i].vec,clust[j].vec)
                
                d=distances[(clust[i].id_number,clust[j].id_number)]
                if d<closest:
                    closest=d
                    lowstpair=(i,j)
            
        #计算两个聚类的平均值
        mergevec=[(clust[lowstpair[0]].vec[i]+clust[lowstpair[1]].vec[i])/2.0 for i in range(len(clust[0].vec))]
            
        #建立新的聚类
        newcluster=bicluster(mergevec,left=clust[lowstpair[0]],right=clust[lowstpair[1]],distance=closest,id_number=currentclustid)
            
        #不在原来集合中的聚类，其id为负数
        currentclustid-=1
        #先删右边的则不会对左边的产生影响
        del clust[lowstpair[1]]
        del clust[lowstpair[0]]
        clust.append(newcluster)
    return clust[0]
    
blognames,words,data=readfile('blogdata.txt')
clust=hcluster(data)

#打印层级结构
def printclust(clust,labels=None,n=0):
    #利用缩进来建立层级布局
    for i in range(n):print(' ')
    if clust.id_number<0:
        #负数标记代表这是一个分支
        print('-')
    else:
        #正数标记代表这是一个叶节点
        if labels==None:print(clust.id_number)
        else:print(labels[clust.id_number])
    
    #现在开始打印右侧和左侧分支
    if clust.left!=None:printclust(clust.left,labels=labels,n=n+1)
    if clust.right!=None:printclust(clust.right,labels=labels,n=n+1)

#printclust(clust,labels=blognames)

#数据矩阵转置
def rotatematrix(data):
    newdata=[]
    for i in range(len(data[0])):
        newrow=[data[j][i] for j in range(len(data))]
        newdata.append(newrow)
    return newdata

#多维缩放-返回二维坐标下的点
def scaledown(data,distance=person,rate=0.01):
    n=len(data)
    
    #每一对数据项之间的真实距离
    realdist=[[distance(data[i],data[j]) for j in range(n)]for i in range(0,n)]
    
    #outersum=0.0
    
    #随机初始化节点在二维空间中的起始位置
    loc=[[random.random(),random.random()] for i in range(n)]
    fakedist=[[0.0 for j in range(n)] for i in range(n)]
    
    lasterror=None
    for m in range(1000):
        #寻找投影后的位置,求出每两个向量之间的距离差
        for i in range(n):
            for j in range(n):
                fakedist[i][j]=sqrt(sum([pow(loc[i][x]-loc[j][x],2) for x in range(len(loc[i]))]))
        
        #移动节点
        grad=[[0.0,0.0] for i in range(n)]
        
        totalerror=0
        for k in range(n):
            #只要处理一半就可以，因为矩阵是对称的
            for j in range(n):
                if j==k: continue
                #误差值等于目标距离与当前距离差值/目标距离
                errorterm=(fakedist[j][k]-realdist[j][k])/realdist[j][k]
                
                #每一个节点都需要根据误差的多少，按比例移向其他节点
                grad[k][0]+=((loc[k][0]-loc[j][0])/fakedist[j][k])*errorterm
                grad[k][1]+=((loc[k][1]-loc[j][1])/fakedist[j][k])*errorterm
                
                #记录总的误差值 需要加绝对值
                totalerror+=abs(errorterm)
        print(lasterror,' ',totalerror)
        
        #如果节点移动之后的情况变得更糟，则程序结束
        if lasterror and lasterror<totalerror:break
        lasterror=totalerror
        
        #根据rate参数与grad值相乘的结果，移动每一个节点
        for k in range(n):
            loc[k][0]-=rate*grad[k][0]
            loc[k][1]-=rate*grad[k][1]
        
    return loc

#多维缩放-绘制二维图
def draw2d(data,labels,jpeg='mds2d.jpg'):
    img=Image.new('RGB',(2000,2000),(255,255,255))
    draw=ImageDraw.Draw(img)
    for i in range(len(data)):
        x=(data[i][0]+0.5)*1000
        y=(data[i][1]+0.5)*1000
        draw.text((x,y),labels[i],(0,0,0))
    img.save(jpeg,'JPEG')

blognames,words,data=readfile('blogdata.txt')
coords=scaledown(data)
draw2d(coords,blognames,jpeg='blogs2d.jpg')


       