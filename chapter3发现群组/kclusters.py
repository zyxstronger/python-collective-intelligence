# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 16:38:19 2019

@author: Think
"""
#K-均值聚类

from clusters import readfile,person
import random

#K-均值聚类
def kcluster(rows,distance=person,k=4):
    #确定每一个点的最小值和最大值,对各向量而言
    ranges=[(min([row[i] for row in rows]),max([row[i] for row in rows])) for i in range(len(rows[0]))]
    
    #随机建立k个点
    clusters=[[random.random()*(ranges[i][1]-ranges[i][0])+ranges[i][0] for i in range(len(rows[0]))] for j in range(k)]
    
    lastmatches=None
    for t in range(100):
        print('Iteration %d' %t)
        bestmatches=[[] for i in range(k)]
        
        #在每一行中寻找距离最近的中心点
        for j in range(len(rows)):
            row=rows[j]
            bestmatch=0;
            for i in range(k):
                d=distance(clusters[i],row)
                if d<distance(clusters[bestmatch],row):bestmatch=i
            bestmatches[bestmatch].append(j)
        
        #如果结果与上一次相同，则整个过程结束
        if bestmatches==lastmatches:break
        lastmatches=bestmatches
        
        #将中心点移到其所有成员的平均位置处
        for i in range(k):
            avgs=[0.0]*len(rows[0])
            if len(bestmatches[i])>0:
                for rowid in bestmatches[i]:
                    for m in range(len(rows[rowid])):
                        avgs[m]+=rows[rowid][m]
                for j in range(len(avgs)):
                    avgs[j]/=len(bestmatches[i])
                clusters[i]=avgs
    
    return bestmatches   
    
blognames,words,data=readfile('blogdata.txt')
kclust=kcluster(data,k=4)
#打印出聚类后的四类的博客名
print([[blognames[i] for i in kclust[j]] for j in range(4)])





