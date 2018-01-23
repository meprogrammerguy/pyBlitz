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

def GetPercent(item):
    newstr = item.replace("%", "")
    return float(newstr)

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
    import scrape_abbreviation

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

index = 0
for idx in range(len(list_sched)):
    total = 0
    skip = 0
    correct = 0
    print ("week{0}".format(idx + 1))
    for item in list_sched[idx].values():
        total += 1
        scoreb, scorea = GetActualScores(item["Score"])
        #pdb.set_trace()
        chancea = GetPercent(list_week[index]["ChanceA"])
        index += 1
        if (chancea < 0 or scorea < 0 or scoreb < 0):
            print ("skip " + item["Score"])
            skip += 1
        else:
            print ("not skip {0}% - {1}".format(chancea, item["Score"]))
            if (chancea >= 50 and (scorea > scoreb)):
                print ("1) chancea={0}, scorea={1}, scoreb={2}".format(chancea, scorea, scoreb))
                correct += 1
            if (chancea < 50 and (scoreb > scorea)):
                print ("2) chancea={0}, scorea={1}, scoreb={2}".format(chancea, scorea, scoreb))
                correct += 1
    print ("total={0}, skip={1}, correct={2}".format(total, skip, correct))
    pdb.set_trace()
print ("done.")
