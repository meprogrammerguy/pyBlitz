#!/usr/bin/env python3

import json
import pdb
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from collections import OrderedDict
import os.path
from pathlib import Path

print ("Merge Abbreviation Tool")
print ("**************************")

file = 'merge_abbreviation.csv'
if (os.path.exists(file)):
    print ("Warning *** The merge_abbreviation.csv file already exists ***")
    print ("        *** delete this file if you want this tool to re-create it. ***")
    exit()

file = 'data/abbreviation.json'
if (not os.path.exists(file)):
    print ("abbreviation files are missing, run the scrape_abbreviation tool to create")
    exit()

with open(file) as abbr_file:
    dict_abbr = json.load(abbr_file, object_pairs_hook=OrderedDict)

file = 'data/bornpowerindex.json'
if (not os.path.exists(file)):
    print ("bornpowerindex file is missing, run the scrape_bornpowerindex tool to create")
    exit()
with open(file) as stats_file:
    dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

AllTeams=[]
for item in  dict_abbr.values():
    AllTeams.append(item["Team"])
team_set = set(AllTeams)
teams_abbr = list(team_set)
teams_abbr.sort()

AllTeams=[]
for item in  dict_stats.values():
    AllTeams.append(item["School"])
team_set = set(AllTeams)
stats_teams = list(team_set)
stats_teams.sort()

merge_sheet = open('merge_abbreviation.csv', 'w', newline='')
csvwriter = csv.writer(merge_sheet)
dict_merge = OrderedDict()
dict_merge["match ratio"] = []
dict_merge["stats team"] = []
dict_merge["abbr team"] = []
dict_merge["corrected stats team"] = []
values = []
for item in teams_abbr:
    key = process.extractOne(item, stats_teams, scorer=fuzz.QRatio)
    dict_merge["match ratio"].append(key[1])
    dict_merge["stats team"].append(key[0])
    dict_merge["abbr team"].append(item)
    dict_merge["corrected stats team"].append("")
    values.append([key[1], key[0], item,  ""])


csvwriter.writerow(dict_merge.keys())
for value in values:
    csvwriter.writerow(value)
merge_sheet.close()
print ("done.")
