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

url = "http://www.footballoutsiders.com/stats/ncaa"

#url = "http://www.footballoutsiders.com/stats/ncaa2016" #past year testing override

print ("Scrape Statistics Tool")
print ("**************************")
print ("data is from {0}".format(url))
print ("**************************")

with contextlib.closing(urlopen(url)) as page:
    soup = BeautifulSoup(page, "html5lib")
ratings_table=soup.find('table', {"class":"stats"})

IDX=[]
A=[]
B=[]
C=[]
D=[]
E=[]
F=[]
G=[]
H=[]
index=0
for row in ratings_table.findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[0].find(text=True)!="Team":
        index+=1
        IDX.append(index)
        A.append(col[0].find(text=True))
        B.append(col[1].find(text=True))
        C.append(col[2].find(text=True))
        D.append(col[3].find(text=True))
        E.append(col[4].find(text=True))
        F.append(col[6].find(text=True))
        G.append(col[8].find(text=True))
        H.append(col[10].find(text=True))

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['Rec']=B
df['2ndO']=C
df['S&P+P']=D
df['S&P+M']=E
df['OS&P+']=F
df['DS&P+']=G
df['STS&P+']=H

with open('stats.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open("stats.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)
stats_sheet = open('stats.csv', 'w', newline='')
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
