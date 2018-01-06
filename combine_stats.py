#!/usr/bin/env python3

import json
import pdb
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from collections import OrderedDict
import os.path
from pathlib import Path

path = "data/"

print ("Combine Stats Tool")
print ("**************************")
print (" ")
print ("This tool combines outsiders and teamrankings into one stats spreadsheet")
print ("Make sure that your merge_stats spreadsheet is correct first")
print (" ")

file = 'merge_stats.csv'
if (not os.path.exists(file)):
    print ("Warning *** The merge_stats.csv file does not exist ***")
    print ("        *** run merge_stats.py tool and then come back ***")
    exit()
dict_merge = []
with open(file) as merge_file:
    reader = csv.DictReader(merge_file)
    for row in reader:
        dict_merge.append(row)

file = '{0}outsiders.json'.format(path)
if (not os.path.exists(file)):
    print ("outsiders file is missing, run the scrape_outsiders tool to create")
    exit()
with open(file) as stats_file:
    dict_outsiders = json.load(stats_file, object_pairs_hook=OrderedDict)


file = '{0}teamrankings.json'.format(path)
if (not os.path.exists(file)):
    print ("teamrankings file is missing, run the scrape_teamrankings tool to create")
    exit()
with open(file) as stats_file:
    dict_teamrankings = json.load(stats_file, object_pairs_hook=OrderedDict)
IDX=[]
A=[]
B=[]
C=[]
D=[]
index = 0
for item in dict_merge:
    teamrankings = item['teamrankings']
    team = item['corrected outsiders']
    if (team.strip() == ""):
        team = item['outsiders']
    for row in dict_outsiders.values():
        if(row['Team']==team):
            index+=1
            IDX.append(str(index))
            A.append(team)
            B.append(row['S&P+M'])
            break
    for row in dict_teamrankings.values():
        if(row['Team']==teamrankings):
            C.append(row['PLpG3'])
            D.append(row['OPTpP3'])
            break

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['S&P+M']=B
df['PLpG3']=C
df['OPTpP3']=D

with open(path + 'stats.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(path + "stats.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)

stats_sheet = open(path + 'stats.csv', 'w', newline='')
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
