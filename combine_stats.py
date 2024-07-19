#!/usr/bin/env python3

import json
import pdb
import pandas as pd
import csv
from collections import OrderedDict
import os.path
from pathlib import Path
import re

import settings
import pyBlitz

print ("Combine Stats Tool")
print ("**************************")
print (" ")
print ("This tool combines bornpowerindex and teamrankings into one stats spreadsheet")
print (" ")

print("... retrieving merge JSON file")
file = '{0}merge.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    merge_excel = "{0}merge.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(merge_excel, sheet_name='Sheet1')
    merge_json = json.loads(excel_df.to_json())
else:
    print ("        *** run combine_merge tool and then come back ***")
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

print("... retrieving teamrankings JSON file")
file = '{0}teamrankings.xlsx'.format(settings.data_path)
if (os.path.exists(file)):
    rank_excel = "{0}teamrankings.xlsx".format(settings.data_path)
    excel_df = pd.read_excel(rank_excel, sheet_name='Sheet1')
    rank_json = json.loads(excel_df.to_json())
else:
    print ("teamrankings files are missing, run the scrape_teamrankings tool to create")
    exit()

IDX=[]
T=[]
AB=[]
A=[]
B=[]
C=[]
D=[]
E=[]
F=[]
G=[]
H=[]
index = 0
for item in merge_json["team"]:
    team = str(merge_json["team"][item]).strip()
    abbr = str(merge_json["abbr"][item]).strip()
    merge_rank_team = merge_json["rankings team"][item]
    if (str(merge_rank_team).strip() == "?") or (merge_rank_team == None):
        merge_rank_team = " "
    merge_bpi_team = merge_json["bpi team"][item]
    if (str(merge_bpi_team).strip() == "?") or (merge_bpi_team == None):
        merge_bpi_team = " "
    bpi_found = False
    for bpi_item in bpi_json["team"]:
        bpi_team = str(bpi_json["team"][bpi_item]).strip()
        bpi = str(bpi_json["bpi"][bpi_item]).strip()
        bpi_class = str(bpi_json["class"][bpi_item]).strip()
        if merge_bpi_team == bpi_team:
            bpi_found = True
            C.append(bpi)
            D.append(bpi_class)
    rank_found = False
    for rank_item in rank_json["team"]:
        rank_team = str(rank_json["team"][rank_item]).strip()
        rank_PLpG3 = str(rank_json["PLpG3"][rank_item]).strip()
        rank_PTpP3 = str(rank_json["PTpP3"][rank_item]).strip()
        rank_OPLpG3 = str(rank_json["OPLpG3"][rank_item]).strip()
        rank_OPTpP3 = str(rank_json["OPTpP3"][rank_item]).strip()
        if merge_rank_team == rank_team:
            rank_found = True
            E.append(rank_PLpG3)
            F.append(rank_PTpP3)
            G.append(rank_OPLpG3)
            H.append(rank_OPTpP3)
    T.append(team)
    AB.append(abbr)
    A.append(merge_bpi_team)
    B.append(merge_rank_team)
    index+=1
    IDX.append(index)

start=len(C)
end=len(T)
for i in range(start, end):
    C.append(0)
    D.append(" ")
    
start=len(E)
end=len(T)
for i in range(start, end):
    E.append(0)
    F.append(0)
    G.append(0)
    H.append(0)

df=pd.DataFrame(IDX,columns=['Index'])
df['team']=T
df['abbr']=AB
df['BPI']=A
df['teamrankings']=B
df['Ranking']=C
df['Class']=D
df['PLpG3']=E
df['PTpP3']=F
df['OPLpG3']=G
df['OPTpP3']=H
  
print ("... creating stats JSON file")
the_file = "{0}json/stats.json".format(settings.data_path)
the_path = "{0}json/".format(settings.data_path)
Path(the_path).mkdir(parents=True, exist_ok=True)
with open(the_file, 'w') as f:
    f.write(df.to_json(orient='index'))
f.close()
    
print ("... creating stats spreadsheet")
the_file = "{0}stats.xlsx".format(settings.data_path)
writer = pd.ExcelWriter(the_file, engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
