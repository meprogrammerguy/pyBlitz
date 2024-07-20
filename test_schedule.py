#!/usr/bin/env python3

import json
import pdb
import pandas as pd
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import datetime
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

print ("Test Schedule spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your scrape schedule spreadsheet has been run")
print ("    == be aware that some teams may not be there (unranked teams)")
print ("    == for these match-ups a prediction will not be possible")
print ("    == (but a very, very, good guess is to pick the 'better' team)")
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

print("... retrieving merge spreadsheet")
file = '{0}merge.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    merge_excel = "{0}merge.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(merge_excel, sheet_name='Sheet1')
    merge_json = json.loads(excel_df.to_json())
else:
    print ("        *** run combine_merge tool and then come back ***")
    exit()

scrape_schedule.year = year
scrape_schedule.main(sys.argv[1:])

print("... retrieving sched spreadsheet")
file = '{0}sched.xlsx'.format(path)
if (os.path.exists(file)):
    sched_excel = "{0}sched.xlsx".format(path)
    excel_df = pd.read_excel(sched_excel, sheet_name='Sheet1')
    sched_json = json.loads(excel_df.to_json())
else:
    print ("        *** run scrape_schedule tool and then come back ***")
    exit()

AllTeam=[]
for item in sched_json["Team 1"]:
    AllTeam.append(str(sched_json["Team 1"][str(item)]).strip())
for item in sched_json["Team 2"]:
    AllTeam.append(str(sched_json["Team 2"][str(item)]).strip())
team_set = set(AllTeam)
teams = list(team_set)
teams.sort()

MergeTeam=[]
for item in merge_json["team"]:
    MergeTeam.append(str(merge_json["team"][str(item)]).strip())
merge_set = set(MergeTeam)
merges = list(merge_set)
merges.sort()

s = set(merges)
bads = [x for x in teams if x not in s]

print (" ")
if bads:
    print ("*** warning: could not find these teams in the merge sheet")
    print ("*** fix your scrape_schedule sheet then come back")
    print ("*** some errors won't be correctable so do your best, then re-run")
    print (" ")
    print (" ")
    for bad in bads:
        print ("         " + bad)
    print (" ")
    print (str(len(bads)) + " team(s) not found in merge sheet.")
    print (" ")
    print ("... fail")
else:
    print ("scheduled teams")
    print ("... pass")
input("press enter for more results...")                
print (" ")
print ("****************************************************************")
print ("done.")
