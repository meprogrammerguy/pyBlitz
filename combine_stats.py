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
print ("This tool combines bornpowerindex and teamrankings into one stats spreadsheet")
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

file = '{0}bornpowerindex.json'.format(path)
if (not os.path.exists(file)):
    print ("bornpowerindex file is missing, run the scrape_bornpowerindex tool to create")
    exit()
with open(file) as stats_file:
    dict_bpi = json.load(stats_file, object_pairs_hook=OrderedDict)


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
E=[]
F=[]
G=[]
index = 0
for item in dict_merge:
    teamrankings = item['teamrankings'].lower().strip()
    team = item['corrected BPI'].lower().strip()
    if (team.strip() == ""):
        team = item['BPI'].lower().strip()
    for row in dict_bpi.values():
        if(row['School'].lower().strip()==team):
            index+=1
            IDX.append(str(index))
            A.append(team)
            B.append(row['Ranking'])
            C.append(row['Class'])
            break
    found = False
    for row in dict_teamrankings.values():
        if(row['Team'].lower().strip()==teamrankings):
            found = True
            D.append(row['PLpG3'])
            E.append(row['PTpP3'])
            F.append(row['OPLpG3'])
            G.append(row['OPTpP3'])
            break
    if (not found):
        D.append("?")
        E.append("?")
        F.append("?")
        G.append("?")
df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['Ranking']=B
df['Class']=C
df['PLpG3']=D
df['PTpP3']=E
df['OPLpG3']=F
df['OPTpP3']=G

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
