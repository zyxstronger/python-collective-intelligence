# -*- coding: utf-8 -*-
"""
Created on Sat Sep  7 15:45:08 2019

@author: Think
"""

import time
import random
import math

people = [('Seymour','BOS'),('Franny','DAL'),('Zooey','CAK'),('Walt','MIA'),('Buddy','ORD'),('Les','OMA')]

#New York的LaGuardia机场
destination='LGA'

#航班数据格式：起点、终点、起飞时间、到达时间、价格
#拆字符串split() 去头和尾字符strip()
flights={}
with open('schedule.txt') as f:
    for line in f:
        #切割字符串 建立key为航班起点与终点的信息,value为空
        origin,dest,depart,arrive,price=line.strip('\n').split(',')
        flights.setdefault((origin,dest),[])
        
        #将航班详情添加到航班信息中 由于同一起点终点的航班可能会有多班
        #所以字典的形式应为key(origin,dest):value[(depart1,arrive1,int(price1)),(depart2,arrive2,int(price2))...]
        flights[(origin,dest)].append((depart,arrive,int(price)))

#计算某个给定时间在一天中的分钟数 传入字符串形式表示的时间
def getminutes(t):
    x=time.strptime(t,"%H:%M")
    return x[3]*60+x[4]

#将人们决定搭乘的所有航班打印成表格
#描述乘坐的航班信息的方式为在该天中同一起点终点的航班的次序号
#r的形式为长度为人数两倍的列表，包含的信息即为航班的次序号
def printschedule(r):
    for d in range(int(len(r)/2)):
        name=people[d][0]
        origin=people[d][1]
        #从原始地出发到目标地的航班信息
        out=flights[(origin,destination)][r[2*d]]
        #返回的航班信息
        ret=flights[(destination,origin)][r[2*d+1]]
        
        #打印出每个人所乘坐的航班信息
        print("%10s%10s %5s-%5s $%3s %5s-%5s $%3s" %(name,origin,out[0],out[1],out[2],ret[0],ret[1],ret[2]))

