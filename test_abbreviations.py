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

import scrape_schedule

path = "data/"

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

def GetCount(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("0")
    return int(idx[0])

def GetSchedFiles(templatename):
    file_dict = {}
    for p in Path(path).glob(templatename):
        idx = GetCount(p)
        file_dict[idx] = str(p)
    file_list = []
    for idx in range(len(file_dict)):
        file_list.append(file_dict[idx + 1])
    return file_list

print ("Test Abbreviation spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your abbreviations are set up correctly")
print ("    Tool will compare the scraped schedule abbreviations to the abbreviations")
print ("    from the combine_merge Tool and show anything that is strange")
print (" ")

file = '{0}merge.json'.format(path)
if (not os.path.exists(file)):
    print ("merge.json file is missing, run the combine_merge tool to create")
    exit()
with open(file) as merge_file:
    dict_merge = json.load(merge_file, object_pairs_hook=OrderedDict)

now = datetime.datetime.now()
year = int(now.year)
lastyear = year - 1
scrape_schedule.year = lastyear
scrape_schedule.main(sys.argv[1:])
schedule_files = GetSchedFiles("sched*.json")
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

scrape_schedule.year = year
scrape_schedule.main(sys.argv[1:])

print ("****************************************************************")
print ("done.")
