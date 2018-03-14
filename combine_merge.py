#!/usr/bin/env python3

import json
import pdb
import pandas as pd
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import re
from datetime import datetime

import settings

def GetCount(item):
    filename = os.path.basename(str(item))
    idx = re.findall(r'\d+', str(filename))
    if (len(idx) == 0):
        idx.append("0")
    return int(idx[0])

def GetSchedFiles(path, templatename):
    A = []
    for p in Path(path).glob(templatename):
        A.append(str(p))
    file_list = []
    for item in range(0, 17):
        file_list.append("?")
    for item in A:
        idx = GetCount(item)
        file_list[idx] = item
    file_list = [x for x in file_list if x != "?"]
    return file_list

def GetIndex(BPI_list, team):
    index = -1
    loop = -1
    for itm in BPI_list:
        loop += 1
        if (itm.lower().strip() == team.lower().strip()):
            index = loop
    return index

def CleanString(data):
    return re.sub(' +',' ', data)

print ("Combine Merge Tool")
print ("**************************")
print (" ")
print ("This tool combines your merge spreadsheets into one master merge spreadsheet")
print ("Make sure that your merge_stats, merge_abbreviation, and merge_schedule")
print ("spreadsheets are correct first")
print (" ")

file = '{0}merge_stats.csv'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("Warning *** The merge_stats.csv file does not exist ***")
    print ("        *** run merge_stats tool and then come back ***")
    exit()
dict_stats_merge = []
with open(file) as stats_file:
    reader = csv.DictReader(stats_file)
    for row in reader:
        dict_stats_merge.append(row)

file = '{0}merge_abbreviation.csv'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("Warning *** The merge_abbreviation.csv file does not exist ***")
    print ("        *** run merge_abbreviations tool and then come back ***")
    exit()
dict_abbr_merge = []
with open(file) as abbr_file:
    reader = csv.DictReader(abbr_file)
    for row in reader:
        dict_abbr_merge.append(row)

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

file = '{0}abbreviation.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("abbreviation file is missing, run the scrape_abbreviation tool to create")
    exit()
with open(file) as abbr_file:
    dict_abbr = json.load(abbr_file, object_pairs_hook=OrderedDict)

dict_sched_merge = []
file = '{0}merge_schedule.csv'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("merge_schedule file is missing, run the merge_schedule tool to create")
    exit()
with open(file) as sched_file:
    reader = csv.DictReader(sched_file)
    for row in reader:
        dict_sched_merge.append(row)

now = datetime.now()
path = "{0}{1}/{2}".format(settings.predict_root, int(now.year), settings.predict_sched)
schedule_files = GetSchedFiles(path, "sched*.json")
list_schedule = []
for file in schedule_files:
    with open(file) as schedule_file:
        list_schedule.append(json.load(schedule_file, object_pairs_hook=OrderedDict))

IDX=[]
A=[]
B=[]
C=[]
D=[]
E=[]
F=[]
index = 0
for row in dict_bpi.values():   #Main key put every one in
    A.append(row["School"])
    B.append("?")
    C.append("?")
    D.append("?")
    E.append("?")
    F.append(row["Class"])
    index+=1
    IDX.append(str(index))

for item in dict_stats_merge:
    teamrankings = CleanString(item['teamrankings'])
    team = CleanString(item['BPI'])
    if (item['corrected BPI'].strip() != ""):
        team = CleanString(item['corrected BPI'])
    index = GetIndex(A, team)    
    for row in dict_teamrankings.values():
        if(row['Team'].lower().strip()==teamrankings.lower().strip()):
            if (index > -1):
                B[index] = teamrankings
                break

for item in dict_abbr_merge:
    abbr_team = CleanString(item['abbr team'])
    stats = CleanString(item["stats team"].lower().strip())
    if (item["corrected stats team"].lower().strip()):
        stats =  CleanString(item["corrected stats team"].lower().strip())
    abbr = item["abbreviation"].strip()
    if (item["corrected abbr"].strip()):
        abbr =  item["corrected abbr"].strip()
    index = GetIndex(A, stats)    
    for row in dict_abbr.values():
        if(row['Team'].lower().strip()==abbr_team.lower().strip()):
            if (index > -1):
                D[index] = abbr_team
                E[index] = abbr
                break

for item in dict_sched_merge:
    scheduled = CleanString(item['scheduled team'])
    stats = CleanString(item["stats team"].lower().strip())
    if (item["corrected stats team"].lower().strip()):
        stats =  CleanString(item["corrected stats team"].lower().strip())
    index = GetIndex(A, stats)    
    for idx in range(len(schedule_files)):
        for row in list_schedule[idx].values():
            if(row['TeamA'].lower().strip()==scheduled.lower().strip()):
                if (index > -1):
                    C[index] = scheduled
                    break
            if(row['TeamB'].lower().strip()==scheduled.lower().strip()):
                if (index > -1):
                    C[index] = scheduled
                    break

df=pd.DataFrame(IDX,columns=['Index'])
df['BPI']=A
df['teamrankings']=B
df['scheduled']=C
df['abbr team']=D
df['abbr']=E
df['class']=F

with open(settings.data_path + 'merge.json', 'w') as f:
    f.write(df.to_json(orient='index'))

with open(settings.data_path + "merge.json") as merge_json:
    dict_merge = json.load(merge_json, object_pairs_hook=OrderedDict)

merge_sheet = open(settings.data_path + 'merge.csv', 'w', newline='')
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
