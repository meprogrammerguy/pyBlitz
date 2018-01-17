#!/usr/bin/env python3

import json
import pdb
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
from datetime import datetime
import re

def GetIndex(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("0")
    return int(idx[0])

def GetFiles(path, templatename):
    file_dict = {}
    for p in Path(path).glob(templatename):
        idx = GetIndex(p)
        file_dict[idx] = str(p)
    file_list = []
    for idx in range(len(file_dict)):
        file_list.append(file_dict[idx + 1])
    return file_list

def CurrentScheduleFiles(filename):
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if stat_date.date() < datetime.now().date():
        return False
    return True

def RefreshScheduleFiles():
    import scrape_schedule

def GetActualScores(scores):
    idx = re.findall(r'\d+', str(scores))
    return idx[0], idx[1]

print ("Measure Actual Results Tool")
print ("**************************")

if (not CurrentScheduleFiles('data/sched1.json')):
    RefreshScheduleFiles()

file = 'data/sched1.json'
if (not os.path.exists(file)):
    print ("schedule files are missing, run the scrape_schedule tool to create")
    exit()

sched_files = GetFiles("data/", "sched*.json")
list_sched = []
for file in sched_files:
    with open(file) as sched_file:
        list_sched.append(json.load(sched_file, object_pairs_hook=OrderedDict))

week_files = GetFiles(".", "week*.csv")
list_week = []
for file in week_files:
    with open(file) as week_file:
        reader = csv.DictReader(week_file)
        for row in reader:
            list_week.append(row)

for idx in range(len(list_sched)):
    index = 0
    for item in list_sched[idx].values():
        scorea, scoreb = GetActualScores(item["Score"])
        print (list_week[idx]["ChanceA"])
        pdb.set_trace()

file = 'data/outsiders.json'
if (not os.path.exists(file)):
    print ("outsiders file is missing, run the scrape_outsiders tool to create")
    exit()
with open(file) as stats_file:
    dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

AllTeams=[]
for e in list_sched:
    for item in e.values():
        AllTeams.append(item["TeamA"])
        AllTeams.append(item["TeamB"])
team_set = set(AllTeams)
sched_teams = list(team_set)
sched_teams.sort()

AllTeams=[]
for item in  dict_stats.values():
    AllTeams.append(item["Team"])
team_set = set(AllTeams)
stats_teams = list(team_set)
stats_teams.sort()

merge_sheet = open('merge_schedule.csv', 'w', newline='')
csvwriter = csv.writer(merge_sheet)
dict_merge = OrderedDict()
dict_merge["match ratio"] = []
dict_merge["stats team"] = []
dict_merge["scheduled team"] = []
dict_merge["corrected stats team"] = []
values = []
for item in sched_teams:
    key = process.extractOne(item, stats_teams, scorer=fuzz.QRatio)
    dict_merge["match ratio"].append(key[1])
    dict_merge["stats team"].append(key[0])
    dict_merge["scheduled team"].append(item)
    dict_merge["corrected stats team"].append("")
    values.append([key[1], key[0], item,  ""])


csvwriter.writerow(dict_merge.keys())
for value in values:
    csvwriter.writerow(value)
merge_sheet.close()
print ("done.")
