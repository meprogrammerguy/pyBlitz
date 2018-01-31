#!/usr/bin/env python3

import json
import pdb
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
from datetime import datetime
import re
import pandas as pd
import sys

import settings
import scrape_schedule

def CalcPercent(total, skip, correct):
    try:
        return  round(correct / (total - skip) * 100., 2)
    except ZeroDivisionError:
        return None

def GetPercent(item):
    newstr = item.replace("%", "")
    newstr = newstr.replace("?", "")
    if (newstr.strip()==""):
        return -1
    return float(newstr)

def GetIndex(item):
    filename = os.path.basename(str(item))
    idx = re.findall(r'\d+', str(filename))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

def GetFiles(path, templatename):
    A = []
    files = Path(path).glob(templatename)
    for p in files:
        A.append(p)
    file_list = []
    for item in range(0, 17):
        file_list.append("?")
    for item in A:
        idx = GetIndex(item)
        file_list[idx] = item
    file_list = [x for x in file_list if x != "?"]
    return file_list

def CurrentScheduleFiles(filename):
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if stat_date.date() < datetime.now().date():
        return False
    return True

def RefreshScheduleFiles():
    now = datetime.now()
    year = int(now.year)
    scrape_schedule.year = year
    scrape_schedule.main(sys.argv[1:])

def GetActualScores(abbra, abbrb, scores):
    items = re.split(r'(,|\s)\s*', str(scores).lower())
    if (not items):
        return -1, -1
    if (items[0].strip() == "?"):   # Cancelled, Postponed or not yet Played Game
        return -1, -1
    if (len(items) != 7):
        return -1, -1
    if (abbra.lower().strip() not in items):
        if (verbose):
            print ("Missing Abbreviation [{0}] [{1}] in Score {2}".format(abbra, abbrb, scores))
        return -1, -1
    if (abbrb.lower().strip() not in items):
        if (verbose):
            print ("Missing Abbreviation [{0}] [{1}] in Score {2}".format(abbra, abbrb, scores))
        return -1, -1
    if (abbra.lower().strip() == items[0].lower().strip()):
        scorea = int(items[2])
        scoreb = int(items[6])
    else:
        scorea = int(items[6])
        scoreb = int(items[2])
    return scorea, scoreb

now = datetime.now()
predict_path = "{0}{1}/".format(settings.predict_root, int(now.year))
verbose = False
if (len(sys.argv)==2):
    verbose = True

    print ("Measure Actual Results Tool")
    print ("**************************")

if (not CurrentScheduleFiles(settings.data_path + 'sched1.json')):
    RefreshScheduleFiles()

file = '{0}sched1.json'.format(settings.data_path)
if (not os.path.exists(file)):
    if (verbose):
        print ("schedule files are missing, run the scrape_schedule tool to create")
    exit()

file = '{0}week1.csv'.format(predict_path)
if (not os.path.exists(file)):
    if (verbose):
        print ("Weekly files are missing, run the score_week tool to create")
    exit()

sched_files = GetFiles(settings.data_path, "sched*.json")
list_sched = []
for file in sched_files:
    with open(file) as sched_file:
        item = json.load(sched_file, object_pairs_hook=OrderedDict)
        item['Week'] = GetIndex(file)
        list_sched.append(item)
week_files = GetFiles(predict_path, "week*.csv")
list_week = []
for file in week_files:
    with open(file) as week_file:
        reader = csv.DictReader(week_file)
        for row in reader:
            row['Week'] = GetIndex(file)
            list_week.append(row)
IDX=[]
A=[]
B=[]
C=[]
D=[]
E=[]
index = 0
alltotal = 0
allskip = 0
allcorrect = 0
count = 0
for idx in range(len(list_sched)):
    total = 0
    skip = 0
    correct = 0
    week = list_sched[idx]["Week"]
    for item in list_sched[idx].values():
        if (item == week):
            break
        total += 1
        chancea = -1
        abbra = ""
        abbrb = ""
        if (index < len(list_week) and list_week[index]["Week"] == week):
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
    count += 1
    IDX.append(count)
    A.append(week)
    B.append(total)
    C.append(skip)
    D.append(correct)
    E.append(CalcPercent(total, skip, correct))
    if (verbose):
        print ("week{0} total={1}, skip={2}, correct={3} Percent={4}%".format(week, total, skip,
            correct, CalcPercent(total, skip, correct)))
    alltotal = alltotal + total
    allskip = allskip + skip
    allcorrect = allcorrect + correct
count += 1
IDX.append(count)
A.append(99)
B.append(alltotal)
C.append(allskip)
D.append(allcorrect)
E.append(CalcPercent(alltotal, allskip, allcorrect))

if (verbose):
    print ("====================================================================")
    print ("Totals total={0}, skip={1}, correct={2} Percent={3}%".format(alltotal, allskip,
        allcorrect, CalcPercent(alltotal, allskip, allcorrect)))
    print ("====================================================================")

df=pd.DataFrame(IDX,columns=['Index'])
df['Week']=A
df['Total Games']=B
df['Count Unpredicted']=C
df['Count Correct']=D
df['Percent Correct']=E

file = "{0}results.json".format(predict_path)
with open(file, 'w') as f:
    f.write(df.to_json(orient='index'))

with open(file) as results_json:
    dict_results = json.load(results_json, object_pairs_hook=OrderedDict)

file = "{0}results.csv".format(predict_path)
results_sheet = open(file, 'w', newline='')
csvwriter = csv.writer(results_sheet)
count = 0
for row in dict_results.values():
    if (count == 0):
        header = row.keys()
        csvwriter.writerow(header)
        count += 1
    csvwriter.writerow(row.values())
results_sheet.close()
print ("done.")
