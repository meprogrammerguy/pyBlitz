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
        if (team.strip() == stats_team.strip() and fixed_team.strip() == ""):
            Found = True
            break
        if (team.strip() == fixed_team.strip()):
            Found = True
            break
    return Found

print ("Test Schedule spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your merge Schedule spreadsheet is set up correctly")
print ("    == be aware that some teams may not be there (unranked teams)")
print ("    == for these match-ups a prediction will not be possible")
print ("    == (but a very, very, good guess is to go with the other team)")
print (" ")

file = 'merge_schedule.csv'
if (not os.path.exists(file)):
    print ("merge_schedule.csv file is missing, run the merge_schedule tool to create")
    exit()
dict_merge = []
with open(file) as merge_file:
    reader = csv.DictReader(merge_file)
    for row in reader:
        dict_merge.append(row)
path = "data/"
file = '{0}bornpowerindex.json'.format(path)
if (not os.path.exists(file)):
    print ("bornpowerindex file is missing, run the scrape_bornpowerindex tool to create")
    exit()
with open(file) as stats_file:
    dict_stats = json.load(stats_file, object_pairs_hook=OrderedDict)

AllTeams=[]
for item in  dict_stats.values():
    AllTeams.append(item["School"])
team_set = set(AllTeams)
stats_teams = list(team_set)
stats_teams.sort()

found = False
for team in dict_merge:
    if (team["corrected stats team"].strip()!=""):
        found = True

if (not found):
    print ("*** Warning: Have you set up your merge_schedule? There are NO fixes entered ***")
    print ("*** Make sure all of your match-ups are correct and then re-run this script ***")
    exit()

for team in dict_merge:
    found = FindTeams(team["stats team"], team["corrected stats team"], stats_teams)
    if (not found):
        print ("warning: {0} was not found in the stats table ***".format(team["scheduled team"]))
 
print ("done.")
