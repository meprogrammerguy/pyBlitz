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

print ("Merge bornpowerindex Tool")
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

print("... retrieving bornpowerindex JSON file")
file = '{0}bornpowerindex.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    bpi_excel = "{0}bornpowerindex.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(bpi_excel, sheet_name='Sheet1')
    bpi_json = json.loads(excel_df.to_json())
else:
    print ("bornpowerindex files are missing, run the scrape_bornpowerindex tool to create")
    exit()

IDX=[]
teams=[]
abbrs=[]
classes=[]
bpi_teams=[]
bpis=[]
cons=[]
over=[]
index=0
for item in teams_json["displayName"]:
    team = str(teams_json["displayName"][item]).strip()
    abbr = str(teams_json["abbreviation"][item]).strip()
    found = False
    for bpi_item in bpi_json["abbr"]:
        bpi_abbr = str(bpi_json["abbr"][bpi_item]).strip()
        bpi_team = str(bpi_json["team"][bpi_item]).strip()
        bpi = str(bpi_json["bpi"][bpi_item]).strip()
        con = str(bpi_json["confidence"][bpi_item]).strip()
        bclass = str(bpi_json["class"][bpi_item]).strip()
        if abbr == bpi_abbr:
            found = True
            bpi_teams.append(bpi_team)
            bpis.append(bpi)
            cons.append(con)
            classes.append(bclass)
       
    teams.append(team)
    abbrs.append(abbr)
    over.append(" ")
    index+=1
    IDX.append(index)
    if not found:
        bpi_teams.append(" ")
        bpis.append(" ")
        classes.append(" ")
        cons.append(0)

for i in range(len(teams), len(bpi_teams)):
        teams.append(" ")
        abbrs.append(" ")
        over.append(" ")
        index+=1
        IDX.append(index)
   
print ("... creating merge_bornpowerindex JSON file")
the_file = "{0}merge_bornpowerindex.json".format(settings.data_path)
Path(settings.data_path).mkdir(parents=True, exist_ok=True)
df=pd.DataFrame(IDX,columns=['Index'])
df['team']=teams
df['abbr']=abbrs
df['class']=classes
df['bpi']=bpis
df['confidence']=cons
df['bpi team']=bpi_teams
df['override']=over
  
with open(the_file, 'w') as f:
    f.write(df.to_json(orient='index'))
f.close()
    
print ("... creating merge_bornpowerindex spreadsheet")
the_file = "{0}merge_bornpowerindex.xlsx".format(settings.data_path)
writer = pd.ExcelWriter(the_file, engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
