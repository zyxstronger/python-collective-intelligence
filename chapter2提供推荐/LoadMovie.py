# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 19:36:57 2019

@author: Think
"""

import Find_similar_users
import csv

def Load_movie_data():
    with open("ratings.csv") as f:
        reader=csv.reader(f)
        next(reader)
        
        rating_scale={}
        #从第一行开始遍历 用户名 电影名 评分 时间
        #首先建立字典的key(用户名)
        for line in reader:
            #忽略第一行  
            #if reader.line_num == 1:  
                #continue  
           
            rating_scale.setdefault(line[0],{})
            rating_scale[line[0]][line[1]]=float(line[2])
        
            
    return rating_scale

str1=Load_movie_data()
#寻找1可能最喜欢的电影  
#print(Find_similar_users.getRecommendations(str1,'1'))

#迭代器 上面读csv文件返回的也是一个迭代器，有点像单向链表，next则指向下一个，前面的就找不到了        
it = iter([1, 2, 3, 4, 5])
next(it)
for li in it:
    print(li)