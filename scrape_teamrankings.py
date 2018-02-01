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
import re
from pathlib import Path

import settings

def CleanString(data):
    return re.sub(' +',' ', data)

urls = []
urls.append("https://www.teamrankings.com/college-football/stat/plays-per-game")
urls.append("https://www.teamrankings.com/college-football/stat/points-per-play")
urls.append("https://www.teamrankings.com/college-football/stat/opponent-points-per-game")
urls.append("https://www.teamrankings.com/college-football/stat/opponent-points-per-play")

print ("Scrape Team Rankings Tool")
print ("**************************")
ratings_table = []
for url in urls:
    print ("data is from {0}".format(url))
    with contextlib.closing(urlopen(url)) as page:
        soup = BeautifulSoup(page, "html5lib")
    ratings_table.append(soup.find('table', {"class":"tr-table datatable scrollable"}))

print ("Directory Location: {0}".format(settings.data_path))
print ("**************************")
IDX=[]
A=[]
B=[]
C=[]
D=[]
E=[]
index=0
for row in ratings_table[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[1].find(text=True)!="Team":
        index+=1
        IDX.append(index)
        A.append(CleanString(col[1].find(text=True)))
        B.append(col[3].find(text=True))
for team in A:
    for row in ratings_table[1].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(text=True)==team:
            C.append(col[3].find(text=True))
            break
for team in A:
    for row in ratings_table[2].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(text=True)==team:
            D.append(col[3].find(text=True))
            break
for team in A:
    for row in ratings_table[3].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(text=True)==team:
            E.append(col[3].find(text=True))
            break

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['PLpG3']=B
df['PTpP3']=C
df['OPLpG3']=D
df['OPTpP3']=E

Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
with open(settings.data_path + 'teamrankings.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(settings.data_path + "teamrankings.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)
stats_sheet = open(settings.data_path + 'teamrankings.csv', 'w', newline='')
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
