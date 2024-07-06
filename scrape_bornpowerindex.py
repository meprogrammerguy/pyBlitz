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
from pathlib import Path
from xlsxwriter import Workbook

import settings
import pyBlitz

url = 'http://www.bornpowerindex.com/cgi-bin/DBRetrieve.pl'

print ("Scrape Born Power Index Tool")
print ("**************************")
print ("data is from {0}".format(url))
print ("Directory Location: {0}".format(settings.data_path))
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
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table2[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table3[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table4[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table5[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))
for row in table6[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(string=True)!="School":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[0].find(string=True)))
        B.append(col[1].find(string=True))
        C.append(col[2].find(string=True))

df=pd.DataFrame(IDX,columns=['Index'])
df['School']=A
df['Ranking']=B
df['Class']=C

Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
with open(settings.data_path + 'bornpowerindex.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(settings.data_path + "bornpowerindex.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)
stats_sheet = open(settings.data_path + 'bornpowerindex.csv', 'w', newline='')
csvwriter = csv.writer(stats_sheet)
count = 0
for row in dict_stats.values():
    if (count == 0):
        header = row.keys()
        csvwriter.writerow(header)
        count += 1
    csvwriter.writerow(row.values())
stats_sheet.close()

writer = pd.ExcelWriter(settings.data_path + "bornpowerindex.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1")
writer.close()

print ("done.")