#测试代码
#其中1,4对应第一个人的航班信息,一直向下
a=[1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
#printschedule(a)
        
#成本函数计算 考虑相关因素：
#价格:所有航班的总票价
#旅行时间:每个人在飞机上花的总时间
#等待时间:在机场等待其他成员到达的时间
#出发时间:航班过早带来的减少睡眠的时间
#汽车租用时间:若集体租用一辆汽车，必须在一天之内早于起租时刻之前将车辆归还，否则将多付一天的租金
def schedulecost(sol):
    totalprice=0
    latestarrival=0
    earliestdep=24*60
    
    for d in range(int(len(sol)/2)):
        #得到往程航班和返程航班信息
        origin=people[d][1]
        outbound=flights[(origin,destination)][sol[2*d]]
        returnf=flights[(destination,origin)][sol[2*d+1]]
        
        #总价格等于所有往返航程的价格之和
        totalprice+=outbound[2]
        totalprice+=returnf[2]
        
        #记录最晚到达时间和最早离开时间
        if latestarrival<getminutes(outbound[1]):
            latestarrival=getminutes(outbound[1])
        if earliestdep>getminutes(returnf[0]):
            earliestdep=getminutes(returnf[0])
        
    #每个人必须在机场等待直到最后一个人到达为止
    #他们也必须在相同时间到达，并等候他们的返程航班
    totalwait=0
    for d in range(int(len(sol)/2)):
        origin=people[d][1]
        outbound=flights[(origin,destination)][sol[2*d]]
        returnf=flights[(destination,origin)][sol[2*d+1]]
        totalwait+=latestarrival-getminutes(outbound[1])
        totalwait+=getminutes(returnf[0])-earliestdep
        
    #判断租车费用是否需要再加一天
    if earliestdep>latestarrival:
        totalprice+=50
    
    return totalprice+totalwait
 
#打印成本总值        
#print(schedulecost(a))      

#随机搜索
#传入参数@domain 列表[(该方向航班序列号min,该方向航班序列号max),(,)...]，长度是两倍的人数
#       @constf计算成本使用的函数
def randomoptimize(domain,constf):
    best=999999999
    bestr=None
    for i in range(1000):
        #创建一个随机解
        r=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
        
        #得到成本
        cost=constf(r)
        
        #与到目前为止的最优解进行比较
        if cost<best:
            bestr=r
            best=cost
    
    return bestr

#随机搜索最好的结果
'''
#测试代码
domain=[(0,9)]*(len(people)*2)
s=randomoptimize(domain,schedulecost)
print(schedulecost(s))   
printschedule(s)
'''

#爬山法
def hillclimb(domain,costf):
    sol=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
    
    #主函数
    while 1:
        #创建相邻的列表
        neighbors=[]
        for j in range(len(domain)):
            
            #在每个方向上相对于原值偏离一点 相当于len维向量
            #neighbors为两倍len长度的列表，每一个索引值改变某一维上的值，或加1或减1
            if sol[j]>domain[j][0]:
                neighbors.append(sol[0:j]+[sol[j]-1]+sol[j+1:])
            if sol[j]<domain[j][1]:
                neighbors.append(sol[0:j]+[sol[j]+1]+sol[j+1:])

        #在相邻解中寻找最优解
        current=costf(sol)
        best=current
        for j in range(len(neighbors)):
            cost=costf(neighbors[j])
            if cost<current:
                sol=neighbors[j]
                best=cost
            
        #遍历所有的相邻解，在周围都没有更好的解，则退出循环
        if best==current:
            break
        
    return sol

#利用爬山法去寻找最优解
'''
#测试代码
domain=[(0,9)]*(len(people)*2)
s=hillclimb(domain,schedulecost)
print(schedulecost(s))   
printschedule(s)
'''

#模拟退火算法
#找到更优解就替换，但如果找到的解更差的话以一定概率接受，概率大小与温度有关
#此算法有几率会跳出局部最优解，但不一定能达到全局最优解
def annealingoptimize(domain,costf,T=10000.0,cool=0.95,step=1):
    #随机初始化值
    vec=[(random.randint(domain[i][0],domain[i][1])) for i in range(len(domain))]
    
    while T>0.1:
        #选择一个索引值 即改变哪一维度的值
        i=random.randint(0,len(domain)-1)
        
        #选择一个改变索引值的方向 即该维度的值增加还是减小
        dirt=random.randint(-step,step)
        
        #创建一个代表题解的新列表，改变其中某一维度的值
        vecb=vec[:]
        vecb[i]+=dirt
        #限制幅度，不能超过量程
        if vecb[i]<domain[i][0]:
            vecb[i]=domain[i][0]
        elif vecb[i]>domain[i][1]:
            vecb[i]=domain[i][1]
        
        #计算当前成本和新的成本
        ea=costf(vec)
        eb=costf(vecb)
        
        #接受新解的条件
        if (eb<ea or random.random()<pow(math.e,-(eb-ea)/T)):
            vec=vecb
        
        #降低温度
        T=T*cool
    return vec

#利用模拟退火法寻找最优解
'''
#测试代码
domain=[(0,9)]*(len(people)*2)
s=annealingoptimize(domain,schedulecost)
print(schedulecost(s))   
printschedule(s)   
'''

#遗传算法
#利用变异和交叉去构建新种群
#传入参数@popsize 种群大小
#       @step    变异步长
#       @mutprob 种群的新成员是由变异还是交叉得来的概率
#       @elite   种群中被认为是优解传入下一代的部分
#       @maxiter 运行多少代，即迭代次数
def geneticoptimize(domain,costf,popsize=50,step=1,mutprob=0.2,elite=0.2,maxiter=100):
    
    #变异操作
    def mutate(vec):
        i=random.randint(0,len(domain)-1)
        temp=random.random()
        if vec[i]>domain[i][0] and temp<0.5:
            return vec[0:i]+[vec[i]-step]+vec[i+1:]
        elif vec[i]<domain[i][1] and temp>=0.5:
            return vec[0:i]+[vec[i]+step]+vec[i+1:]
        else:
            return vec

    #交叉操作
    def crossover(r1,r2):
        i=random.randint(0,len(domain)-2)
        return r1[0:i]+r2[i:]
    
    #构建初始种群
    pop=[]
    for i in range(popsize):
        vec=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
        pop.append(vec)
    
    #每一代有多少胜出者
    topelite=int(elite*popsize)
    
    #主循环
    for i in range(maxiter):
        scores=[(costf(v),v) for v in pop]
        scores.sort()
        ranked=[v for (s,v) in scores]
        
        #从纯粹的胜出者开始
        pop=ranked[0:topelite]
        
        #添加变异和配对后的胜出者
        while len(pop)<popsize:
            #变异
            if random.random()<mutprob:
                c=random.randint(0,topelite)
                pop.append(mutate(ranked[c]))
            #交叉
            else:
                c1=random.randint(0,topelite)
                c2=random.randint(0,topelite)
                pop.append(crossover(ranked[c1],ranked[c2]))
            
        #打印当前最优值
        print(scores[0][0])
    
    return scores[0][1]

#利用遗传算法寻找最优解
domain=[(0,9)]*(len(people)*2)
s=geneticoptimize(domain,schedulecost)
print(schedulecost(s))   
printschedule(s)  
