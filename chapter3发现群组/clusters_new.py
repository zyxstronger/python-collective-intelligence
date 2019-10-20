# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 14:41:28 2019

@author: Think
"""

import clusters
import drawtree

#定义Tanimoto系数
#两个向量同时拥有的/两个向量分别自己独有的之和
def tanimoto(v1,v2):
    c1,c2,shr=0,0,0
    
    for i in range(len(v1)):
        if v1[i]!=0:c1+=1
        if v2[i]!=0:c2+=1
        if v1[i]!=0 and v2[i]!=0:shr+=1
        
    return 1.0-(float(shr)/(c1+c2-shr))

#读取文本中的数据
def readfile(filename):
    with open(filename) as f:
        lines=[line for line in f]
    
    #读出来是字符串的形式，所以需要转换成list
    colname=lines[0].strip().split('\t')[1:]
    rowname=[]
    data=[]
    for line in lines[1:]:
        p=line.strip().split('\t')
        
        rowname.append(p[0])
        data.append([float(i) for i in p[1:]])
    
    return rowname,colname,data
  
'''      
(wants,people,data)=readfile('zebo.txt')
clust=clusters.hcluster(data,distance=tanimoto)
drawtree.drawdendrogram(clust,wants)
'''




