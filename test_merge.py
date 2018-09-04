#!/usr/bin/env python3

import json
import pdb
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import re
import sys, getopt
from datetime import datetime

import settings
import scrape_schedule

def CurrentSchedFile(filename):
    if (not os.path.exists(filename)):
        return False
    stat = os.path.getmtime(filename)
    stat_date = datetime.fromtimestamp(stat)
    if stat_date.date() < datetime.now().date():
        return False
    return True

def GetTeams(keymatch, dict_merge):
    A=[]
    for team in dict_merge.values():
        key = team["BPI"].strip()
        if (key != "?"):
            A.append(key)
    return A

def GetKey(keymatch, item, dict_merge, team_list):
    key = {}
    loop = -1
    index = -1
    for team in dict_merge.values():
        loop += 1
        if (item == team[keymatch]):
            if (index != -1):
                print ("*** {0} is used for {1}[{2}] and {3}[{4}] in merge file"
                    .format(item, team_list[index], index, team_list[loop], loop))
            else:
                index = loop
                key = team
    return key, index

def GetSchedAbbr(scores):
    abbrw = ""
    abbrl = ""
    items = re.split(r'(,|\s)\s*', str(scores))
    if (items[0].strip() == "?"):   # Cancelled, Postponed or not yet Played Game
        return abbrw, abbrl
    if (len(items) != 7):
        return abbrw, abbrl
    abbrw = items[0]
    abbrl = items[4]
    return abbrw, abbrl

def GetWeek(item):
    filename = os.path.basename(str(item))
    idx = re.findall(r'\d+', str(filename))
    if (len(idx) == 0):
        idx.append("0")
    return int(idx[0])

def GetSchedFiles(path, templatename):
    A = []
    for p in Path(path).glob(templatename):
        A.append(str(p))
    file_list = []
    for item in range(0, 18):
        file_list.append("?")
    for item in A:
        idx = GetWeek(item)
        if (idx < len(file_list)):
            file_list[idx] = item
    file_list = [x for x in file_list if x != "?"]
    return file_list

print ("Test Master Merge spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your Master Merge Spreadsheet is as correct as possible")
print ("    Tool will compare the scraped schedule abbreviations to the abbreviations")
print ("    Tool will compare the scraped teamrankings to the teamrankings")
print ("    Tool will compare the scraped schedule teams to the schedule teams")
print ("An exceptions printout will be shown,")
print ("    try to correct as many issues as you can")
print ("*** Your predictions will be much more valuable ***")
print ("*** if you spend time doing this ***")
print ("*** I suggest using this tool once a year ***")
print ("*** before you start running score_week ***")
print (" ")

now = datetime.now()
year = int(now.year)
lastyear = year - 1
lastyear_path = "{0}{1}/{2}".format(settings.predict_root, lastyear, settings.predict_sched)
path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_sched)

file = '{0}merge.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("merge.json file is missing, run the combine_merge tool to create")
    exit()
with open(file) as merge_file:
    dict_merge = json.load(merge_file, object_pairs_hook=OrderedDict)

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

last_schedule_files = GetSchedFiles(lastyear_path, "sched*.json")
schedule_files = GetSchedFiles(path, "sched*.json")

if (not CurrentSchedFile(last_schedule_files[0])):
    scrape_schedule.year = lastyear
    scrape_schedule.main(sys.argv[1:])
    last_schedule_files = GetSchedFiles(lastyear_path, "sched*.json")

if (not CurrentSchedFile(schedule_files[0])):
    scrape_schedule.year = year
    scrape_schedule.main(sys.argv[1:])
    schedule_files = GetSchedFiles(path, "sched*.json")

if (not os.path.exists(schedule_files[0])):
    print ("schedule files are missing, run the scrape_schedule tool to create")
    exit()

schedule = []
for file in schedule_files:
    with open(file) as schedule_file:
        schedule.append(json.load(schedule_file, object_pairs_hook=OrderedDict))

if (not os.path.exists(last_schedule_files[0])):
    print ("last years schedule files are missing, run the scrape_schedule tool to create")
    exit()

last_schedule = []
for file in last_schedule_files:
    with open(file) as schedule_file:
        last_schedule.append(json.load(schedule_file, object_pairs_hook=OrderedDict))
AllAbbr=[]
for idx in range(len(last_schedule_files)):
    for item in last_schedule[idx].values():
        abbrw, abbrl = GetSchedAbbr(item["Score"])
        if (abbrw):
            AllAbbr.append(abbrw)
        if (abbrl):
            AllAbbr.append(abbrl)
abbr_set = set(AllAbbr)
abbr_codes = list(abbr_set)
abbr_codes.sort()

AllSchedTeams=[]
for idx in range(len(schedule_files)):
    for item in schedule[idx].values():
        AllSchedTeams.append(item["TeamA"])
        AllSchedTeams.append(item["TeamB"])
team_set = set(AllSchedTeams)
sched_codes = list(team_set)
sched_codes.sort()

AllRankTeams=[]
for item in dict_teamrankings.values():
    AllRankTeams.append(item["Team"])
team_set = set(AllRankTeams)
rank_codes = list(team_set)
rank_codes.sort()

team_list = GetTeams("BPI", dict_merge)

print ("Merge BPI count: {0}, Actual BPI count: {1}".format(len(team_list), len(dict_bpi)))
print ("Merge teamrankings count: {0}, Actual teamrankings count: {1}".format(len(team_list), len(dict_teamrankings)))
print ("Unique Scheduled teams: {0}".format(len(sched_codes)))

for item in abbr_codes:
    team, index = GetKey("abbr", item, dict_merge, team_list)
    if (index == -1):
        print ("*** warning: could not find schedule abbreviation [{0}] in merge file".format(item))

for item in rank_codes:
    team, index = GetKey("teamrankings", item, dict_merge, team_list)
    if (index == -1):
        print ("*** warning: could not find teamrankings [{0}] in merge file".format(item))

for item in sched_codes:
    team, index = GetKey("scheduled", item, dict_merge, team_list)
    if (index == -1):
        print ("*** warning: could not find schedule team [{0}] in merge file".format(item))

print ("****************************************************************")
print ("done.")
