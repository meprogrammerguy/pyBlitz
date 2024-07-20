#!/usr/bin/env python3

import json
import pdb
import pandas as pd
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import re
import sys, getopt
from datetime import datetime

import settings
import scrape_schedule

def GetNumber(item):
    idx = re.findall(r'\d+', str(item))
    if (len(idx) == 0):
        idx.append("-1")
    return int(idx[0])

print ("Test Master Stats spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your Master Stats Spreadsheet is as correct as possible")
print ("    Tool will compare the scraped schedule teams to the stats teams")
print ("    Tool will compare the scraped teams to the stats teams")
print ("    Tool will compare the scraped teamrankings to the stats teamrankings")
print ("    Tool will compare the scraped bornpowerindex to the stats bornpowerindex")
print ("An exceptions printout will be shown,")
print ("    try to correct as many issues as you can")
print ("*** Your predictions will be much more valuable ***")
print ("*** if you spend time doing this ***")
print ("*** I suggest using this tool once a year ***")
print ("*** before you start running score_week ***")
print (" ")

year = 0
now = datetime.now()
year = int(now.year)
if (len(sys.argv)>=2):
    year = GetNumber(sys.argv[1])
    if (year < 2002 or year > int(now.year)):
        year = int(now.year)
current_working_directory = os.getcwd()
path = "{0}{1}/{2}".format(settings.predict_root, year, settings.predict_sched)

print("... retrieving stats spreadsheet")
file = '{0}stats.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    stats_excel = "{0}stats.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(stats_excel, sheet_name='Sheet1')
    stats_json = json.loads(excel_df.to_json())
else:
    print ("    *** run combine_stats tool and then come back ***")
    exit()

print("... retrieving teamrankings spreadsheet")
rank_file = '{0}teamrankings.xlsx'.format(settings.data_path)
if (os.path.exists(rank_file)):
    excel_df = pd.read_excel(rank_file, sheet_name='Sheet1')
    rank_json = json.loads(excel_df.to_json())
else:
    print ("    *** run scrape_teamrankings, merge_teamrankings, combine_merge and combine_stats and then come back ***")
    exit()
    
print("... retrieving teams spreadsheet")
team_file = '{0}teams.xlsx'.format(settings.data_path)
if (os.path.exists(team_file)):
    excel_df = pd.read_excel(team_file, sheet_name='Sheet1')
    team_json = json.loads(excel_df.to_json())
else:
    print ("    *** run scrape_teams, combine_merge and combine_stats and then come back ***")
    exit()

print("... retrieving bornpowerindex spreadsheet")
bpi_file = '{0}bornpowerindex.xlsx'.format(settings.data_path)
if (os.path.exists(bpi_file)):
    excel_df = pd.read_excel(bpi_file, sheet_name='Sheet1')
    bpi_json = json.loads(excel_df.to_json())
else:
    print ("    *** run scrape_bornpowerindex, merge_bornpowerindex, combine_merge and combine_stats and then come back ***")
    exit()

scrape_schedule.year = year
scrape_schedule.main(sys.argv[1:])

print("... retrieving current sched spreadsheet")
file = '{0}sched.xlsx'.format(path)
if (os.path.exists(file)):
    sched_excel = "{0}sched.xlsx".format(path)
    excel_df = pd.read_excel(sched_excel, sheet_name='Sheet1')
    sched_json = json.loads(excel_df.to_json())
else:
    print ("    *** run scrape_schedule tool and then come back ***")
    exit()
    
tTeam=[]
for item in team_json["shortDisplayName"]:
    tTeam.append(str(team_json["shortDisplayName"][str(item)]).strip())
tteam_set = set(tTeam)
tteams = list(tteam_set)
tteams.sort()

bpiTeam=[]
for item in bpi_json["team"]:
    bpiTeam.append(str(bpi_json["team"][str(item)]).strip())
