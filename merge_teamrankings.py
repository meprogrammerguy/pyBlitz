#!/usr/bin/env python3

import json
import pdb
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import re
import pandas as pd

import settings
import pyBlitz

print ("Merge teamrankings Tool")
print ("**************************")

print("... retrieving teams JSON file")
file = '{0}teams.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    teams_excel = "{0}teams.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(teams_excel, sheet_name='Sheet1')
    teams_json = json.loads(excel_df.to_json())
else:
    print ("teams files are missing, run the scrape_teams tool to create")
    exit()

print("... retrieving teamrankings JSON file")
file = '{0}teamrankings.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    rank_excel = "{0}teamrankings.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(rank_excel, sheet_name='Sheet1')
    rank_json = json.loads(excel_df.to_json())
else:
    print ("teamrankings files are missing, run the scrape_teamrankings tool to create")
    exit()
    
print("... checking for existing overrides in merge_teamrankings")
print (" ")
file = '{0}merge_teamrankings.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    over_excel = "{0}merge_teamrankings.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(over_excel, sheet_name='Sheet1')
    over_json = json.loads(excel_df.to_json())
    overrides = over_json["override"]
    over = False
    for item in over_json["override"]:
        test = over_json["override"][item]
        if (str(test).strip() > "") and (test != None):
            over = True
            break
    if over:
        print ("*** warning, some overrides have been found ***")
        print ("...     if you really want to run")
        print ("...     remove the overrides or delete merge_teamrankings.xlsx")
        print ("... exiting")
        print ("***")
        exit()

IDX=[]
teams=[]
abbrs=[]
rank_teams=[]
over=[]
index=0
for item in teams_json["shortDisplayName"]:
    team = teams_json["shortDisplayName"][item]
    abbr = teams_json["abbreviation"][item]
    found = False
    for rank_item in rank_json["abbr"]:
        rank_abbr = rank_json["abbr"][rank_item]
        rank_team = rank_json["team"][rank_item]
        if abbr == rank_abbr:
            found = True
            rank_teams.append(rank_team)

    teams.append(team)
    abbrs.append(abbr)
    over.append(" ")
    index+=1
    IDX.append(index)
    if not found:
        rank_teams.append(" ")
    
df=pd.DataFrame(IDX,columns=['Index'])
df['team']=teams
df['abbr']=abbrs
df['rankings team']=rank_teams
df['override']=over
  
print ("... creating merge_teamrankings JSON file")
the_file = "{0}json/merge_teamrankings.json".format(settings.data_path)
the_path = "{0}json/".format(settings.data_path)
Path(the_path).mkdir(parents=True, exist_ok=True)
with open(the_file, 'w') as f:
    f.write(df.to_json(orient='index'))
f.close()
    
print ("... creating merge_teamrankings spreadsheet")
the_file = "{0}merge_teamrankings.xlsx".format(settings.data_path)
writer = pd.ExcelWriter(the_file, engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
