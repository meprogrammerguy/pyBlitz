#!/usr/bin/env python3

import json
import pdb
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import re
from datetime import datetime

import settings
import pyBlitz

def GetOverride(item, list_overrides):
    field = ""
    for ovr in list_overrides:
        if (item.lower().strip() == ovr[0].lower().strip()):
            field = ovr[1]
            break
    return field

now = datetime.now()
path = "{0}{1}/{2}".format(settings.predict_root, int(now.year), settings.predict_sched)
 
print ("Merge Schedule Tool")
print ("**************************")

file = '{0}merge_schedule.csv'.format(settings.data_path)
list_overrides = []
if (os.path.exists(file)):
    with open(file) as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            bpi = ""
            if (row["corrected stats team"].strip() > ""):
                bpi = row["corrected stats team"]
            if (bpi):
                list_overrides.append([row["scheduled team"], bpi])
file = '{0}sched1.json'.format(path)
if (not os.path.exists(file)):
    print ("schedule files are missing, run the scrape_schedule tool to create")
    exit()

list_sched = []
for p in Path(path).glob("sched*.json"):
    with open(p) as sched_files:
        list_sched.append(json.load(sched_files, object_pairs_hook=OrderedDict))

file = '{0}bornpowerindex.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("bornpowerindex file is missing, run the scrape_bornpowerindex tool to create")
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
    AllTeams.append(item["School"])
team_set = set(AllTeams)
stats_teams = list(team_set)
stats_teams.sort()

file = "{0}merge_schedule.csv".format(settings.data_path)
merge_sheet = open(file, 'w', newline='')
csvwriter = csv.writer(merge_sheet)
dict_merge = OrderedDict()
dict_merge["scheduled team"] = []
dict_merge["match ratio"] = []
dict_merge["stats team"] = []
dict_merge["corrected stats team"] = []
values = []
for item in sched_teams:
    key = process.extractOne(item, stats_teams, scorer=fuzz.QRatio)
    dict_merge["scheduled team"].append(pyBlitz.CleanString(item))
    dict_merge["match ratio"].append(key[1])
    dict_merge["stats team"].append(pyBlitz.CleanString(key[0]))
    ovr = GetOverride(item, list_overrides)
    dict_merge["corrected stats team"].append(ovr)
    values.append([item, key[1], key[0], ovr])

#pdb.set_trace()

csvwriter.writerow(dict_merge.keys())
for value in values:
    #pdb.set_trace()
    csvwriter.writerow(value)
merge_sheet.close()
print ("done.")
