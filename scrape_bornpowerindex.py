#!/usr/bin/env python3

import pdb
import requests
from bs4 import BeautifulSoup
import pandas as pd
import html5lib
from collections import OrderedDict
import json
import csv
import re

def CleanString(data):
    return re.sub(' +',' ', data)

url = 'http://www.bornpowerindex.com/cgi-bin/DBRetrieve.pl'

print ("Scrape Born Power Index Tool")
print ("**************************")
print ("data is from {0}".format(url))
print ("**************************")

data1 = {
    "getClassName": "on",
    "class": "1",
    "sort": "team"
}

data2 = {
    "getClassName": "on",
    "class": "2",
    "sort": "team"
}

data3 = {
    "getClassName": "on",
    "class": "3",
    "sort": "team"
}

data4 = {
    "getClassName": "on",
    "class": "4",
    "sort": "team"
}

data5 = {
    "getClassName": "on",
    "class": "5",
    "sort": "team"
}

data6 = {
    "getClassName": "on",
    "class": "6",
    "sort": "team"
}

headers = {
    "Host": "www.bornpowerindex.com",
    "Connection": "keep-alive",
    "Content-Length": "33",
    "Cache-Control": "max-age=0",
    "Origin": "http://www.bornpowerindex.com",
    "Upgrade-Insecure-Requests": "1",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "DNT": "1",
    "Referer": "http://www.bornpowerindex.com/M_COL_FB_CLASS.shtml",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9"
}

r = requests.post(url, data=data1, headers=headers)
soup = BeautifulSoup(r.content, "html5lib")
table1 = soup.findAll("table")

r = requests.post(url, data=data2, headers=headers)
soup = BeautifulSoup(r.content, "html5lib")
table2 = soup.findAll("table")

r = requests.post(url, data=data3, headers=headers)
soup = BeautifulSoup(r.content, "html5lib")
table3 = soup.findAll("table")

r = requests.post(url, data=data4, headers=headers)
soup = BeautifulSoup(r.content, "html5lib")
table4 = soup.findAll("table")

r = requests.post(url, data=data5, headers=headers)
soup = BeautifulSoup(r.content, "html5lib")
table5 = soup.findAll("table")

r = requests.post(url, data=data6, headers=headers)
soup = BeautifulSoup(r.content, "html5lib")
table6 = soup.findAll("table")

IDX=[]
A=[]
B=[]
C=[]
index=0
for row in table1[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(text=True)!="School":
        index+=1
        IDX.append(index)
        A.append(CleanString(col[0].find(text=True)))
        B.append(col[1].find(text=True))
        C.append(col[2].find(text=True))
for row in table2[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(text=True)!="School":
        index+=1
        IDX.append(index)
        A.append(CleanString(col[0].find(text=True)))
        B.append(col[1].find(text=True))
        C.append(col[2].find(text=True))
for row in table3[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(text=True)!="School":
        index+=1
        IDX.append(index)
        A.append(CleanString(col[0].find(text=True)))
        B.append(col[1].find(text=True))
        C.append(col[2].find(text=True))
for row in table4[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(text=True)!="School":
        index+=1
        IDX.append(index)
        A.append(CleanString(col[0].find(text=True)))
        B.append(col[1].find(text=True))
        C.append(col[2].find(text=True))
for row in table5[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(text=True)!="School":
        index+=1
        IDX.append(index)
        A.append(CleanStringcol[0].find(text=True)))
        B.append(col[1].find(text=True))
        C.append(col[2].find(text=True))
for row in table6[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(text=True)!="School":
        index+=1
        IDX.append(index)
        A.append(CleanStringcol[0].find(text=True)))
        B.append(col[1].find(text=True))
        C.append(col[2].find(text=True))

df=pd.DataFrame(IDX,columns=['Index'])
df['School']=A
df['Ranking']=B
df['Class']=C

path = "data/"

with open(path + 'bornpowerindex.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(path + "bornpowerindex.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)
stats_sheet = open(path + 'bornpowerindex.csv', 'w', newline='')
csvwriter = csv.writer(stats_sheet)
count = 0
for row in dict_stats.values():
    if (count == 0):
        header = row.keys()
        csvwriter.writerow(header)
        count += 1
    csvwriter.writerow(row.values())
stats_sheet.close()
print ("done.")
