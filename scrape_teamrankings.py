#!/usr/bin/env python3

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import html5lib
import pdb
from collections import OrderedDict
import json
import csv
import contextlib
import os
import re
from pathlib import Path
from thefuzz import fuzz
from thefuzz import process

import settings
import pyBlitz

urls = []
urls.append("https://www.teamrankings.com/college-football/stat/plays-per-game")
urls.append("https://www.teamrankings.com/college-football/stat/points-per-play")
urls.append("https://www.teamrankings.com/college-football/stat/opponent-points-per-game")
urls.append("https://www.teamrankings.com/college-football/stat/opponent-points-per-play")

print ("Scrape Team Rankings Tool")
print ("**************************")
ratings_table = []
for url in urls:
    print ("data is from {0}".format(url))
    with contextlib.closing(urlopen(url)) as page:
        soup = BeautifulSoup(page, "html5lib")
    ratings_table.append(soup.find('table', {"class":"tr-table datatable scrollable"}))

print ("Directory Location: {0}".format(settings.data_path))
print ("**************************")
IDX=[]
A=[]
B=[]
C=[]
D=[]
E=[]
index=0
for row in ratings_table[0].findAll("tr"):
    col=row.findAll('td')
    if len(col)>0 and col[1].find(string=True)!="Team":
        index+=1
        IDX.append(index)
        A.append(pyBlitz.CleanString(col[1].find(string=True)))
        B.append(col[3].find(string=True))
for team in A:
    for row in ratings_table[1].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(string=True)==team:
            C.append(col[3].find(string=True))
            break
for team in A:
    for row in ratings_table[2].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(string=True)==team:
            D.append(col[3].find(string=True))
            break
for team in A:
    for row in ratings_table[3].findAll("tr"):
        col=row.findAll('td')
        if len(col)>0 and col[1].find(string=True)==team:
            E.append(col[3].find(string=True))
            break

df=pd.DataFrame(IDX,columns=['Index'])
df['Team']=A
df['PLpG3']=B
df['PTpP3']=C
df['OPLpG3']=D
df['OPTpP3']=E

print("... retrieving teams spreadsheet")
teams_excel = "{0}teams.xlsx".format(settings.data_path)
excel_df = pd.read_excel(teams_excel, sheet_name='Sheet1')
teams_json = json.loads(excel_df.to_json())

results={}
Abbrev=[]
index=-1
for item in teams_json["abbreviation"]:
    abbrev=teams_json["abbreviation"][str(item)]
    matches={}
    max_all_list=[]
    for team in A:
        match=[]
        max_list=[]
        to_match=teams_json["shortDisplayName"][str(item)]
        match_fuzz=fuzz.ratio(team, to_match)
        match.append({"shortDisplayName": match_fuzz})
        max_list.append(match_fuzz)

        to_match=teams_json["displayName"][str(item)]
        match_fuzz=fuzz.ratio(team, to_match)
        match.append({"displayName": match_fuzz})
        max_list.append(match_fuzz)
        
        to_match=teams_json["name"][str(item)]
        match_fuzz=fuzz.ratio(team, to_match)
        match.append({"name": match_fuzz})
        max_list.append(match_fuzz)

        to_match=teams_json["nickname"][str(item)]
        match_fuzz=fuzz.ratio(team, to_match)
        match.append({"nickname": match_fuzz})
        max_list.append(match_fuzz)

        to_match=teams_json["location"][str(item)]
        match_fuzz=fuzz.ratio(team, to_match)
        match.append({"location": match_fuzz})
        max_list.append(match_fuzz)
        max_val = max(max_list)
        matches[team]=max_val
        #pdb.set_trace()
    max_team=""
    max_ratio=-1
    for team in matches:
        #print (team)
        ratio=matches[team]
        #print (ratio)
        if ratio > max_ratio:
            max_team=team
            max_ratio=ratio
            #print ("max team: " + max_team)
            #print ("max ratio: " + str(max_ratio))
            #pdb.set_trace()
        #print ("max team: " + max_team)
        #print ("max ratio: " + str(max_ratio))
        #pdb.set_trace()
    #pdb.set_trace()
    #print (max_team)
    #print (max_ratio)
    results[abbrev]=max_team, max_ratio
    #pdb.set_trace()
pdb.set_trace()
  
Path(settings.data_path).mkdir(parents=True, exist_ok=True) 
with open(settings.data_path + 'teamrankings.json', 'w') as f:
    f.write(df.to_json(orient='index'))

writer = pd.ExcelWriter(settings.data_path + "teamrankings.xlsx", engine="xlsxwriter")
df.to_excel(writer, sheet_name="Sheet1", index=False)
writer.close()

print ("done.")
