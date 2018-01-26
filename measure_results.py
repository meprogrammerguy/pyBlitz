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
    newstr = newstr.replace("?", "")
    if (newstr.strip()==""):
        return -1
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
    import scrape_abbreviations

def GetActualScores(abbra, abbrb, scores):
    items = re.split(r'(,|\s)\s*', str(scores).lower())
    if (items[0].strip() == "?"):   # Cancelled Game
        return -1, -1
    if (len(items) != 7):
        return -1, -1
    if (abbra.lower().strip() not in items):
        print ("Missing Abbreviation [{0}] in Score {1}".format(abbra, scores))
        return -1, -1
    if (abbrb.lower().strip() not in items):
        print ("Missing Abbreviation [{0}] in Score {1}".format(abbrb, scores))
        return -1, -1
    if (abbra.lower().strip() == items[0].lower().strip()):
        scorea = int(items[2])
        scoreb = int(items[6])
    else:
        scorea = int(items[6])
        scoreb = int(items[2])
    return scorea, scoreb

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
alltotal = 0
allskip = 0
allcorrect = 0
for idx in range(len(list_sched)):
    total = 0
    skip = 0
    correct = 0
    for item in list_sched[idx].values():
        total += 1
        chancea = GetPercent(list_week[index]["ChanceA"])
        abbra = list_week[index]["AbbrA"]
        abbrb = list_week[index]["AbbrB"]
        index += 1
        scorea, scoreb = GetActualScores(abbra, abbrb, item["Score"])
        if (chancea < 0 or scorea < 0 or scoreb < 0 or abbra.strip() == "" or abbrb.strip() == ""):
            skip += 1
        else:
            if (chancea >= 50 and (scorea >= scoreb)):
                correct += 1
            if (chancea < 50 and (scorea < scoreb)):
                correct += 1
    print ("week{0} total={1}, skip={2}, correct={3} Percent={4}%".format(idx + 1, total, skip,
        correct, round(correct / (total - skip) * 100., 2)))
    alltotal = alltotal + total
    allskip = allskip + skip
    allcorrect = allcorrect + correct
print ("Totals total={0}, skip={1}, correct={2} Percent={3}%".format(alltotal, allskip,
    allcorrect, round(allcorrect / (alltotal - allskip) * 100., 2)))
print ("done.")
