#!/usr/bin/env python3

import json
import pdb
import csv
from collections import OrderedDict
import os.path
from pathlib import Path

import settings

def GetTeams(dict_merge):
    A=[]
    for team in dict_merge.values():
        A.append(team["BPI"])
    return A

def GetKey(team, dict_merge, team_list):
    key = {}
    loop = -1
    index = -1
    for item in dict_merge.values():
        loop += 1
        if (team == item["teamrankings"]):
            if (index != -1):
                print ("*** [{0}] is used for {1}[{2}] and {3}[{4}] in merge file"
                    .format(team, team_list[index], index, team_list[loop], loop))
            else:
                index = loop
                key = team
    return key, index

print ("Test stats spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your merge stats spreadsheet is set up correctly")
print ("    == be aware that all teams need to match up")
print ("    == if they do not a prediction will not be possible")
print (" ")

file = '{0}merge.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("merge.json file is missing, run the combine_merge tool to create")
    exit()
with open(file) as merge_file:
    dict_merge = json.load(merge_file, object_pairs_hook=OrderedDict)

file = '{0}teamrankings.json'.format(settings.data_path)
if (not os.path.exists(file)):
    print ("teamrankings file is missing, run the scrape_teamrankings tool to create")
    exit()
with open(file) as stats_file:
    dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

AllTeams=[]
for item in  dict_stats.values():
    AllTeams.append(item["Team"])
team_set = set(AllTeams)
stats_teams = list(team_set)
stats_teams.sort()

team_list = GetTeams(dict_merge)
 
for item in stats_teams:
    team, index = GetKey(item, dict_merge, team_list)
    if (index == -1):
        print ("*** warning: could not find teamrankings [{0}] in merge file".format(item))
    #else:
        #print ("BPI [{0}], teamrankings [{1}]".format(team_list[index], item))

print ("done.")
