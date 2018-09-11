#!/usr/bin/env python3

import json
import pdb
import pandas as pd
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import re

import settings
import pyBlitz

print ("Combine Stats Tool")
print ("**************************")
print (" ")
print ("This tool combines bornpowerindex and teamrankings into one stats spreadsheet")
print ("Make sure that your merge_stats spreadsheet is correct first")
print (" ")

file = '{0}merge.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("Warning *** The merge.json file does not exist ***")
    print ("        *** run combine_merge tool and then come back ***")
    exit()
with open(file) as merge_file:
    dict_merge = json.load(merge_file, object_pairs_hook=OrderedDict)

file = '{0}bornpowerindex.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("bornpowerindex file is missing, run the scrape_bornpowerindex tool to create")
    exit()
with open(file) as stats_file:
    dict_bpi = json.load(stats_file, object_pairs_hook=OrderedDict)


file = '{0}teamrankings.json'.format(settings.data_path)
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
H=[]
index = 0
for item in dict_merge.values():
    teamrankings = pyBlitz.CleanString(item['teamrankings'])
    team = pyBlitz.CleanString(item['BPI'])
    
    row_team = []
    for row in dict_teamrankings.values():
        if(row['Team'].lower().strip()==teamrankings.lower().strip()):
            row_team = row  
            break

    for row in dict_bpi.values():
        if(row['School'].lower().strip()==team.lower().strip()):
            index+=1
            IDX.append(str(index))
            A.append(team)
            B.append(teamrankings)
            if (row_team):
                E.append(row_team['PLpG3'])
                F.append(row_team['PTpP3'])
                G.append(row_team['OPLpG3'])
                H.append(row_team['OPTpP3'])
            else:
                E.append("0")
                F.append("0")
                G.append("0")
                H.append("0")
            C.append(row['Ranking'])
            D.append(row['Class'])
            break

df=pd.DataFrame(IDX,columns=['Index'])
df['BPI']=A
df['teamrankings']=B
df['Ranking']=C
df['Class']=D
df['PLpG3']=E
df['PTpP3']=F
df['OPLpG3']=G
df['OPTpP3']=H

with open(settings.data_path + 'stats.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(settings.data_path + "stats.json") as stats_json:
    dict_stats = json.load(stats_json, object_pairs_hook=OrderedDict)

stats_sheet = open(settings.data_path + 'stats.csv', 'w', newline='')
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
