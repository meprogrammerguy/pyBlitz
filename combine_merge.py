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

print ("Combine Merge Tool")
print ("**************************")
print (" ")
print ("This tool combines your merge spreadsheets into one master merge spreadsheet")
print ("Make sure that your merge_bornpowerindex, and merge_team_rankings")
print ("spreadsheets are correct first")
print (" ")

print("... retrieving teams JSON file")
file = '{0}teams.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    teams_excel = "{0}teams.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(teams_excel, sheet_name='Sheet1')
    teams_json = json.loads(excel_df.to_json())
else:
    print ("teams files are missing, run the scrape_teams tool to create")
    exit()

print("... retrieving merge_bornpowerindex JSON file")
file = '{0}merge_bornpowerindex.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    bpi_excel = "{0}merge_bornpowerindex.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(bpi_excel, sheet_name='Sheet1')
    bpi_json = json.loads(excel_df.to_json())
else:
    print ("merge_bornpowerindex files are missing, run the merge_bornpowerindex tool to create")
    exit()

print("... retrieving merge_teamrankings JSON file")
file = '{0}merge_teamrankings.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    rank_excel = "{0}merge_teamrankings.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(rank_excel, sheet_name='Sheet1')
    rank_json = json.loads(excel_df.to_json())
else:
    print ("merge_teamrankings files are missing, run the merge_teamrankings tool to create")
    exit()

IDX=[]
teams=[]
abbrs=[]
rank_teams=[]
bpi_teams=[]
index=0
for item in teams_json["displayName"]:
    team = teams_json["displayName"][item]
    abbr = teams_json["abbreviation"][item]
    bpi_found = False
    for bpi_item in bpi_json["abbr"]:
        bpi_team = bpi_json["bpi team"][bpi_item]
        bpi_abbr = bpi_json["abbr"][bpi_item]
        bpi_over = bpi_json["override"][bpi_item]
        if bpi_over > " ":
            bpi_team = bpi_over
        if abbr == bpi_abbr:
            bpi_found = True
            bpi_teams.append(bpi_team)
    rank_found = False
    for rank_item in rank_json["abbr"]:
        rank_team = rank_json["rankings team"][rank_item]
        rank_abbr = rank_json["abbr"][rank_item]
        rank_over = rank_json["override"][rank_item]
        if rank_over > " ":
            rank_team = rank_over
        if abbr == rank_abbr:
            rank_found = True
            rank_teams.append(rank_team)
    teams.append(team)
    abbrs.append(abbr)
    index+=1
    IDX.append(index)
    if not bpi_found:
        bpi_teams.append(" ")
    if not rank_found:
        rank_teams.append(" ")
    
print ("... creating merge JSON file")
the_file = "{0}merge.json".format(settings.data_path)
Path(settings.data_path).mkdir(parents=True, exist_ok=True)
df=pd.DataFrame(IDX,columns=['Index'])
df['team']=teams
df['abbr']=abbrs
df['rankings team']=rank_teams
df['bpi team']=bpi_teams
  
with open(the_file, 'w') as f:
    f.write(df.to_json(orient='index'))
f.close()
    
print ("... creating merge spreadsheet")
the_file = "{0}merge.xlsx".format(settings.data_path)
writer = pd.ExcelWriter(the_file, engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
