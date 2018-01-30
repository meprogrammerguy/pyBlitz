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

import settings

def CleanString(data):
    return re.sub(' +',' ', data)

print ("Merge Stats Tool")
print ("**************************")

file = '{0}merge_stats.csv'.format(settings.data_path)
if (os.path.exists(file)):
    print ("Warning *** The merge_stats.csv file already exists ***")
    print ("        *** delete this file if you want to re-create it. ***")
    exit()

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

AllTeams=[]
for item in  dict_bpi.values():
    AllTeams.append(item["School"])
team_set = set(AllTeams)
bpi = list(team_set)
bpi.sort()

AllTeams=[]
for item in  dict_teamrankings.values():
    AllTeams.append(item["Team"])
team_set = set(AllTeams)
teamrankings = list(team_set)
teamrankings.sort()

file = "{0}merge_stats.csv".format(settings.data_path)
merge_sheet = open(file, 'w', newline='')
csvwriter = csv.writer(merge_sheet)
dict_merge = OrderedDict()
dict_merge["teamrankings"] = []
dict_merge["match ratio"] = []
dict_merge["BPI"] = []
dict_merge["corrected BPI"] = []
values = []
for item in teamrankings:
    key = process.extractOne(item, bpi, scorer=fuzz.QRatio)
    dict_merge["teamrankings"].append(CleanString(item))
    dict_merge["match ratio"].append(key[1])
    dict_merge["BPI"].append(CleanString(key[0]))
    dict_merge["corrected BPI"].append("")
    values.append([item, key[1], key[0], ""])

csvwriter.writerow(dict_merge.keys())
for value in values:
    csvwriter.writerow(value)
merge_sheet.close()
print ("done.")
