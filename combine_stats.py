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
import re

def CleanString(data):
    return re.sub(' +',' ', data)

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
H=[]
index = 0
for item in dict_merge:
    teamrankings = CleanString(item['teamrankings'])
    team = CleanString(item['BPI'])
    if (item['corrected BPI'].strip() != ""):
        team = CleanString(item['corrected BPI'])
    
    row_bpi = []
    for row in dict_bpi.values():
        if(row['School'].lower().strip()==team.lower().strip()):
            row_bpi = row  
            break
    for row in dict_teamrankings.values():
        if(row['Team'].lower().strip()==teamrankings.lower().strip()):
            index+=1
            IDX.append(str(index))
            A.append(team)
            B.append(teamrankings)
            if (row_bpi):
                C.append(row_bpi['Ranking'])
                D.append(row_bpi['Class'])
            else:
                C.append("?")
                D.append("?")
            E.append(row['PLpG3'])
            F.append(row['PTpP3'])
            G.append(row['OPLpG3'])
            H.append(row['OPTpP3'])
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
