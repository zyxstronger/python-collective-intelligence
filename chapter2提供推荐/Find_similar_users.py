# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 19:42:38 2019

@author: Think
"""

critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

#from recommendations import critics
from math import sqrt

#返回一个有关person1和person2的基于距离的相似度评价
#欧几里得距离
def sim_distance(prefs,person1,person2):
    #用来判断是否存在相同的评价指标项
    #注意字典的可以直接追加数据
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1
    
    if len(item)==0:
        return 0
    
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2) 
                        for item in prefs[person1] if item in prefs[person2]])
    
    return 1/(1+sqrt(sum_of_squares))

#print('person1 and person2',sim_distance(critics,'Lisa Rose','Gene Seymour'))
    
#皮尔逊相关度评价
#返回结果为两人的相关度指标
def sim_person(prefs,p1,p2):
    si={}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item]=1
    n=len(si)
    if n==0:
        return 1
    
    #对所有偏好求和
    sum1=sum([prefs[p1][item] for item in si])
    sum2=sum([prefs[p2][item] for item in si])
    
    #求平方和
    sum1Sq=sum([pow(prefs[p1][item],2) for item in si])
    sum2Sq=sum([pow(prefs[p2][item],2) for item in si])
    
    #求乘积之和
    pSum=sum([prefs[p1][item]*prefs[p2][item] for item in si])
    
    #计算皮尔逊评价值
    num=pSum-(sum1*sum2/n)
    den=sqrt((sum1Sq-pow(sum1,2)/n)*(sum2Sq-pow(sum2,2)/n))
    if den==0:
        return 0
    
    r=num/den
    
    return r

#print('person1 and person2',sim_person(critics,'Lisa Rose','Gene Seymour'))

#从反映偏好的字典中返回最为匹配者
#返回的个数和相似度函数均为可选参数
def topMatches(prefs,person,n=5,similarity=sim_person):
    scores=[(similarity(prefs,person,other),other) for other in prefs if other !=person]
    
    #对列表进行排序
    scores.sort()
    scores.reverse()
    return scores[0:n]
    
#a=topMatches(critics,'Toby',n=4)

#利用所有他人评价值的加权平均，为某人提供建议
#返回值为对person来说推荐的电影从高到低
def getRecommendations(prefs,person,similarity=sim_person):
    totals={}
    simSum={}
    for other in prefs:
        #不和自己比较
        if other==person:continue
        
        sim=similarity(prefs,person,other)
        #忽略两人的评价相关度小于0的情况
        if sim<=0:continue
    
        for item in prefs[other]:
            #只对自己未看过的影片进行评价
            if item not in prefs[person] or prefs[person][item]==0:
                #若不存在key则放入value，存在则返回value，避免重复建立覆盖
                totals.setdefault(item,0)
                #相似度*评价值求和
                totals[item]+=prefs[other][item]*sim
                simSum.setdefault(item,0)
                simSum[item]+=sim
    
    #建立一个归一化的列表
    rankings=[(total/simSum[item],item) for item ,total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings

#b=getRecommendations(critics,'Toby')

#计算每个人的推荐电影，用字典存储
#person_habby={}
#for item in critics:
#    person_habby.setdefault(item,getRecommendations(critics,item))
#print(person_habby)

#将电影与评价者反转，字典的key为电影名，value为各个评价者的评分组成的字典
def transformPrefs(prefs):
    result={}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
        
            result[item][person]=prefs[person][item]
    return result

movie=transformPrefs(critics)
#print(getRecommendations(movie,'Just My Luck'))


   
    
    