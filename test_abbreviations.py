#!/usr/bin/env python3

import json
import pdb
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import datetime
import re
import sys, getopt

import settings
import scrape_schedule

def GetTeams(dict_merge):
    A=[]
    for team in dict_merge.values():
        A.append(team["BPI"])
    return A

def GetKey(abbr, dict_merge, team_list):
    key = {}
    loop = -1
    index = -1
    for team in dict_merge.values():
        loop += 1
        if (abbr == team["abbr"]):
            if (index != -1):
                print ("*** {0} is used for {1}[{2}] and {3}[{4}] in merge file"
                    .format(abbr, team_list[index], index, team_list[loop], loop))
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

print ("Test Abbreviation spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your abbreviations are set up correctly")
print ("    Tool will compare the scraped schedule abbreviations to the abbreviations")
print ("    from the combine_merge Tool and show anything that is strange")
print (" ")

now = datetime.datetime.now()
year = int(now.year)
lastyear = year - 1
path = "{0}{1}/{2}".format(settings.predict_root, lastyear, settings.predict_sched)

file = '{0}merge.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("merge.json file is missing, run the combine_merge tool to create")
    exit()
with open(file) as merge_file:
    dict_merge = json.load(merge_file, object_pairs_hook=OrderedDict)

scrape_schedule.year = lastyear
scrape_schedule.main(sys.argv[1:])
schedule_files = GetSchedFiles(path, "sched*.json")
if (not os.path.exists(schedule_files[0])):
    print ("schedule files are missing, run the scrape_schedule tool to create")
    exit()

list_schedule = []
for file in schedule_files:
    with open(file) as schedule_file:
        list_schedule.append(json.load(schedule_file, object_pairs_hook=OrderedDict))
AllAbbr=[]
for idx in range(len(schedule_files)):
    for item in list_schedule[idx].values():
        abbrw, abbrl = GetSchedAbbr(item["Score"])
        if (abbrw):
            AllAbbr.append(abbrw)
        if (abbrl):
            AllAbbr.append(abbrl)
abbr_set = set(AllAbbr)
abbr_codes = list(abbr_set)
abbr_codes.sort()

team_list = GetTeams(dict_merge)

for item in abbr_codes:
    team, index = GetKey(item, dict_merge, team_list)
    if (index == -1):
        print ("*** warning: could not find schedule abbreviation {0} in merge file".format(item))
    #else:
        #print ("merge [{0}], scheduled [{1}]".format(team_list[index], item))

print ("****************************************************************")
print ("done.")
