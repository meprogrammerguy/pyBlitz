#!/usr/bin/env python3

import json
import pdb
import csv
from collections import OrderedDict
import os.path
from pathlib import Path

import settings

def FindTeams(stats_team, fixed_team, stats_teams):
    Found = False
    for team in stats_teams:
        if (team.strip() == stats_team.strip() and fixed_team.strip() == ""):
            Found = True
            break
        if (team.strip() == fixed_team.strip()):
            Found = True
            break
    return Found

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
 
print ("done.")
