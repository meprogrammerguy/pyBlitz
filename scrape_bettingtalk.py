#!/usr/bin/env python3

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import html5lib
import pdb
from collections import OrderedDict
import json
import csv
import contextlib
import os

url = "http://www.bettingtalk.com/win-probability-percentage-point-spread-nfl-nba"

print ("Scrape Percentage by Spread Tool")
print ("**************************")
print ("data is from {0}".format(url))
print ("**************************")

with contextlib.closing(urlopen(url)) as page:
    soup = BeautifulSoup(page, "html5lib")
ratings_table=soup.find('table', id="tablepress-23")

IDX=[]
A=[]
B=[]
C=[]
index=0
for row in ratings_table.findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(text=True)!="Spread":
        index+=1
        IDX.append(index)
        A.append(col[0].find(text=True))
        B.append(col[1].find(text=True))
        C.append(col[2].find(text=True))

df=pd.DataFrame(IDX,columns=['Index'])
df['Spread']=A
df['Favorite']=B
df['Underdog']=C

path = "data/"

with open(path + 'bettingtalk.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(path + "bettingtalk.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)
stats_sheet = open(path + 'bettingtalk.csv', 'w', newline='')
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