bpiteam_set = set(bpiTeam)
bpiteams = list(bpiteam_set)
bpiteams.sort()

rankTeam=[]
for item in rank_json["team"]:
    rankTeam.append(str(rank_json["team"][str(item)]).strip())
rankteam_set = set(rankTeam)
rankteams = list(rankteam_set)
rankteams.sort()

schedTeam=[]
for item in sched_json["Team 1"]:
    schedTeam.append(str(sched_json["Team 1"][str(item)]).strip())
for item in sched_json["Team 2"]:
    schedTeam.append(str(sched_json["Team 2"][str(item)]).strip())
schedteam_set = set(schedTeam)
schedteams = list(schedteam_set)
schedteams.sort()

Statsrank=[]
for item in stats_json["teamrankings"]:
    Statsrank.append(str(stats_json["teamrankings"][str(item)]).strip())
rankstats_set = set(Statsrank)
rankstats = list(rankstats_set)
rankstats.sort()

Statsbpi=[]
for item in stats_json["BPI"]:
    Statsbpi.append(str(stats_json["BPI"][str(item)]).strip())
bpistats_set = set(Statsbpi)
bpistats = list(bpistats_set)
bpistats.sort()

StatsTeam=[]
for item in stats_json["team"]:
    StatsTeam.append(str(stats_json["team"][str(item)]).strip())
stats_set = set(StatsTeam)
stats = list(stats_set)
stats.sort()

s = set(stats)
schedbads = [x for x in schedteams if x not in s]
teambads = [x for x in tteams if x not in s]

s = set(bpistats)
start=len(bpistats)
end=len(bpiteams)
for i in range(start, end):
    bpiteams.pop()
bpibads = [x for x in bpiteams if x not in s]

s = set(rankstats)
rankbads = [x for x in rankteams if x not in s]

print (" ")
if teambads:
    print ("*** warning: could not find these teams in the merge sheet")
    print ("*** some errors won't be correctable so do your best, then re-run")
    print (" ")
    print (" ")
    for bad in teambads:
        print ("         " + bad)
    print (" ")
    print (str(len(teambads)) + " team(s) not found in merge sheet.")
    print (" ")
    print ("... fail")
else:
    print ("teams")
    print ("... pass")
input("press enter for more results...")                
print (" ")
if schedbads:
    print ("*** warning: could not find these scheduled teams in the merge sheet")
    print ("*** TBD as a team means the schedule is not yet firmed up (this is ok)")
    print ("*** some errors won't be correctable so do your best, then re-run")
    print (" ")
    print (" ")
    for bad in schedbads:
        print ("         " + bad)
    print (" ")
    print (str(len(schedbads)) + " team(s) not found in merge sheet.")
    print (" ")
    print ("... fail")
else:
    print ("scheduled teams")
    print ("... pass")
input("press enter for more results...")        
print (" ")
if rankbads:
    print ("*** warning: could not find these teamrankings teams in the merge sheet")
    print ("*** some errors won't be correctable so do your best, then re-run")
    print (" ")
    print (" ")
    for bad in rankbads:
        print ("         " + bad)
    print (" ")
    print (str(len(rankbads)) + " team(s) not found in merge sheet.")
    print (" ")
    print ("... fail")
else:
    print ("teamranking teams")
    print ("... pass")
input("press enter for more results...")                
print (" ")
if bpibads:
    print ("*** warning: could not find these bornpowerindex teams in the merge sheet")
    print ("*** the bornpowerindex has every team in the universe (so lots of warnings will happen)")
    print ("*** some errors won't be correctable so do your best, then re-run")
    print (" ")
    print (" ")
    for bad in bpibads:
        print ("         " + bad)
    print (" ")
    print (str(len(bpibads)) + " team(s) not found in merge sheet.")
    print (" ")
    print ("... fail")
else:
    print ("bornpowerindex teams")
    print ("... pass")
input("press enter for more results...")                
print ("****************************************************************")
print ("done.")
