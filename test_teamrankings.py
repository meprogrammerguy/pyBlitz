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

print ("Test bornpowerindex spreadsheet validation Tool")
print ("****************************************************************")
print (" ")
print ("Makes sure that your merge bornpowerindex spreadsheet has been run")
print (" ")

print("... retrieving merge spreadsheet")
file = '{0}merge.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    merge_excel = "{0}merge.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(merge_excel, sheet_name='Sheet1')
    merge_json = json.loads(excel_df.to_json())
else:
    print ("        *** run combine_merge tool and then come back ***")
    exit()

print("... retrieving bornpowerindex spreadsheet")
bpi_file = '{0}bornpowerindex.xlsx'.format(settings.data_path)
if (os.path.exists(bpi_file)):
    excel_df = pd.read_excel(bpi_file, sheet_name='Sheet1')
    bpi_json = json.loads(excel_df.to_json())
else:
    print ("        *** run scrape_bornpowerindex tool and then come back ***")
    exit()

AllTeam=[]
for item in bpi_json["team"]:
    AllTeam.append(str(bpi_json["team"][str(item)]).strip())
team_set = set(AllTeam)
teams = list(team_set)
teams.sort()

MergeTeam=[]
for item in merge_json["bpi team"]:
    MergeTeam.append(str(merge_json["bpi team"][str(item)]).strip())
merge_set = set(MergeTeam)
merges = list(merge_set)
merges.sort()

s = set(merges)
bads = [x for x in teams if x not in s]

print (" ")
if bads:
    print ("*** warning: could not find these teams in the merge sheet")
    print ("*** fix your merge_bornpowerindex sheet then come back")
    print ("*** some errors won't be correctable so do your best, then re-run")
    print (" ")
    for bad in bads:
        print ("         " + bad)
    print (" ")
    print (str(len(bads)) + " team(s) not found in merge sheet.")
    print (" ")
    print ("... fail")
else:
        print ("... pass")
print (" ")
print ("****************************************************************")
print ("done.")
