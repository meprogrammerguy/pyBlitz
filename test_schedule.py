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

def GetKey(team, dict_merge, team_list):
    key = {}
    loop = -1
    index = -1
    for itm in dict_merge.values():
        loop += 1
        if (team == itm["scheduled"]):
            if (index != -1):
                print ("*** {0} is used for {1}[{2}] and {3}[{4}] in merge file"
                    .format(team, team_list[index], index, team_list[loop], loop))
            else:
                index = loop
                key = itm
    return key, index

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
    for item in range(0, 16):
        file_list.append("?")
    for item in A:
        idx = GetWeek(item)
        if (len(file_list) > idx):
            file_list[idx] = item
    file_list = [x for x in file_list if x != "?"]
    return file_list

print ("Test Schedule spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your merge Schedule spreadsheet is set up correctly")
print ("    == be aware that some teams may not be there (unranked teams)")
print ("    == for these match-ups a prediction will not be possible")
print ("    == (but a very, very, good guess is to go with the other team)")
print (" ")

now = datetime.datetime.now()
year = int(now.year)
path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_sched)

file = '{0}merge.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("merge.json file is missing, run the combine_merge tool to create")
    exit()
with open(file) as merge_file:
    dict_merge = json.load(merge_file, object_pairs_hook=OrderedDict)

scrape_schedule.year = year
scrape_schedule.main(sys.argv[1:])
schedule_files = GetSchedFiles(path, "sched*.json")

if (not os.path.exists(schedule_files[0])):
    print ("schedule files are missing, run the scrape_schedule tool to create")
    exit()

list_schedule = []
for file in schedule_files:
    with open(file) as schedule_file:
        list_schedule.append(json.load(schedule_file, object_pairs_hook=OrderedDict))
AllTeam=[]
for idx in range(len(schedule_files)):
    for item in list_schedule[idx].values():
        AllTeam.append(item["TeamA"])
        AllTeam.append(item["TeamA"])
team_set = set(AllTeam)
teams = list(team_set)
teams.sort()
#pdb.set_trace()

team_list = GetTeams(dict_merge)

for item in teams:
    #pdb.set_trace()
    team, index = GetKey(item, dict_merge, team_list)
    if (index == -1):
        print ("*** warning: could not find schedule team [{0}] in merge file".format(item))
    #else:
        #print ("BPI [{0}], teamrankings [{1}]".format(team_list[index], item))

print ("****************************************************************")
print ("done.")
