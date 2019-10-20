# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 21:26:12 2019

@author: Think
"""

#encoding:UTF-8
from bs4 import BeautifulSoup
import requests
import time
import json


'''
url="https://movie.douban.com/chart"
f = requests.get(url)                 #Get该网页从而获取该html内容
soup=BeautifulSoup(f.content,"lxml")
contents=soup.find_all("div",class_='pl2')
for content in contents:
    tag=content.a
    print(tag.next_element.strip().strip('/').strip())
'''

















html_doc = """
<html><head><title><b>The Dormouse's story</b></title></head>
    <body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""
soup = BeautifulSoup(html_doc, 'html.parser')
tag=soup.head
title_tag=soup.title
#print(tag.contents)
#print(soup.contents)
print(tag.string)

'''
for string in soup.stripped_strings:
    print(string)
    

link=soup.a
for parent in link.parents:
    if parent !=None:
        print(parent.name)
    else:
        print(parent)


link=soup.a
for sibling in soup.a.next_siblings:
    print(repr(sibling))


def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')

print([i.name for i in soup.find_all(has_class_but_no_id)])
'''