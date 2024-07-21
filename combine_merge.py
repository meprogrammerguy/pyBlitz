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
print ("Make sure that your merge_bornpowerindex, and merge_teamrankings")
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
bpi_overs={}
rank_overs={}
index=0
for item in teams_json["shortDisplayName"]:
    team = teams_json["shortDisplayName"][item]
    abbr = teams_json["abbreviation"][item]
    for bpi_item in bpi_json["team"]:
        key_team = bpi_json["team"][bpi_item]
        bpi_team = pyBlitz.CleanString(str(bpi_json["bpi team"][bpi_item]).strip())
        if (bpi_team.strip() == "?") or (bpi_team.strip() == "") or (bpi_team == "None") or (bpi_team == None):
            bpi_team = " "
        bpi_over = pyBlitz.CleanString(str(bpi_json["override"][bpi_item]).strip())
        if (bpi_over.strip() == "?") or (bpi_over.strip() == "") or (bpi_over == "None") or (bpi_over == None):
            bpi_over = " "
        if team == key_team:
            if len(bpi_over.strip()) > 0:
                bpi_overs[item] = bpi_over
            bpi_teams.append(bpi_team)
    for rank_item in rank_json["team"]:
        key_team = str(rank_json["team"][rank_item]).strip()
        rank_team = pyBlitz.CleanString(str(rank_json["rankings team"][rank_item]).strip())
        if (rank_team.strip() == "?") or (rank_team.strip() == "") or (rank_team == "None") or (rank_team == None):
            rank_team = " "
        rank_over = pyBlitz.CleanString(str(rank_json["override"][rank_item]).strip())   
        if (rank_over.strip() == "?") or (rank_over.strip() == "") or (rank_over == "None") or (rank_over == None):
            rank_over = " "
        if team == key_team:
            if len(rank_over.strip()) > 0:
                rank_overs[item] = rank_over
            rank_teams.append(rank_team)
    teams.append(team)
    abbrs.append(abbr)
    index+=1
    IDX.append(index)

for ovr in bpi_overs:
    bpi_team = bpi_overs[str(ovr)]
    if (bpi_team == "None") or (bpi_team == None):
        bpi_team = ""
    if len(bpi_team.strip()) > 0:
        bpi_teams[int(ovr)] = pyBlitz.CleanString(bpi_team)
for ovr in rank_overs:
    rank_team = rank_overs[str(ovr)]
    if (rank_team == "None") or (bpi_team == None):
        rank_team = "" 
    if len(rank_team.strip()) > 0:
        rank_teams[int(ovr)] = pyBlitz.CleanString(rank_team)
    
df=pd.DataFrame(IDX,columns=['Index'])
df['team']=teams
df['abbr']=abbrs
df['rankings team']=rank_teams
df['bpi team']=bpi_teams
  
print ("... creating merge JSON file")
the_file = "{0}json/merge.json".format(settings.data_path)
the_path = "{0}json/".format(settings.data_path)
Path(the_path).mkdir(parents=True, exist_ok=True)
with open(the_file, 'w') as f:
    f.write(df.to_json(orient='index'))
f.close()
    
print ("... creating merge spreadsheet")
the_file = "{0}merge.xlsx".format(settings.data_path)
writer = pd.ExcelWriter(the_file, engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
