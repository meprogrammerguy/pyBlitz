#!/usr/bin/env python3

import json
import pdb
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from collections import OrderedDict
import os.path
from pathlib import Path

print ("Merge Teams Tool")
print ("**************************")
file = 'week1.json'
if (not os.path.exists(file)):
    print ("schedule files are missing, run the scrape_schedule tool to create")
    exit()

for p in Path(".").glob("week*.json"):
    with open(p) as sched_files:
        dict_sched = json.load(sched_files, object_pairs_hook=OrderedDict)

file = 'stats.json'
if (not os.path.exists(file)):
    print ("statistics file is missing, run the scrape_stats tool to create")
    exit()
with open(file) as stats_file:
    dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

AllTeams=[]
for item in dict_sched.values():
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

merge_sheet = open('merge.csv', 'w', newline='')
csvwriter = csv.writer(merge_sheet)
dict_merge = OrderedDict()
dict_merge["sched team"] = []
dict_merge["stats team"] = []
dict_merge["ratio"] = []
dict_merge["fixed stats team"] = []
values = []
for item in sched_teams:
    dict_merge["sched team"].append(item)
    statskey = process.extractOne(item, stats_teams, scorer=fuzz.token_sort_ratio)
    dict_merge["stats team"].append(statskey[0])
    dict_merge["ratio"].append(statskey[1])
    dict_merge["fixed stats team"].append("")
    values.append([item,statskey[0],statskey[1],""])

csvwriter.writerow(dict_merge.keys())
for value in values:
    csvwriter.writerow(value)
merge_sheet.close()
print ("done.")
