#!/usr/bin/env python3

import json
import pdb
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from collections import OrderedDict
import os.path
from pathlib import Path

print ("Merge Stats Tool")
print ("**************************")

file = 'merge_stats.csv'
if (os.path.exists(file)):
    print ("Warning *** The merge_stats.csv file already exists ***")
    print ("        *** delete this file if you want to re-create it. ***")
    exit()

file = 'data/outsiders.json'
if (not os.path.exists(file)):
    print ("outsiders file is missing, run the scrape_outsiders tool to create")
    exit()
with open(file) as stats_file:
    dict_outsiders = json.load(stats_file, object_pairs_hook=OrderedDict)


file = 'data/teamrankings.json'
if (not os.path.exists(file)):
    print ("teamrankings file is missing, run the scrape_teamrankings tool to create")
    exit()
with open(file) as stats_file:
    dict_teamrankings = json.load(stats_file, object_pairs_hook=OrderedDict)

AllTeams=[]
for item in  dict_outsiders.values():
    AllTeams.append(item["Team"])
team_set = set(AllTeams)
outsiders = list(team_set)
outsiders.sort()

AllTeams=[]
for item in  dict_teamrankings.values():
    AllTeams.append(item["Team"])
team_set = set(AllTeams)
teamrankings = list(team_set)
teamrankings.sort()

merge_sheet = open('merge_stats.csv', 'w', newline='')
csvwriter = csv.writer(merge_sheet)
dict_merge = OrderedDict()
dict_merge["match ratio"] = []
dict_merge["outsiders"] = []
dict_merge["teamrankings"] = []
dict_merge["corrected outsiders"] = []
values = []
for item in teamrankings:
    key = process.extractOne(item, outsiders, scorer=fuzz.QRatio)
    dict_merge["match ratio"].append(key[1])
    dict_merge["outsiders"].append(key[0])
    dict_merge["teamrankings"].append(item)
    dict_merge["corrected outsiders"].append("")
    values.append([key[1], key[0], item,  ""])


csvwriter.writerow(dict_merge.keys())
for value in values:
    csvwriter.writerow(value)
merge_sheet.close()
print ("done.")
