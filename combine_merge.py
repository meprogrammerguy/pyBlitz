#!/usr/bin/env python3

import json
import pdb
import pandas as pd
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import re

def CleanString(data):
    return re.sub(' +',' ', data)

path = "data/"

print ("Combine Merge Tool")
print ("**************************")
print (" ")
print ("This tool combines your merge spreadsheets into one master merge spreadsheet")
print ("Make sure that your merge_stats, merge_abbreviation, and merge_schedule")
print ("spreadsheets are correct first")
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
            if (not row_bpi):
                warning = team + " - ?" #This indicates there is a problem with the main key
                A.append(warning)
            else:
                A.append(team)
            B.append(teamrankings)
            break

df=pd.DataFrame(IDX,columns=['Index'])
df['BPI']=A
df['teamrankings']=B

with open(path + 'merge.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(path + "merge.json") as merge_json:
    dict_merge = json.load(merge_json, object_pairs_hook=OrderedDict)

merge_sheet = open(path + 'merge.csv', 'w', newline='')
csvwriter = csv.writer(merge_sheet)
count = 0
for row in dict_merge.values():
    if (count == 0):
        header = row.keys()
        csvwriter.writerow(header)
        count += 1
    csvwriter.writerow(row.values())
merge_sheet.close()
print ("done.")
