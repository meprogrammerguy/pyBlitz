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
        idx.append("-1")
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
    if (len(idx) == 0):
        idx.append("-1")
        idx.append("-1")
    return int(idx[0]), int(idx[1])

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
    total = 0
    skip = 0
    correct = 0
    loop = 0
    for item in list_sched[idx].values():
        total += 1
        scorea, scoreb = GetActualScores(item["Score"])
        chancea = GetIndex(list_week[loop]["ChanceA"])
        chanceb = GetIndex(list_week[loop]["ChanceB"])
        loop += 1
        if (chancea < 0 or chanceb < 0 or scorea < 0 or scoreb < 0):
            print ("skip " + item["Score"])
            skip += 1
        else:
            print ("not skip " + item["Score"])
            if (chancea > 50 and scorea > scoreb):
                print ("1) chance={0}, scorea={1}, scoreb={2}".format(chancea, scorea, scoreb))
                correct += 1
            if (chanceb > 50 and scoreb > scorea):
                print ("2) chance={0}, scorea={1}, scoreb={2}".format(chanceb, scorea, scoreb))
                correct += 1
    print ("total={0}, skip={1}, correct={2}".format(total, skip, correct))
    pdb.set_trace()

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
