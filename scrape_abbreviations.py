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
import pyBlitz

index = 0

def AddSchool(team, abbr):
    global index
    index += 1
    IDX.append(index)
    A.append(team)
    B.append(abbr)

url = "https://www.reddit.com/r/CFB/wiki/abbreviations"

print ("Scrape Abbreviations Tool")
print ("**************************")
print ("data is from {0}".format(url))
print ("Directory Location: {0}".format(settings.data_path))
print ("**************************")

with contextlib.closing(urlopen(url)) as page:
    soup = BeautifulSoup(page, "html5lib")
tables=soup.findAll("table")

IDX=[]
A=[]
B=[]

# Add any Missing Teams Here
AddSchool("ALABAMA-BIRMINGHAM", "UAB")
AddSchool("LOUISIANA COLLEGE", "LC")
AddSchool("WESTERN KENTUCKY","WKU")
AddSchool("FLORIDA ATLANTIC","FAU")
AddSchool("WESTERN KENTUCKY","WKU")
# Add any Missing Teams Here

for row in tables[1].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0:
        tag = str(col[0].find(text=True)).strip()
        tag2 = str(col[0].find(href=True)).lower().strip()
        if (tag != "none" and tag != "team"):
            if ("#f" in tag2):
                index+=1
                IDX.append(index)
                A.append(pyBlitz.CleanString(tag))
                B.append(col[1].find(text=True))

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['Abbreviation']=B

Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
with open(settings.data_path + 'abbreviation.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(settings.data_path + "abbreviation.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)
stats_sheet = open(settings.data_path + 'abbreviation.csv', 'w', newline='')
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
