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

url = "https://www.reddit.com/r/CFB/wiki/abbreviations"

print ("Scrape Abbreviations Tool")
print ("**************************")
print ("data is from {0}".format(url))
print ("**************************")

with contextlib.closing(urlopen(url)) as page:
    soup = BeautifulSoup(page, "html5lib")
tables=soup.findAll("table")

IDX=[]
A=[]
B=[]
index=1
# Add any Missing Teams Here
IDX.append(index)
A.append("ALABAMA-BIRMINGHAM")
B.append("UAB")
for row in tables[1].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0:
        tag = str(col[0].find(text=True)).strip()
        tag2 = str(col[0].find(href=True)).lower().strip()
        if (tag != "none" and tag != "team"):
            if ("#f" in tag2):
                index+=1
                IDX.append(index)
                A.append(tag)
                B.append(col[1].find(text=True))

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['Abbreviation']=B

path = "data/"

with open(path + 'abbreviation.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(path + "abbreviation.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)
stats_sheet = open(path + 'abbreviation.csv', 'w', newline='')
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
