#!/usr/bin/env python3

import json
import pdb
import csv
from collections import OrderedDict
import os.path
from pathlib import Path

def FindTeams(stats_team, fixed_team, stats_teams):
    Found = False
    for team in stats_teams:
        if (team.rstrip() == stats_team.rstrip() and fixed_team.rstrip() == ""):
            Found = True
            break
        if (team.rstrip() == fixed_team.rstrip()):
            Found = True
            break
    return Found

print ("Merge spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your merge spreadsheet is set up correctly")
print ("    == be aware that some teams may not be there")
print ("    == for these match-ups a prediction will not be possible")
print ("    == (but a very, very, good guess is to go with the other team)")
print (" ")

file = 'merge.csv'
if (not os.path.exists(file)):
    print ("merge.csv file is missing, run the merge_teams tool to create")
    exit()
dict_merge = []
with open(file) as merge_file:
    reader = csv.DictReader(merge_file)
    for row in reader:
        dict_merge.append(row)

file = 'stats.json'
if (not os.path.exists(file)):
    print ("statistics file is missing, run the scrape_stats tool to create")
    exit()
with open(file) as stats_file:
    dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

AllTeams=[]
for item in  dict_stats.values():
    AllTeams.append(item["Team"])
team_set = set(AllTeams)
stats_teams = list(team_set)
stats_teams.sort()

for team in dict_merge:
    #pdb.set_trace()
    found = FindTeams(team["stats team"], team["corrected stats team"], stats_teams)
    if (not found):
        print ("warning: {0} was not found in the stats table ***".format(team["scheduled team"]))
 
print ("done.")
