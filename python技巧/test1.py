# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 17:30:33 2019

@author: Think
"""

l=[1,2,3,4,5,6,7]
print([v*10 for v in l if v>4])
temp=dict([(v,v*10) for v in l])

